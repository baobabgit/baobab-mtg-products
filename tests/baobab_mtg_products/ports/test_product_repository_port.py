"""Tests structurels du port :class:`~baobab_mtg_products.ports.ProductRepositoryPort`."""

from typing import Dict, Optional

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort


class _FakeRepo:
    """Adaptateur minimal."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        _barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

    def list_by_reference_id(
        self,
        reference_id: ProductReferenceId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [p for p in self.by_id.values() if p.reference_id.value == reference_id.value]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_by_production_code(
        self,
        code: ProductionCode,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [
            p
            for p in self.by_id.values()
            if p.production_code is not None and p.production_code.value == code.value
        ]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_direct_children_of_parent(
        self,
        parent_id: InternalProductId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        kids = [
            p
            for p in self.by_id.values()
            if p.parent_id is not None and p.parent_id.value == parent_id.value
        ]
        kids.sort(key=lambda p: p.internal_id.value)
        return tuple(kids)

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product


class TestProductRepositoryPort:
    """Contrat dépôt incluant la liste des enfants directs."""

    def test_adapter_lists_children_sorted(self) -> None:
        """Les enfants directs sont énumérables."""
        fake = _FakeRepo()
        adapter: ProductRepositoryPort = fake
        root = InternalProductId("r")
        fake.save(
            ProductInstance(
                internal_id=root,
                reference_id=ProductReferenceId("ref-root"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("z"),
                reference_id=ProductReferenceId("ref-z"),
                product_type=ProductType.PLAY_BOOSTER,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                parent_id=root,
            ),
        )
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("a"),
                reference_id=ProductReferenceId("ref-a"),
                product_type=ProductType.SET_BOOSTER,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                parent_id=root,
            ),
        )
        kids = adapter.list_direct_children_of_parent(root)
        assert [k.internal_id.value for k in kids] == ["a", "z"]

    def test_list_by_reference_id_returns_sorted_tuple(self) -> None:
        """Plusieurs instances partagent une référence : résultat trié par identifiant interne."""
        fake = _FakeRepo()
        adapter: ProductRepositoryPort = fake
        ref = ProductReferenceId("ref-shared")
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("b"),
                reference_id=ref,
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("a"),
                reference_id=ref,
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        out = adapter.list_by_reference_id(ref)
        assert [p.internal_id.value for p in out] == ["a", "b"]

    def test_list_by_production_code_returns_all_matches_sorted(self) -> None:
        """Code de production non unique : plusieurs lignes, jamais une sémantique d'unicité."""
        fake = _FakeRepo()
        adapter: ProductRepositoryPort = fake
        code = ProductionCode("BATCH-42")
        ref = ProductReferenceId("ref-1")
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("z"),
                reference_id=ref,
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                production_code=code,
            ),
        )
        fake.save(
            ProductInstance(
                internal_id=InternalProductId("m"),
                reference_id=ProductReferenceId("ref-2"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                production_code=code,
            ),
        )
        out = adapter.list_by_production_code(code)
        assert [p.internal_id.value for p in out] == ["m", "z"]
