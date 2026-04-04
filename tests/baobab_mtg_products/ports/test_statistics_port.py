"""Tests structurels du port :class:`~baobab_mtg_products.ports.StatisticsPort`."""

from baobab_mtg_products.domain.integration.card_revealed_statistics_event import (
    CardRevealedStatisticsEvent,
)
from baobab_mtg_products.domain.integration.opening_card_scan_statistics_event import (
    OpeningCardScanStatisticsEvent,
)
from baobab_mtg_products.domain.integration.sealed_product_opened_statistics_event import (
    SealedProductOpenedStatisticsEvent,
)
from baobab_mtg_products.ports.statistics_port import StatisticsPort


class _FakeStatisticsAdapter:
    """Adaptateur minimal compatible avec :class:`StatisticsPort`."""

    def __init__(self) -> None:
        self.opened: list[SealedProductOpenedStatisticsEvent] = []
        self.revealed: list[CardRevealedStatisticsEvent] = []
        self.scans: list[OpeningCardScanStatisticsEvent] = []

    def record_sealed_product_opened(self, event: SealedProductOpenedStatisticsEvent) -> None:
        """Stocke l'ouverture (double de test)."""
        self.opened.append(event)

    def record_card_revealed_from_opening(self, event: CardRevealedStatisticsEvent) -> None:
        """Stocke la révélation (double de test)."""
        self.revealed.append(event)

    def record_opening_card_scan(self, event: OpeningCardScanStatisticsEvent) -> None:
        """Stocke le scan (double de test)."""
        self.scans.append(event)


class TestStatisticsPort:
    """Vérifie qu'un adaptateur peut satisfaire le contrat du port."""

    def test_adapter_records_typed_events(self) -> None:
        """Les méthodes du port acceptent les DTO métier."""
        fake = _FakeStatisticsAdapter()
        adapter: StatisticsPort = fake
        o = SealedProductOpenedStatisticsEvent(
            product_id="x",
            previous_status_value="sealed",
            product_type_value="play_booster",
            set_code_value="MH3",
        )
        adapter.record_sealed_product_opened(o)
        r = CardRevealedStatisticsEvent(
            source_product_id="x",
            external_card_id="c1",
            sequence_in_opening=0,
        )
        adapter.record_card_revealed_from_opening(r)
        s = OpeningCardScanStatisticsEvent(product_id="x", scan_payload="raw")
        adapter.record_opening_card_scan(s)
        assert fake.opened == [o]
        assert fake.revealed == [r]
        assert fake.scans == [s]
