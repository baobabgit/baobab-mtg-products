"""Cas d'usage : associer ou remplacer le code de production d'une instance existante."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class AssignProductionCodeToProductInstanceUseCase(UseCase[ProductInstance]):
    """Pose ou met à jour le :class:`ProductionCode` sur une instance.

    Le code de production reste **non unique** : plusieurs instances peuvent partager
    la même valeur après cette opération.

    :param product_id: Instance à mettre à jour.
    :type product_id: InternalProductId
    :param production_code: Code de lot à associer.
    :type production_code: ProductionCode
    :param repository: Persistance des instances.
    :type repository: ProductRepositoryPort
    :param events: Journal métier (association du code).
    :type events: ProductWorkflowEventRecorderPort
    :raises ProductNotFoundForWorkflowError: si l'identifiant interne est inconnu.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        production_code: ProductionCode,
        repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
    ) -> None:
        self._product_id = product_id
        self._production_code = production_code
        self._repository = repository
        self._events = events

    def execute(self) -> ProductInstance:
        """Persiste l'instance mise à jour et journalise l'association.

        :return: Instance après modification.
        :rtype: ProductInstance
        """
        existing = self._repository.find_by_id(self._product_id)
        if existing is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit ne correspond à l'identifiant fourni pour assignation de code.",
            )
        updated = existing.derived_with(production_code=self._production_code)
        self._repository.save(updated)
        self._events.record_production_code_assigned(
            updated.internal_id.value,
            self._production_code.value,
        )
        return updated
