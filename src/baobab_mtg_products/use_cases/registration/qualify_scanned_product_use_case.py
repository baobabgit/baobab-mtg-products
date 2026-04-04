"""Cas d'usage : qualification minimale d'un produit encore « registered »."""

from typing import Optional

from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.registration.invalid_qualification_state_error import (
    InvalidQualificationStateError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.collection_port import CollectionPort
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class QualifyScannedProductUseCase(UseCase[ProductInstance]):
    """Fixe type et set métier pour un produit en attente après scan.

    :param product_id: Identifiant de l'instance à qualifier.
    :type product_id: InternalProductId
    :param product_type: Type définitif choisi par l'opérateur.
    :type product_type: ProductType
    :param set_code: Code de set définitif.
    :type set_code: MtgSetCode
    :param repository: Dépôt à mettre à jour.
    :type repository: ProductRepositoryPort
    :param events: Journal pour l'événement de qualification.
    :type events: ProductWorkflowEventRecorderPort
    :param collection: Synchronisation collection après qualification, si fourni.
    :type collection: CollectionPort | None
    :raises ProductNotFoundForWorkflowError: si l'identifiant est inconnu.
    :raises InvalidQualificationStateError: si le statut n'est pas ``registered``.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        product_type: ProductType,
        set_code: MtgSetCode,
        repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
        collection: Optional[CollectionPort] = None,
    ) -> None:
        self._product_id = product_id
        self._product_type = product_type
        self._set_code = set_code
        self._repository = repository
        self._events = events
        self._collection = collection

    def execute(self) -> ProductInstance:
        """Qualifie puis persiste l'instance mise à jour.

        :return: Produit après qualification.
        :rtype: ProductInstance
        """
        existing = self._repository.find_by_id(self._product_id)
        if existing is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit ne correspond à l'identifiant fourni pour qualification.",
            )
        if existing.status is not ProductStatus.REGISTERED:
            raise InvalidQualificationStateError(
                "Seul un produit au statut « registered » peut être qualifié via ce flux.",
            )
        updated = existing.derived_with(
            product_type=self._product_type,
            set_code=self._set_code,
            status=ProductStatus.QUALIFIED,
        )
        self._repository.save(updated)
        self._events.record_product_qualified(updated.internal_id.value)
        if self._collection is not None:
            self._collection.publish_product_provenance(
                ProductProvenanceForCollection.from_product_instance(updated),
            )
        return updated
