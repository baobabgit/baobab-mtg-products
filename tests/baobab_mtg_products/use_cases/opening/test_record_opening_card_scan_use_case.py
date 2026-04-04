"""Tests pour :class:`RecordOpeningCardScanUseCase`."""

from typing import Dict, List, Optional, Tuple

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
from baobab_mtg_products.domain.opening.opening_card_scan_payload import OpeningCardScanPayload
from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.opening.product_not_opened_for_card_trace_error import (
    ProductNotOpenedForCardTraceError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.opening.record_opening_card_scan_use_case import (
    RecordOpeningCardScanUseCase,
)


class _Repo:
    """Dépôt produit."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product


class _Events:
    """Journal des scans."""

    def __init__(self) -> None:
        self.opening_scans: List[Tuple[str, str]] = []

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
        """Non utilisé."""
        del product_id, external_card_id, sequence_in_opening

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.opening_scans.append((product_id, scan_payload))


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
        """Non utilisé."""
        self.revealed.append(event)

    def record_opening_card_scan(self, event: OpeningCardScanStatisticsEvent) -> None:
        """Voir :class:`StatisticsPort`."""
        self.scans.append(event)


class TestRecordOpeningCardScanUseCase:
    """Scans carte en contexte d'ouverture."""

    def test_records_when_opened(self) -> None:
        """Journal OK si produit ouvert."""
        repo = _Repo()
        p = ProductInstance(
            InternalProductId("p1"),
            ProductType.BUNDLE,
            MtgSetCode("TS"),
            ProductStatus.OPENED,
        )
        repo.save(p)
        events = _Events()
        RecordOpeningCardScanUseCase(
            p.internal_id,
            OpeningCardScanPayload("scan-raw-1"),
            repo,
            events,
        ).execute()
        assert events.opening_scans == [("p1", "scan-raw-1")]

    def test_statistics_port_receives_scan_event(self) -> None:
        """Le port statistiques reçoit la charge utile du scan."""
        repo = _Repo()
        p = ProductInstance(
            InternalProductId("p1"),
            ProductType.BUNDLE,
            MtgSetCode("TS"),
            ProductStatus.OPENED,
        )
        repo.save(p)
        events = _Events()
        statistics = _StatisticsStub()
        RecordOpeningCardScanUseCase(
            p.internal_id,
            OpeningCardScanPayload("payload-z"),
            repo,
            events,
            statistics=statistics,
        ).execute()
        assert len(statistics.scans) == 1
        assert statistics.scans[0].product_id == "p1"
        assert statistics.scans[0].scan_payload == "payload-z"

    def test_rejects_sealed(self) -> None:
        """Pas de scan carte si non ouvert."""
        repo = _Repo()
        p = ProductInstance(
            InternalProductId("p2"),
            ProductType.BUNDLE,
            MtgSetCode("TS"),
            ProductStatus.SEALED,
        )
        repo.save(p)
        with pytest.raises(ProductNotOpenedForCardTraceError):
            RecordOpeningCardScanUseCase(
                p.internal_id,
                OpeningCardScanPayload("x"),
                repo,
                _Events(),
            ).execute()

    def test_missing_product(self) -> None:
        """Produit inconnu."""
        with pytest.raises(ProductNotFoundForWorkflowError):
            RecordOpeningCardScanUseCase(
                InternalProductId("ghost"),
                OpeningCardScanPayload("x"),
                _Repo(),
                _Events(),
            ).execute()
