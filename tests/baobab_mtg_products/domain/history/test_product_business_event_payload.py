"""Tests pour :class:`ProductBusinessEventPayload`."""

from baobab_mtg_products.domain.history.product_business_event_payload import (
    ProductBusinessEventPayload,
)


class TestProductBusinessEventPayload:
    """DTO optionnel par défaut."""

    def test_empty_payload(self) -> None:
        """Tous les champs absents."""
        p = ProductBusinessEventPayload()
        assert p.scan_channel is None
        assert p.barcode_value is None

    def test_partial_fields(self) -> None:
        """Sous-ensemble renseigné."""
        p = ProductBusinessEventPayload(
            scan_channel="commercial",
            barcode_value="123",
        )
        assert p.scan_channel == "commercial"
        assert p.barcode_value == "123"
