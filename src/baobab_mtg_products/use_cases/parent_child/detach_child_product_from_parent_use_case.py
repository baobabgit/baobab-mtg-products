"""Cas d'usage : retirer le lien parent d'une instance rattachée."""

from typing import Optional

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.relationship.child_product_not_attached_error import (
    ChildProductNotAttachedError,
)
from baobab_mtg_products.exceptions.relationship.detach_parent_mismatch_error import (
    DetachParentMismatchError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class DetachChildProductFromParentUseCase(UseCase[None]):
    """Supprime la référence ``parent_id`` sur l'enfant (produit indépendant).

    :param child_id: Instance à détacher.
    :type child_id: InternalProductId
    :param repository: Persistance des instances.
    :type repository: ProductRepositoryPort
    :param events: Journal des détachements.
    :type events: ProductWorkflowEventRecorderPort
    :param expected_parent_id: Si fourni, doit coïncider avec le parent actuel.
    :type expected_parent_id: InternalProductId | None
    :raises ProductNotFoundForWorkflowError: si l'enfant est inconnu.
    :raises ChildProductNotAttachedError: si aucun parent n'est défini.
    :raises DetachParentMismatchError: si le parent effectif ne correspond pas.
    """

    def __init__(
        self,
        child_id: InternalProductId,
        repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
        *,
        expected_parent_id: Optional[InternalProductId] = None,
    ) -> None:
        self._child_id = child_id
        self._repository = repository
        self._events = events
        self._expected_parent_id = expected_parent_id

    def execute(self) -> None:
        """Efface ``parent_id`` et journalise l'ancien parent."""
        child = self._repository.find_by_id(self._child_id)
        if child is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit enfant ne correspond à l'identifiant fourni.",
            )
        if child.parent_id is None:
            raise ChildProductNotAttachedError(
                "Ce produit n'est rattaché à aucun parent.",
            )
        if self._expected_parent_id is not None:
            if child.parent_id.value != self._expected_parent_id.value:
                raise DetachParentMismatchError(
                    "Le parent effectif ne correspond pas à l'identifiant attendu.",
                )
        previous = child.parent_id.value
        updated = child.derived_with(parent_id=None)
        self._repository.save(updated)
        self._events.record_product_detached_from_parent(child.internal_id.value, previous)
