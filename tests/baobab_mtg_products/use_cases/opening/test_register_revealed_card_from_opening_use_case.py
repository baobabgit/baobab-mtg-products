"""Tests pour :class:`RegisterRevealedCardFromOpeningUseCase`."""

from typing import Dict, List, Optional, Set, Tuple

import pytest

from baobab_mtg_products.domain.integration.card_revealed_statistics_event import (
    CardRevealedStatisticsEvent,
)
from baobab_mtg_products.domain.integration.opening_card_scan_statistics_event import (
    OpeningCardScanStatisticsEvent,
)
from baobab_mtg_products.domain.integration.sealed_product_opened_statistics_event import (
    SealedProductOpenedStatisticsEvent,
)
from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.domain.opening.revealed_card_trace import RevealedCardTrace
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.opening.duplicate_revealed_card_trace_error import (
    DuplicateRevealedCardTraceError,
)
from baobab_mtg_products.exceptions.opening.product_not_opened_for_card_trace_error import (
    ProductNotOpenedForCardTraceError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.opening.register_revealed_card_from_opening_use_case import (
    RegisterRevealedCardFromOpeningUseCase,
)


class _Repo:
    """Dépôt produit."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product

    def list_by_reference_id(
        self,
        reference_id: ProductReferenceId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [p for p in self.by_id.values() if p.reference_id.value == reference_id.value]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_by_production_code(
        self,
        code: ProductionCode,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [
            p
            for p in self.by_id.values()
            if p.production_code is not None and p.production_code.value == code.value
        ]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_direct_children_of_parent(
        self,
        parent_id: InternalProductId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        kids = [
            p
            for p in self.by_id.values()
            if p.parent_id is not None and p.parent_id.value == parent_id.value
        ]
        kids.sort(key=lambda p: p.internal_id.value)
        return tuple(kids)


class _TraceRepo:
    """Traces en mémoire."""

    def __init__(self) -> None:
        self.traces: List[RevealedCardTrace] = []
        self._pairs: Set[Tuple[str, str]] = set()

    def count_traces_for_product(self, product_id: InternalProductId) -> int:
        """Voir :class:`RevealedCardTraceRepositoryPort`."""
        return sum(1 for t in self.traces if t.source_product_id.value == product_id.value)

    def has_trace_for_product_and_card(
        self,
        product_id: InternalProductId,
        external_card_id: ExternalCardId,
    ) -> bool:
        """Voir :class:`RevealedCardTraceRepositoryPort`."""
        return (product_id.value, external_card_id.value) in self._pairs

    def append_trace(self, trace: RevealedCardTrace) -> None:
        """Voir :class:`RevealedCardTraceRepositoryPort`."""
        self.traces.append(trace)
        self._pairs.add((trace.source_product_id.value, trace.external_card_id.value))


class _Events:
    """Journal."""

    def __init__(self) -> None:
        self.revealed: List[Tuple[str, str, int]] = []

    def record_scan(self, *args: object) -> None:
        """Non utilisé."""
        del args

    def record_registration(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_qualified(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Non utilisé."""
        del child_id, parent_id, relationship_kind

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Non utilisé."""
        del child_id, previous_parent_id

    def record_product_opened(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.revealed.append((product_id, external_card_id, sequence_in_opening))

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Non utilisé."""
        del product_id, scan_payload

    def record_product_instance_created(self, product_id: str, reference_id: str) -> None:
        """Non utilisé."""
        del product_id, reference_id

    def record_production_code_assigned(self, product_id: str, production_code: str) -> None:
        """Non utilisé."""
        del product_id, production_code


class _StatisticsStub:
    """Double statistiques."""

    def __init__(self) -> None:
        self.opened: list[SealedProductOpenedStatisticsEvent] = []
        self.revealed: list[CardRevealedStatisticsEvent] = []
        self.scans: list[OpeningCardScanStatisticsEvent] = []

    def record_sealed_product_opened(self, event: SealedProductOpenedStatisticsEvent) -> None:
        """Non utilisé."""
        self.opened.append(event)

    def record_card_revealed_from_opening(self, event: CardRevealedStatisticsEvent) -> None:
        """Voir :class:`StatisticsPort`."""
        self.revealed.append(event)

    def record_opening_card_scan(self, event: OpeningCardScanStatisticsEvent) -> None:
        """Non utilisé."""
        self.scans.append(event)


def _opened() -> ProductInstance:
    return ProductInstance(
        internal_id=InternalProductId("o1"),
        reference_id=ProductReferenceId("ref-o1"),
        product_type=ProductType.COLLECTOR_BOOSTER,
        set_code=MtgSetCode("TS"),
        status=ProductStatus.OPENED,
    )


class TestRegisterRevealedCardFromOpeningUseCase:
    """Enregistrement des cartes révélées."""

    def test_registers_sequence_and_event(self) -> None:
        """Première puis deuxième carte."""
        repo = _Repo()
        prod = _opened()
        repo.save(prod)
        traces = _TraceRepo()
        events = _Events()
        uc = RegisterRevealedCardFromOpeningUseCase
        t0 = uc(
            prod.internal_id,
            ExternalCardId("c-a"),
            repo,
            traces,
            events,
        ).execute()
        assert t0.sequence_in_opening == 0
        t1 = uc(
            prod.internal_id,
            ExternalCardId("c-b"),
            repo,
            traces,
            events,
        ).execute()
        assert t1.sequence_in_opening == 1
        assert events.revealed == [
            ("o1", "c-a", 0),
            ("o1", "c-b", 1),
        ]

    def test_statistics_port_records_reveal(self) -> None:
        """Le port statistiques reçoit le même fait que le journal."""
        repo = _Repo()
        prod = _opened()
        repo.save(prod)
        traces = _TraceRepo()
        events = _Events()
        statistics = _StatisticsStub()
        RegisterRevealedCardFromOpeningUseCase(
            prod.internal_id,
            ExternalCardId("c-stat"),
            repo,
            traces,
            events,
            statistics=statistics,
        ).execute()
        assert len(statistics.revealed) == 1
        ev = statistics.revealed[0]
        assert ev.source_product_id == "o1"
        assert ev.external_card_id == "c-stat"
        assert ev.sequence_in_opening == 0

    def test_rejects_when_not_opened(self) -> None:
        """Produit encore scellé."""
        repo = _Repo()
        sealed = ProductInstance(
            internal_id=InternalProductId("s1"),
            reference_id=ProductReferenceId("ref-s1"),
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
        )
        repo.save(sealed)
        with pytest.raises(ProductNotOpenedForCardTraceError):
            RegisterRevealedCardFromOpeningUseCase(
                sealed.internal_id,
                ExternalCardId("c"),
                repo,
                _TraceRepo(),
                _Events(),
            ).execute()

    def test_rejects_duplicate_card(self) -> None:
        """Même carte deux fois."""
        repo = _Repo()
        prod = _opened()
        repo.save(prod)
        traces = _TraceRepo()
        ev = _Events()
        uc = RegisterRevealedCardFromOpeningUseCase(
            prod.internal_id,
            ExternalCardId("dup"),
            repo,
            traces,
            ev,
        )
        uc.execute()
        with pytest.raises(DuplicateRevealedCardTraceError):
            uc.execute()

    def test_missing_product(self) -> None:
        """Produit inconnu."""
        with pytest.raises(ProductNotFoundForWorkflowError):
            RegisterRevealedCardFromOpeningUseCase(
                InternalProductId("nope"),
                ExternalCardId("c"),
                _Repo(),
                _TraceRepo(),
                _Events(),
            ).execute()
