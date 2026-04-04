"""Tests pour :class:`~baobab_mtg_products.domain.products.product_type.ProductType`."""

from baobab_mtg_products.domain.products.product_type import ProductType


class TestProductType:
    """Couverture minimale du périmètre cahier des charges."""

    def test_core_sealed_categories_exist(self) -> None:
        """Les catégories explicites du cahier des charges sont définies."""
        assert ProductType.DISPLAY.value == "display"
        assert ProductType.PLAY_BOOSTER.value == "play_booster"
        assert ProductType.COLLECTOR_BOOSTER.value == "collector_booster"
        assert ProductType.BUNDLE.value == "bundle"
        assert ProductType.PRERELEASE_KIT.value == "prerelease_kit"

    def test_string_enum_value_is_payload(self) -> None:
        """L'énumération mixin :class:`str` expose la valeur via :attr:`value`."""
        assert ProductType.SET_BOOSTER.value == "set_booster"
        assert ProductType.DRAFT_BOOSTER.value == "draft_booster"
