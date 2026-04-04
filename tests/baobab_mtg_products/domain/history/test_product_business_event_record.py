"""Tests pour :class:`ProductBusinessEventRecord`."""

from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.history.product_business_event_payload import (
    ProductBusinessEventPayload,
)
from baobab_mtg_products.domain.history.product_business_event_record import (
    ProductBusinessEventRecord,
)


class TestProductBusinessEventRecord:
    """Ligne de journal immuable."""

    def test_builds(self) -> None:
        """Construction complète."""
        rec = ProductBusinessEventRecord(
            0,
            "p1",
            ProductBusinessEventKind.SCAN,
            ProductBusinessEventPayload(scan_channel="internal"),
        )
        assert rec.global_sequence == 0
        assert rec.principal_product_id == "p1"
