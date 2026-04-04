"""Tests pour :class:`GetProductBusinessTimelineService`."""

from baobab_mtg_products.domain.history.in_memory_product_business_event_ledger import (
    InMemoryProductBusinessEventLedger,
)
from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.services.query.get_product_business_timeline_service import (
    GetProductBusinessTimelineService,
)


class TestGetProductBusinessTimelineService:
    """Alignement sur le port d'historique."""

    def test_matches_ledger_order(self) -> None:
        """Même séquence que les enregistrements du journal."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("z")
        ledger.record_product_qualified("z")
        svc = GetProductBusinessTimelineService(InternalProductId("z"), ledger)
        out = svc.load()
        assert len(out) == 2
        assert out[0].kind is ProductBusinessEventKind.REGISTRATION
        assert out[1].kind is ProductBusinessEventKind.QUALIFIED
