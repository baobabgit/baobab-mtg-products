"""Tests pour :class:`GetProductStructuralViewService`."""

from typing import Optional

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.query.missing_referenced_parent_product_error import (
    MissingReferencedParentProductError,
)
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.services.query.get_product_structural_view_service import (
    GetProductStructuralViewService,
)


class _Repo:
    """Dépôt minimal."""

    def __init__(self) -> None:
        self.by_id: dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> ProductInstance | None:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        _barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

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


def _node(
    pid: str,
    ptype: ProductType,
    *,
    parent: str | None = None,
) -> ProductInstance:
    return ProductInstance(
        InternalProductId(pid),
        ptype,
        MtgSetCode("TS"),
        ProductStatus.SEALED,
        parent_id=InternalProductId(parent) if parent else None,
    )


class TestGetProductStructuralViewService:
    """Vues structurelles cohérentes."""

    def test_standalone_product(self) -> None:
        """Sans parent ni enfants."""
        repo = _Repo()
        solo = _node("s", ProductType.SET_BOOSTER)
        repo.save(solo)
        view = GetProductStructuralViewService(solo.internal_id, repo).load()
        assert view.product is solo
        assert view.parent is None
        assert not view.direct_children

    def test_child_resolves_parent(self) -> None:
        """Enfant avec parent chargé."""
        repo = _Repo()
        root = _node("r", ProductType.DISPLAY)
        child = _node("c", ProductType.PLAY_BOOSTER, parent="r")
        repo.save(root)
        repo.save(child)
        view = GetProductStructuralViewService(child.internal_id, repo).load()
        assert view.parent is root
        assert not view.direct_children

    def test_parent_lists_sorted_children(self) -> None:
        """Enfants directs triés par identifiant."""
        repo = _Repo()
        root = _node("r", ProductType.DISPLAY)
        b = _node("b", ProductType.PLAY_BOOSTER, parent="r")
        a = _node("a", ProductType.SET_BOOSTER, parent="r")
        repo.save(root)
        repo.save(b)
        repo.save(a)
        view = GetProductStructuralViewService(root.internal_id, repo).load()
        assert view.parent is None
        assert view.direct_children == (a, b)

    def test_unknown_product(self) -> None:
        """Produit absent."""
        with pytest.raises(ProductNotFoundForQueryError):
            GetProductStructuralViewService(InternalProductId("x"), _Repo()).load()

    def test_orphan_parent_reference(self) -> None:
        """parent_id sans ligne parent."""
        repo = _Repo()
        bad = _node("c", ProductType.PLAY_BOOSTER, parent="missing")
        repo.save(bad)
        with pytest.raises(MissingReferencedParentProductError):
            GetProductStructuralViewService(bad.internal_id, repo).load()
