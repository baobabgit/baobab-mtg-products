"""Tests pour :class:`ListProductBusinessHistoryUseCase`."""

from baobab_mtg_products.domain.history.in_memory_product_business_event_ledger import (
    InMemoryProductBusinessEventLedger,
)
from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.use_cases.history.list_product_business_history_use_case import (
    ListProductBusinessHistoryUseCase,
)


class TestListProductBusinessHistoryUseCase:
    """Délégation vers le port de lecture."""

    def test_returns_ledger_view(self) -> None:
        """Même ordre et contenu que le ledger."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("z")
        ledger.record_product_qualified("z")
        uc = ListProductBusinessHistoryUseCase(InternalProductId("z"), ledger)
        out = uc.execute()
        assert len(out) == 2
        assert out[0].kind is ProductBusinessEventKind.REGISTRATION
        assert out[1].kind is ProductBusinessEventKind.QUALIFIED
