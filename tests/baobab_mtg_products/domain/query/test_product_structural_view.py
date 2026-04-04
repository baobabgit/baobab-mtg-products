"""Tests pour :class:`ProductStructuralView`."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.query.product_structural_view import ProductStructuralView


class TestProductStructuralView:
    """DTO de vue structurelle."""

    def test_fields_immutable(self) -> None:
        """Les trois emplacements sont accessibles en lecture."""
        p = ProductInstance(
            InternalProductId("p"),
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            ProductStatus.SEALED,
        )
        view = ProductStructuralView(product=p, parent=None, direct_children=())
        assert view.product is p
        assert view.parent is None
        assert not view.direct_children
