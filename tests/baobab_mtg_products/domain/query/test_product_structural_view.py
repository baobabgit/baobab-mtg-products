"""Tests pour :class:`ProductStructuralView`."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.query.product_structural_view import ProductStructuralView


class TestProductStructuralView:
    """DTO de vue structurelle."""

    def test_fields_immutable(self) -> None:
        """Les emplacements sont accessibles en lecture."""
        ref = ProductReference(
            ProductReferenceId("ref-p"),
            name="P",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
        )
        p = ProductInstance(
            InternalProductId("p"),
            reference_id=ref.reference_id,
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
        )
        view = ProductStructuralView(
            product=p,
            product_reference=ref,
            parent=None,
            parent_reference=None,
            direct_children=(),
            child_references=(),
        )
        assert view.product is p
        assert view.product_reference is ref
        assert view.parent is None
        assert view.parent_reference is None
        assert not view.direct_children
        assert not view.child_references
