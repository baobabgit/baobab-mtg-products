"""Cas d'usage : journaliser un scan de carte lié à un produit ouvert."""

from typing import Optional

from baobab_mtg_products.domain.integration.opening_card_scan_statistics_event import (
    OpeningCardScanStatisticsEvent,
)
from baobab_mtg_products.domain.opening.opening_card_scan_payload import OpeningCardScanPayload
from baobab_mtg_products.domain.opening.opened_product_card_trace_rules import (
    OpenedProductCardTraceRules,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.statistics_port import StatisticsPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class RecordOpeningCardScanUseCase(UseCase[None]):
    """Écrit uniquement dans le journal d'événements (pas de persistance trace carte).

    :param product_id: Produit ouvert auquel rattacher le scan.
    :type product_id: InternalProductId
    :param scan_payload: Valeur validée du scan.
    :type scan_payload: OpeningCardScanPayload
    :param product_repository: Vérification du statut.
    :type product_repository: ProductRepositoryPort
    :param events: Journal métier.
    :type events: ProductWorkflowEventRecorderPort
    :param statistics: Agrégation statistique des scans carte, si fourni.
    :type statistics: StatisticsPort | None
    :raises ProductNotFoundForWorkflowError: si le produit est inconnu.
    :raises ProductNotOpenedForCardTraceError: si le produit n'est pas ouvert.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        scan_payload: OpeningCardScanPayload,
        product_repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
        statistics: Optional[StatisticsPort] = None,
    ) -> None:
        self._product_id = product_id
        self._scan_payload = scan_payload
        self._product_repository = product_repository
        self._events = events
        self._statistics = statistics

    def execute(self) -> None:
        """Journalise le scan pour audit."""
        product = self._product_repository.find_by_id(self._product_id)
        if product is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit ne correspond à l'identifiant fourni pour scan carte.",
            )
        OpenedProductCardTraceRules.assert_product_is_opened_for_card_tracing(product)
        self._events.record_opening_card_scan(
            self._product_id.value,
            self._scan_payload.value,
        )
        if self._statistics is not None:
            self._statistics.record_opening_card_scan(
                OpeningCardScanStatisticsEvent(
                    product_id=self._product_id.value,
                    scan_payload=self._scan_payload.value,
                ),
            )
