"""Tests pour :class:`SealedProductSnapshot`."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.query.sealed_product_snapshot import SealedProductSnapshot


class TestSealedProductSnapshot:
    """Couple instance / référence pour consultation."""

    def test_holds_product_and_reference(self) -> None:
        """Le snapshot expose bien les deux agrégats."""
        ref = ProductReference(
            ProductReferenceId("ref-snap"),
            name="Snap",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH1"),
            requires_qualification=False,
        )
        inst = ProductInstance(
            internal_id=InternalProductId("i1"),
            reference_id=ref.reference_id,
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH1"),
            status=ProductStatus.SEALED,
        )
        snap = SealedProductSnapshot(product=inst, reference=ref)
        assert snap.product.internal_id.value == "i1"
        assert snap.reference.name == "Snap"
