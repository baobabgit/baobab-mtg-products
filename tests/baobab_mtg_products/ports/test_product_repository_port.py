"""Tests de contrat du port :class:`ProductRepositoryPort` (instances physiques, double mémoire)."""

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from tests.support.in_memory_product_repositories import InMemoryProductRepository


class TestProductRepositoryPort:
    """Contrat dépôt instances avec :class:`InMemoryProductRepository`."""

    def test_protocol_exposes_no_commercial_barcode_lookup(self) -> None:
        """Le port instance ne propose pas de résolution par EAN (clé catalogue, pas exemplaire)."""
        public = {n for n in dir(ProductRepositoryPort) if not n.startswith("_")}
        assert "find_by_commercial_barcode" not in public

    def test_find_by_id_returns_none_when_unknown(self) -> None:
        """Identifiant interne inconnu → ``None``."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        assert adapter.find_by_id(InternalProductId("absent")) is None

    def test_find_by_internal_barcode_returns_none_when_unknown(self) -> None:
        """Code interne inconnu → ``None``."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        assert adapter.find_by_internal_barcode(InternalBarcode("INT-404")) is None

    def test_find_by_internal_barcode_roundtrip(self) -> None:
        """Une instance avec code interne est retrouvée par ce code."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        inst = ProductInstance(
            internal_id=InternalProductId("p1"),
            reference_id=ProductReferenceId("ref-1"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            internal_barcode=InternalBarcode("INT-001"),
        )
        adapter.save(inst)
        assert adapter.find_by_internal_barcode(InternalBarcode("INT-001")) is inst

    def test_find_by_internal_barcode_distinguishes_instances(self) -> None:
        """Deux instances avec codes internes distincts se résolvent séparément."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        a = ProductInstance(
            internal_id=InternalProductId("a"),
            reference_id=ProductReferenceId("ref-x"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            internal_barcode=InternalBarcode("INT-A"),
        )
        b = ProductInstance(
            internal_id=InternalProductId("b"),
            reference_id=ProductReferenceId("ref-x"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            internal_barcode=InternalBarcode("INT-B"),
        )
        adapter.save(a)
        adapter.save(b)
        assert adapter.find_by_internal_barcode(InternalBarcode("INT-A")) is a
        assert adapter.find_by_internal_barcode(InternalBarcode("INT-B")) is b

    def test_list_by_reference_id_returns_empty_tuple_when_none(self) -> None:
        """Liste vide explicite, jamais ``None``."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        assert not adapter.list_by_reference_id(ProductReferenceId("vide"))

    def test_list_by_production_code_returns_empty_tuple_when_none(self) -> None:
        """Aucun match sur le code de lot → tuple vide."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        assert not adapter.list_by_production_code(ProductionCode("LOT-inconnu"))

    def test_list_direct_children_returns_empty_tuple_when_none(self) -> None:
        """Parent sans enfants → ``()``."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        root = InternalProductId("solo")
        adapter.save(
            ProductInstance(
                internal_id=root,
                reference_id=ProductReferenceId("ref-root"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        assert not adapter.list_direct_children_of_parent(root)

    def test_repository_contract_lists_direct_children_from_parent_id(self) -> None:
        """Enfants directs uniquement ; ``parent_id`` renseigné ; ordre stable."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        root = InternalProductId("display-1")
        adapter.save(
            ProductInstance(
                internal_id=root,
                reference_id=ProductReferenceId("ref-root"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        adapter.save(
            ProductInstance(
                internal_id=InternalProductId("z-child"),
                reference_id=ProductReferenceId("ref-z"),
                product_type=ProductType.PLAY_BOOSTER,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                parent_id=root,
            ),
        )
        adapter.save(
            ProductInstance(
                internal_id=InternalProductId("a-child"),
                reference_id=ProductReferenceId("ref-a"),
                product_type=ProductType.SET_BOOSTER,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                parent_id=root,
            ),
        )
        kids = adapter.list_direct_children_of_parent(root)
        assert [k.internal_id.value for k in kids] == ["a-child", "z-child"]

    def test_list_by_reference_id_returns_sorted_tuple(self) -> None:
        """Plusieurs instances partagent une référence : résultat trié par identifiant interne."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        ref = ProductReferenceId("ref-shared")
        adapter.save(
            ProductInstance(
                internal_id=InternalProductId("b"),
                reference_id=ref,
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
            ),
        )
        adapter.save(
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
        """Code de production non unique : plusieurs lignes via ``tuple``, pas ``Optional``."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        code = ProductionCode("BATCH-42")
        adapter.save(
            ProductInstance(
                internal_id=InternalProductId("z"),
                reference_id=ProductReferenceId("ref-1"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                production_code=code,
            ),
        )
        adapter.save(
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

    def test_repository_contract_allows_multiple_instances_with_same_production_code(self) -> None:
        """Deux ``internal_id`` distincts, même ``ProductionCode`` possible ; liste des deux."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        shared = ProductionCode("LOT-2026-A")
        ref = ProductReferenceId("ref-même")
        first = ProductInstance(
            internal_id=InternalProductId("phys-1"),
            reference_id=ref,
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
            production_code=shared,
        )
        second = ProductInstance(
            internal_id=InternalProductId("phys-2"),
            reference_id=ref,
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
            production_code=shared,
        )
        adapter.save(first)
        adapter.save(second)
        found = adapter.list_by_production_code(shared)
        assert len(found) == 2
        assert {p.internal_id.value for p in found} == {"phys-1", "phys-2"}
        assert adapter.find_by_id(InternalProductId("phys-1")) is first
        assert adapter.find_by_id(InternalProductId("phys-2")) is second

    def test_repository_contract_rejects_duplicate_internal_barcode(self) -> None:
        """Le double mémoire refuse deux instances distinctes avec le même code interne."""
        adapter: ProductRepositoryPort = InMemoryProductRepository()
        shared_bc = InternalBarcode("INT-DUP")
        adapter.save(
            ProductInstance(
                internal_id=InternalProductId("keep"),
                reference_id=ProductReferenceId("r1"),
                product_type=ProductType.DISPLAY,
                set_code=MtgSetCode("TS"),
                status=ProductStatus.SEALED,
                internal_barcode=shared_bc,
            ),
        )
        clash = ProductInstance(
            internal_id=InternalProductId("other"),
            reference_id=ProductReferenceId("r2"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            internal_barcode=shared_bc,
        )
        with pytest.raises(DuplicateInternalBarcodeError):
            adapter.save(clash)
