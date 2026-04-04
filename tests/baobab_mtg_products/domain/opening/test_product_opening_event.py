"""Tests pour :class:`ProductOpeningEvent`."""

from baobab_mtg_products.domain.opening.product_opening_event import ProductOpeningEvent
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_status import ProductStatus


class TestProductOpeningEvent:
    """Value object d'audit d'ouverture."""

    def test_fields_immutable(self) -> None:
        """Construction figée."""
        evt = ProductOpeningEvent(
            InternalProductId("p1"),
            ProductStatus.SEALED,
        )
        assert evt.source_product_id.value == "p1"
        assert evt.previous_status is ProductStatus.SEALED
