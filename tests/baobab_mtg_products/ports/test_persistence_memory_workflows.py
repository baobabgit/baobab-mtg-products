"""Scénarios mémoire insert→read et consultation structurelle (feature 13)."""

from pathlib import Path

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.services.query.get_product_structural_view_service import (
    GetProductStructuralViewService,
)
from tests.support.in_memory_product_repositories import (
    InMemoryProductReferenceRepository,
    InMemoryProductRepository,
)


def test_insert_and_read_reference_and_multiple_instances_from_memory_repositories() -> None:
    """Référence puis deux instances distinctes : relire par ref, par id et par code de lot."""
    ref_repo = InMemoryProductReferenceRepository()
    prod_repo = InMemoryProductRepository()

    ref_id = ProductReferenceId("ref-booster-display")
    reference = ProductReference(
        ref_id,
        name="Display FDN",
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("FDN"),
        requires_qualification=False,
        commercial_barcode=CommercialBarcode("087207027866"),
    )
    ref_repo.save(reference)

    lot = ProductionCode("FAB-001")
    first = ProductInstance(
        internal_id=InternalProductId("disp-1"),
        reference_id=ref_id,
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("FDN"),
        status=ProductStatus.SEALED,
        production_code=lot,
    )
    second = ProductInstance(
        internal_id=InternalProductId("disp-2"),
        reference_id=ref_id,
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("FDN"),
        status=ProductStatus.SEALED,
        production_code=lot,
    )
    prod_repo.save(first)
    prod_repo.save(second)

    by_ref = prod_repo.list_by_reference_id(ref_id)
    assert len(by_ref) == 2
    assert prod_repo.find_by_id(InternalProductId("disp-1")) is first
    assert prod_repo.find_by_id(InternalProductId("disp-2")) is second
    by_lot = prod_repo.list_by_production_code(lot)
    assert len(by_lot) == 2
    assert first is not second


def test_structural_view_with_in_memory_repositories_aligns_children_and_references() -> None:
    """Parent display, enfants boosters : références alignées sur ``direct_children``."""
    ref_repo = InMemoryProductReferenceRepository()
    prod_repo = InMemoryProductRepository()

    ref_parent = ProductReference(
        ProductReferenceId("ref-parent"),
        name="Display",
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("TS"),
        requires_qualification=False,
    )
    ref_child_a = ProductReference(
        ProductReferenceId("ref-child-a"),
        name="Booster A",
        product_type=ProductType.PLAY_BOOSTER,
        set_code=MtgSetCode("TS"),
        requires_qualification=False,
    )
    ref_child_z = ProductReference(
        ProductReferenceId("ref-child-z"),
        name="Booster Z",
        product_type=ProductType.PLAY_BOOSTER,
        set_code=MtgSetCode("TS"),
        requires_qualification=False,
    )
    ref_repo.save(ref_parent)
    ref_repo.save(ref_child_a)
    ref_repo.save(ref_child_z)

    parent_id = InternalProductId("parent-display")
    prod_repo.save(
        ProductInstance(
            internal_id=parent_id,
            reference_id=ref_parent.reference_id,
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
        ),
    )
    prod_repo.save(
        ProductInstance(
            internal_id=InternalProductId("child-z"),
            reference_id=ref_child_z.reference_id,
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            parent_id=parent_id,
        ),
    )
    prod_repo.save(
        ProductInstance(
            internal_id=InternalProductId("child-a"),
            reference_id=ref_child_a.reference_id,
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.SEALED,
            parent_id=parent_id,
        ),
    )

    view = GetProductStructuralViewService(parent_id, prod_repo, ref_repo).load()
    assert view.product.internal_id == parent_id
    assert view.product_reference.reference_id == ref_parent.reference_id
    assert view.parent is None
    ids_children = [c.internal_id.value for c in view.direct_children]
    assert ids_children == ["child-a", "child-z"]
    assert [r.reference_id.value for r in view.child_references] == ["ref-child-a", "ref-child-z"]


def test_project_has_no_runtime_database_dependency() -> None:
    """Le projet ne déclare pas de driver SQL / ORM dans les dépendances runtime."""
    root = Path(__file__).resolve().parents[3]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "\ndependencies = []\n" in text
    opt = "[project.optional-dependencies]"
    end = text.find(opt)
    block = text[:end] if end != -1 else text
    lowered = block.lower()
    for forbidden in (
        "sqlalchemy",
        "psycopg",
        "psycopg2",
        "asyncpg",
        "aiosqlite",
        "sqlite-utils",
        "pymongo",
    ):
        assert forbidden not in lowered
