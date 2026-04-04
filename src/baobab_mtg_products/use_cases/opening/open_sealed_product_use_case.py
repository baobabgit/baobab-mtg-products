"""Cas d'usage : ouvrir une instance scellé éligible (une seule transition vers opened)."""

from baobab_mtg_products.domain.opening.open_sealed_product_outcome import OpenSealedProductOutcome
from baobab_mtg_products.domain.opening.product_opening_event import ProductOpeningEvent
from baobab_mtg_products.domain.opening.sealed_product_opening_rules import (
    SealedProductOpeningRules,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class OpenSealedProductUseCase(UseCase[OpenSealedProductOutcome]):
    """Passe le statut à ``opened`` si le type et l'état le permettent.

    :param product_id: Instance à ouvrir.
    :type product_id: InternalProductId
    :param repository: Persistance du produit.
    :type repository: ProductRepositoryPort
    :param events: Journal métier (événement d'ouverture).
    :type events: ProductWorkflowEventRecorderPort
    :raises ProductNotFoundForWorkflowError: si l'identifiant est inconnu.
    :raises ProductAlreadyOpenedError: si déjà ouvert.
    :raises ProductNotReadyForOpeningError: si le statut est inadapté.
    :raises ProductNotOpenableError: si le type est non ouvrable.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
    ) -> None:
        self._product_id = product_id
        self._repository = repository
        self._events = events

    def execute(self) -> OpenSealedProductOutcome:
        """Met à jour le dépôt et journalise l'ouverture."""
        existing = self._repository.find_by_id(self._product_id)
        if existing is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit ne correspond à l'identifiant fourni pour ouverture.",
            )
        SealedProductOpeningRules.assert_product_may_be_opened(existing)
        previous = existing.status
        updated = existing.derived_with(status=ProductStatus.OPENED)
        self._repository.save(updated)
        self._events.record_product_opened(updated.internal_id.value)
        event = ProductOpeningEvent(
            source_product_id=updated.internal_id,
            previous_status=previous,
        )
        return OpenSealedProductOutcome(updated_product=updated, opening_event=event)
