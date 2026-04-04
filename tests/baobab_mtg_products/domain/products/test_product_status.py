"""Tests pour :class:`~baobab_mtg_products.domain.products.product_status.ProductStatus`."""

from baobab_mtg_products.domain.products.product_status import ProductStatus


class TestProductStatus:
    """Statuts métier du cycle de vie de référence."""

    def test_lifecycle_values(self) -> None:
        """Les statuts attendus pour une instance sont présents."""
        assert ProductStatus.REGISTERED.value == "registered"
        assert ProductStatus.QUALIFIED.value == "qualified"
        assert ProductStatus.SEALED.value == "sealed"
        assert ProductStatus.OPENED.value == "opened"

    def test_enum_value_is_stable_string(self) -> None:
        """La charge utile sérialisable est la valeur de l'énumération."""
        assert ProductStatus.SEALED.value == "sealed"
