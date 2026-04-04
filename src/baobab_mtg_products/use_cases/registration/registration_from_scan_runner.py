"""Orchestration partagée des enregistrements déclenchés par scan."""

from typing import Optional, cast

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
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
from baobab_mtg_products.ports.internal_product_id_factory_port import (
    InternalProductIdFactoryPort,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
    ScanChannel,
)


class RegistrationFromScanRunner:
    """Applique le scénario scan → résolution → persistance → événements.

    :param repository: Dépôt des instances produit.
    :type repository: ProductRepositoryPort
    :param resolution: Résolution catalogue pour les codes scannés.
    :type resolution: BarcodeResolutionPort
    :param product_ids: Fabrique d'identifiants pour les nouvelles instances.
    :type product_ids: InternalProductIdFactoryPort
    :param events: Journal métier (scan, enregistrement).
    :type events: ProductWorkflowEventRecorderPort
    """

    def __init__(
        self,
        repository: ProductRepositoryPort,
        resolution: BarcodeResolutionPort,
        product_ids: InternalProductIdFactoryPort,
        events: ProductWorkflowEventRecorderPort,
    ) -> None:
        self._repository = repository
        self._resolution = resolution
        self._product_ids = product_ids
        self._events = events

    def register_via_commercial(
        self,
        barcode: CommercialBarcode,
        *,
        serial_number: Optional[SerialNumber] = None,
        set_code_override: Optional[MtgSetCode] = None,
        product_type_override: Optional[ProductType] = None,
    ) -> RegistrationScanResult:
        """Enregistre ou retrouve un produit à partir d'un scan commercial.

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
        existing = self._repository.find_by_commercial_barcode(barcode)
        if existing is not None:
            self._events.record_scan(
                existing.internal_id.value,
                "commercial",
                barcode.value,
            )
            return RegistrationScanResult(
                existing,
                RegistrationScanOutcome.EXISTING_PRODUCT,
            )
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

        new_id = self._product_ids.new_product_id()
        product = ProductInstance(
            internal_id=new_id,
            product_type=cast(ProductType, final_type),
            set_code=cast(MtgSetCode, final_set),
            status=status,
            serial_number=serial_number,
            commercial_barcode=commercial_barcode,
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
        outcome = (
            RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
            if needs_qualification
            else RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG
        )
        return RegistrationScanResult(product, outcome)
