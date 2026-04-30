"""Orchestration partagée des enregistrements déclenchés par scan."""

from typing import Optional, cast

from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.domain.registration.registration_defaults import RegistrationDefaults
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan
from baobab_mtg_products.ports.barcode_resolution_port import BarcodeResolutionPort
from baobab_mtg_products.ports.collection_port import CollectionPort
from baobab_mtg_products.ports.internal_product_id_factory_port import (
    InternalProductIdFactoryPort,
)
from baobab_mtg_products.ports.product_reference_id_factory_port import (
    ProductReferenceIdFactoryPort,
)
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
    ScanChannel,
)


class RegistrationFromScanRunner:
    """Applique le scénario scan → résolution → persistance → événements.

    :param repository: Dépôt des instances produit physiques.
    :type repository: ProductRepositoryPort
    :param reference_repository: Dépôt des références catalogue partagées.
    :type reference_repository: ProductReferenceRepositoryPort
    :param resolution: Résolution catalogue pour les codes scannés.
    :type resolution: BarcodeResolutionPort
    :param product_ids: Fabrique d'identifiants pour les nouvelles instances.
    :type product_ids: InternalProductIdFactoryPort
    :param reference_ids: Fabrique d'identifiants pour les nouvelles références.
    :type reference_ids: ProductReferenceIdFactoryPort
    :param events: Journal métier (scan, enregistrement).
    :type events: ProductWorkflowEventRecorderPort
    :param collection: Synchronisation collection (instantanés provenance), si fourni.
    :type collection: CollectionPort | None
    """

    def __init__(
        self,
        repository: ProductRepositoryPort,
        reference_repository: ProductReferenceRepositoryPort,
        resolution: BarcodeResolutionPort,
        product_ids: InternalProductIdFactoryPort,
        reference_ids: ProductReferenceIdFactoryPort,
        events: ProductWorkflowEventRecorderPort,
        collection: Optional[CollectionPort] = None,
    ) -> None:
        self._repository = repository
        self._reference_repository = reference_repository
        self._resolution = resolution
        self._product_ids = product_ids
        self._reference_ids = reference_ids
        self._events = events
        self._collection = collection

    def register_via_commercial(
        self,
        barcode: CommercialBarcode,
        *,
        serial_number: Optional[SerialNumber] = None,
        set_code_override: Optional[MtgSetCode] = None,
        product_type_override: Optional[ProductType] = None,
    ) -> RegistrationScanResult:
        """Enregistre un nouvel exemplaire ou retrouve une instance par scan interne équivalent.

        Un même code-barres commercial peut désigner une :class:`ProductReference`
        déjà persistée : une nouvelle :class:`ProductInstance` est alors créée sans
        fusion ni blocage. Les overrides type/set ne s'appliquent pas dans ce cas :
        la vérité descriptive reste celle de la référence existante.

        :param barcode: Code-barres commercial scanné.
        :type barcode: CommercialBarcode
        :param serial_number: Série fabricant si disponible au moment du scan.
        :type serial_number: SerialNumber | None
        :param set_code_override: Set imposé par l'opérateur si le catalogue est muet.
        :type set_code_override: MtgSetCode | None
        :param product_type_override: Type imposé par l'opérateur si besoin.
        :type product_type_override: ProductType | None
        :return: Instance persistée et issue métier du flux.
        :rtype: RegistrationScanResult
        """
        shared_ref = self._reference_repository.find_by_commercial_barcode(barcode)
        if shared_ref is not None:
            product = self._new_instance_for_existing_reference(
                shared_ref,
                serial_number=serial_number,
            )
            self._repository.save(product)
            self._events.record_registration(product.internal_id.value)
            self._events.record_scan(
                product.internal_id.value,
                "commercial",
                barcode.value,
            )
            self._maybe_publish_provenance(product)
            outcome = (
                RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
                if shared_ref.requires_qualification
                else RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
            )
            return RegistrationScanResult(product, outcome)

        resolved = self._resolution.resolve_commercial(barcode)
        return self._materialize_new_scan(
            resolved=resolved,
            commercial_barcode=barcode,
            internal_barcode=None,
            serial_number=serial_number,
            set_code_override=set_code_override,
            product_type_override=product_type_override,
        )

    def register_via_internal(
        self,
        barcode: InternalBarcode,
        *,
        serial_number: Optional[SerialNumber] = None,
        set_code_override: Optional[MtgSetCode] = None,
        product_type_override: Optional[ProductType] = None,
    ) -> RegistrationScanResult:
        """Enregistre ou retrouve un produit à partir d'un scan interne.

        :param barcode: Code-barres interne scanné.
        :type barcode: InternalBarcode
        :param serial_number: Série fabricant si disponible au moment du scan.
        :type serial_number: SerialNumber | None
        :param set_code_override: Set imposé par l'opérateur si le catalogue est muet.
        :type set_code_override: MtgSetCode | None
        :param product_type_override: Type imposé par l'opérateur si besoin.
        :type product_type_override: ProductType | None
        :return: Instance persistée et issue métier du flux.
        :rtype: RegistrationScanResult
        """
        existing = self._repository.find_by_internal_barcode(barcode)
        if existing is not None:
            self._events.record_scan(
                existing.internal_id.value,
                "internal",
                barcode.value,
            )
            self._maybe_publish_provenance(existing)
            return RegistrationScanResult(
                existing,
                RegistrationScanOutcome.EXISTING_PRODUCT,
            )
        resolved = self._resolution.resolve_internal(barcode)
        return self._materialize_new_scan(
            resolved=resolved,
            commercial_barcode=None,
            internal_barcode=barcode,
            serial_number=serial_number,
            set_code_override=set_code_override,
            product_type_override=product_type_override,
        )

    def _reference_display_name(
        self,
        resolved: ResolvedFromScan,
        *,
        commercial_barcode: Optional[CommercialBarcode],
        internal_barcode: Optional[InternalBarcode],
    ) -> str:
        if resolved.display_name is not None:
            stripped = resolved.display_name.strip()
            if stripped:
                return stripped
        if commercial_barcode is not None:
            return f"Produit commercial {commercial_barcode.value}"
        if internal_barcode is not None:
            return f"Produit interne {internal_barcode.value}"
        return "Référence produit"

    def _new_instance_for_existing_reference(
        self,
        reference: ProductReference,
        *,
        serial_number: Optional[SerialNumber],
    ) -> ProductInstance:
        new_id = self._product_ids.new_product_id()
        status = (
            ProductStatus.REGISTERED
            if reference.requires_qualification
            else ProductStatus.QUALIFIED
        )
        return ProductInstance(
            internal_id=new_id,
            reference_id=reference.reference_id,
            product_type=reference.product_type,
            set_code=reference.set_code,
            status=status,
            serial_number=serial_number,
            internal_barcode=None,
        )

    def _materialize_new_scan(  # pylint: disable=too-many-locals
        self,
        *,
        resolved: ResolvedFromScan,
        commercial_barcode: Optional[CommercialBarcode],
        internal_barcode: Optional[InternalBarcode],
        serial_number: Optional[SerialNumber],
        set_code_override: Optional[MtgSetCode],
        product_type_override: Optional[ProductType],
    ) -> RegistrationScanResult:
        merged_type = (
            product_type_override if product_type_override is not None else resolved.product_type
        )
        merged_set = set_code_override if set_code_override is not None else resolved.set_code

        used_default_type = merged_type is None
        used_default_set = merged_set is None

        final_type = (
            RegistrationDefaults.unknown_product_type() if used_default_type else merged_type
        )
        final_set = RegistrationDefaults.placeholder_set_code() if used_default_set else merged_set

        needs_qualification = used_default_type or used_default_set
        status = ProductStatus.REGISTERED if needs_qualification else ProductStatus.QUALIFIED

        ref_name = self._reference_display_name(
            resolved,
            commercial_barcode=commercial_barcode,
            internal_barcode=internal_barcode,
        )
        ref_id = self._reference_ids.new_reference_id()
        reference = ProductReference(
            reference_id=ref_id,
            name=ref_name,
            product_type=cast(ProductType, final_type),
            set_code=cast(MtgSetCode, final_set),
            requires_qualification=needs_qualification,
            commercial_barcode=commercial_barcode,
            image_uri=resolved.image_uri,
        )
        self._reference_repository.save(reference)

        new_id = self._product_ids.new_product_id()
        product = ProductInstance(
            internal_id=new_id,
            reference_id=ref_id,
            product_type=cast(ProductType, final_type),
            set_code=cast(MtgSetCode, final_set),
            status=status,
            serial_number=serial_number,
            internal_barcode=internal_barcode,
        )
        self._repository.save(product)
        self._events.record_registration(new_id.value)
        scan_kind: ScanChannel = "commercial" if commercial_barcode is not None else "internal"
        raw = (
            commercial_barcode.value
            if commercial_barcode is not None
            else (internal_barcode.value if internal_barcode is not None else "")
        )
        self._events.record_scan(new_id.value, scan_kind, raw)
        self._maybe_publish_provenance(product)
        outcome = (
            RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
            if needs_qualification
            else RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG
        )
        return RegistrationScanResult(product, outcome)

    def _maybe_publish_provenance(self, instance: ProductInstance) -> None:
        if self._collection is None:
            return
        self._collection.publish_product_provenance(
            ProductProvenanceForCollection.from_product_instance(instance),
        )
