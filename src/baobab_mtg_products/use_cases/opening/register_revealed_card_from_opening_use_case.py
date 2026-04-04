"""Cas d'usage : rattacher une carte révélée à un produit déjà ouvert."""

from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.domain.opening.opened_product_card_trace_rules import (
    OpenedProductCardTraceRules,
)
from baobab_mtg_products.domain.opening.revealed_card_trace import RevealedCardTrace
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.opening.duplicate_revealed_card_trace_error import (
    DuplicateRevealedCardTraceError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.ports.revealed_card_trace_repository_port import (
    RevealedCardTraceRepositoryPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class RegisterRevealedCardFromOpeningUseCase(UseCase[RevealedCardTrace]):
    """Persiste une trace de provenance produit ouvert → carte externe.

    :param product_id: Source (doit être ``opened``).
    :type product_id: InternalProductId
    :param external_card_id: Identifiant carte côté intégration.
    :type external_card_id: ExternalCardId
    :param product_repository: Lecture du statut produit.
    :type product_repository: ProductRepositoryPort
    :param trace_repository: Persistance des traces.
    :type trace_repository: RevealedCardTraceRepositoryPort
    :param events: Journal des révélations.
    :type events: ProductWorkflowEventRecorderPort
    :raises ProductNotFoundForWorkflowError: si le produit est inconnu.
    :raises ProductNotOpenedForCardTraceError: si le produit n'est pas ouvert.
    :raises DuplicateRevealedCardTraceError: si la paire produit + carte existe déjà.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        external_card_id: ExternalCardId,
        product_repository: ProductRepositoryPort,
        trace_repository: RevealedCardTraceRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
    ) -> None:
        self._product_id = product_id
        self._external_card_id = external_card_id
        self._product_repository = product_repository
        self._trace_repository = trace_repository
        self._events = events

    def execute(self) -> RevealedCardTrace:
        """Calcule la séquence, persiste et émet l'événement."""
        product = self._product_repository.find_by_id(self._product_id)
        if product is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit ne correspond à l'identifiant fourni pour trace carte.",
            )
        OpenedProductCardTraceRules.assert_product_is_opened_for_card_tracing(product)
        if self._trace_repository.has_trace_for_product_and_card(
            self._product_id,
            self._external_card_id,
        ):
            raise DuplicateRevealedCardTraceError(
                "Cette carte est déjà enregistrée pour ce produit ouvert.",
            )
        seq = self._trace_repository.count_traces_for_product(self._product_id)
        trace = RevealedCardTrace(
            source_product_id=self._product_id,
            external_card_id=self._external_card_id,
            sequence_in_opening=seq,
        )
        self._trace_repository.append_trace(trace)
        self._events.record_card_revealed_from_opening(
            self._product_id.value,
            self._external_card_id.value,
            seq,
        )
        return trace
