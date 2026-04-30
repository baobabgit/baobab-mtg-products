"""Tests pour :class:`GetProductStructuralViewService`."""

from typing import Dict, Optional

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.query.missing_referenced_parent_product_error import (
    MissingReferencedParentProductError,
)
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.exceptions.query.product_reference_not_found_for_query_error import (
    ProductReferenceNotFoundForQueryError,
)
from baobab_mtg_products.services.query.get_product_structural_view_service import (
    GetProductStructuralViewService,
)


class _Repo:
    """Dépôt instance minimal."""

    def __init__(self) -> None:
        self.by_id: dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> ProductInstance | None:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        _barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

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


class _RefRepo:
    """Dépôt références minimal."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> ProductReference | None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_id.get(reference_id.value)

    def find_by_commercial_barcode(self, barcode: object) -> ProductReference | None:
        """Non utilisé."""
        del barcode

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference


def _ref_for(pid: str, ptype: ProductType) -> ProductReference:
    return ProductReference(
        ProductReferenceId(f"ref-{pid}"),
        name=f"nom-{pid}",
        product_type=ptype,
        set_code=MtgSetCode("TS"),
        requires_qualification=False,
    )


def _node(
    pid: str,
    ptype: ProductType,
    ref: ProductReference,
    *,
    parent: str | None = None,
) -> ProductInstance:
    return ProductInstance(
        internal_id=InternalProductId(pid),
        reference_id=ref.reference_id,
        product_type=ptype,
        set_code=MtgSetCode("TS"),
        status=ProductStatus.SEALED,
        parent_id=InternalProductId(parent) if parent else None,
    )


class TestGetProductStructuralViewService:
    """Vues structurelles cohérentes."""

    def test_standalone_product(self) -> None:
        """Sans parent ni enfants."""
        repo = _Repo()
        ref_repo = _RefRepo()
        r = _ref_for("s", ProductType.SET_BOOSTER)
        ref_repo.save(r)
        solo = _node("s", ProductType.SET_BOOSTER, r)
        repo.save(solo)
        view = GetProductStructuralViewService(solo.internal_id, repo, ref_repo).load()
        assert view.product is solo
        assert view.product_reference is r
        assert view.parent is None
        assert view.parent_reference is None
        assert not view.direct_children
        assert not view.child_references

    def test_child_resolves_parent(self) -> None:
        """Enfant avec parent chargé."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_r = _ref_for("r", ProductType.DISPLAY)
        ref_c = _ref_for("c", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_r)
        ref_repo.save(ref_c)
        root = _node("r", ProductType.DISPLAY, ref_r)
        child = _node("c", ProductType.PLAY_BOOSTER, ref_c, parent="r")
        repo.save(root)
        repo.save(child)
        view = GetProductStructuralViewService(child.internal_id, repo, ref_repo).load()
        assert view.parent is root
        assert view.parent_reference is ref_r
        assert view.product_reference is ref_c
        assert not view.direct_children

    def test_parent_lists_sorted_children(self) -> None:
        """Enfants directs triés par identifiant."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_r = _ref_for("r", ProductType.DISPLAY)
        ref_b = _ref_for("b", ProductType.PLAY_BOOSTER)
        ref_a = _ref_for("a", ProductType.SET_BOOSTER)
        for rf in (ref_r, ref_b, ref_a):
            ref_repo.save(rf)
        root = _node("r", ProductType.DISPLAY, ref_r)
        b = _node("b", ProductType.PLAY_BOOSTER, ref_b, parent="r")
        a = _node("a", ProductType.SET_BOOSTER, ref_a, parent="r")
        repo.save(root)
        repo.save(b)
        repo.save(a)
        view = GetProductStructuralViewService(root.internal_id, repo, ref_repo).load()
        assert view.parent is None
        assert view.direct_children == (a, b)
        assert view.child_references == (ref_a, ref_b)

    def test_unknown_product(self) -> None:
        """Produit absent."""
        with pytest.raises(ProductNotFoundForQueryError):
            GetProductStructuralViewService(
                InternalProductId("x"),
                _Repo(),
                _RefRepo(),
            ).load()

    def test_orphan_parent_reference(self) -> None:
        """parent_id sans ligne parent."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_c = _ref_for("c", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_c)
        bad = _node("c", ProductType.PLAY_BOOSTER, ref_c, parent="missing")
        repo.save(bad)
        with pytest.raises(MissingReferencedParentProductError):
            GetProductStructuralViewService(bad.internal_id, repo, ref_repo).load()

    def test_missing_reference_raises(self) -> None:
        """Référence absente pour le produit central."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_missing = _ref_for("z", ProductType.BUNDLE)
        inst = _node("z", ProductType.BUNDLE, ref_missing)
        repo.save(inst)
        with pytest.raises(ProductReferenceNotFoundForQueryError):
            GetProductStructuralViewService(inst.internal_id, repo, ref_repo).load()
