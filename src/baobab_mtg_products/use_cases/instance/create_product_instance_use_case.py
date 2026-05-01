"""Cas d'usage : création explicite d'une instance physique à partir d'une référence catalogue."""

from typing import Optional

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.exceptions.registration.missing_product_ref_workflow_error import (
    ProductReferenceNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.internal_product_id_factory_port import (
    InternalProductIdFactoryPort,
)
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class CreateProductInstanceUseCase(UseCase[ProductInstance]):
    """Crée une nouvelle instance physique liée à une :class:`ProductReference` existante.

    Le code de production est **optionnel** et **non unique**. Le code-barres interne,
    s'il est fourni, doit être **unique** parmi les instances persistées.

    :param reference_id: Référence catalogue cible.
    :type reference_id: ProductReferenceId
    :param repository: Persistance des instances.
    :type repository: ProductRepositoryPort
    :param reference_repository: Lecture des références catalogue.
    :type reference_repository: ProductReferenceRepositoryPort
    :param product_ids: Fabrique d'identifiants internes pour la nouvelle instance.
    :type product_ids: InternalProductIdFactoryPort
    :param events: Journal métier (création d'instance).
    :type events: ProductWorkflowEventRecorderPort
    :param production_code: Code de lot / production optionnel (non unique).
    :type production_code: ProductionCode | None
    :param internal_barcode: Code-barres interne optionnel (unique s'il existe).
    :type internal_barcode: InternalBarcode | None
    :param serial_number: Numéro de série fabricant optionnel (distinct du code de production).
    :type serial_number: SerialNumber | None
    :raises ProductReferenceNotFoundForWorkflowError: si la référence est absente.
    :raises DuplicateInternalBarcodeError: si le code interne est déjà utilisé.
    """

    def __init__(
        self,
        reference_id: ProductReferenceId,
        repository: ProductRepositoryPort,
        reference_repository: ProductReferenceRepositoryPort,
        product_ids: InternalProductIdFactoryPort,
        events: ProductWorkflowEventRecorderPort,
        *,
        production_code: Optional[ProductionCode] = None,
        internal_barcode: Optional[InternalBarcode] = None,
        serial_number: Optional[SerialNumber] = None,
    ) -> None:
        self._reference_id = reference_id
        self._repository = repository
        self._reference_repository = reference_repository
        self._product_ids = product_ids
        self._events = events
        self._production_code = production_code
        self._internal_barcode = internal_barcode
        self._serial_number = serial_number

    def execute(self) -> ProductInstance:
        """Matérialise, persiste et journalise la nouvelle instance.

        :return: Instance telle que stockée.
        :rtype: ProductInstance
        """
        reference = self._reference_repository.find_by_id(self._reference_id)
        if reference is None:
            raise ProductReferenceNotFoundForWorkflowError(
                "Aucune référence catalogue ne correspond à l'identifiant fourni pour création.",
            )
        if self._internal_barcode is not None:
            taken = self._repository.find_by_internal_barcode(self._internal_barcode)
            if taken is not None:
                raise DuplicateInternalBarcodeError(
                    "Ce code-barres interne est déjà attribué à une autre instance.",
                )
        status = (
            ProductStatus.REGISTERED
            if reference.requires_qualification
            else ProductStatus.QUALIFIED
        )
        new_id = self._product_ids.new_product_id()
        instance = ProductInstance(
            internal_id=new_id,
            reference_id=reference.reference_id,
            product_type=reference.product_type,
            set_code=reference.set_code,
            status=status,
            serial_number=self._serial_number,
            production_code=self._production_code,
            internal_barcode=self._internal_barcode,
        )
        self._repository.save(instance)
        self._events.record_product_instance_created(
            new_id.value,
            reference.reference_id.value,
        )
        return instance
