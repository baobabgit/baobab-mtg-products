"""Tests pour :class:`ProductBusinessEventKind`."""

from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)


class TestProductBusinessEventKind:
    """Valeurs sérialisables stables."""

    def test_string_values(self) -> None:
        """Chaînes attendues pour persistance ou API."""
        assert ProductBusinessEventKind.SCAN.value == "scan"
        assert ProductBusinessEventKind.REGISTRATION.value == "registration"
        assert ProductBusinessEventKind.OPENED.value == "opened"
