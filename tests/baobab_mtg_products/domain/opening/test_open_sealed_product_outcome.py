"""Tests pour :class:`OpenSealedProductOutcome`."""

from baobab_mtg_products.domain.opening.open_sealed_product_outcome import OpenSealedProductOutcome
from baobab_mtg_products.domain.opening.product_opening_event import ProductOpeningEvent
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType


class TestOpenSealedProductOutcome:
    """Résultat structuré du cas d'usage d'ouverture."""

    def test_bundles_product_and_event(self) -> None:
        """Les deux facettes sont accessibles."""
        opened = ProductInstance(
            InternalProductId("x"),
            ProductType.PLAY_BOOSTER,
            MtgSetCode("TS"),
            ProductStatus.OPENED,
        )
        evt = ProductOpeningEvent(InternalProductId("x"), ProductStatus.SEALED)
        out = OpenSealedProductOutcome(updated_product=opened, opening_event=evt)
        assert out.updated_product.status is ProductStatus.OPENED
        assert out.opening_event.previous_status is ProductStatus.SEALED
