"""Tests pour :class:`ProductAncestorChain`."""

from typing import Dict, Optional

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.relationships.product_ancestor_chain import (
    ProductAncestorChain,
)


class _Repo:
    """Dépôt minimal."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product

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


def _node(
    pid: str,
    ptype: ProductType,
    *,
    parent: Optional[str] = None,
) -> ProductInstance:
    return ProductInstance(
        internal_id=InternalProductId(pid),
        reference_id=ProductReferenceId(f"ref-{pid}"),
        product_type=ptype,
        set_code=MtgSetCode("TS"),
        status=ProductStatus.SEALED,
        parent_id=InternalProductId(parent) if parent else None,
    )


class TestProductAncestorChain:
    """Détection de cycles et chaînes cassées."""

    def test_child_is_ancestor_detects_cycle(self) -> None:
        """B est ancêtre de A : rattacher B sous A créerait un cycle."""
        repo = _Repo()
        b = _node("b", ProductType.BUNDLE)
        a = _node("a", ProductType.PLAY_BOOSTER, parent="b")
        repo.save(b)
        repo.save(a)
        assert ProductAncestorChain.child_is_ancestor_of_parent(
            repo,
            a,
            b.internal_id,
        )

    def test_child_is_ancestor_false_when_independent(self) -> None:
        """Hiérarchie plate : pas d'ancêtre commun problématique."""
        repo = _Repo()
        p = _node("p", ProductType.DISPLAY)
        c = _node("c", ProductType.PLAY_BOOSTER)
        repo.save(p)
        repo.save(c)
        assert not ProductAncestorChain.child_is_ancestor_of_parent(
            repo,
            p,
            c.internal_id,
        )

    def test_has_broken_path_when_parent_missing(self) -> None:
        """parent_id pointe vers une instance absente."""
        repo = _Repo()
        orphan = _node("o", ProductType.PLAY_BOOSTER, parent="ghost")
        repo.save(orphan)
        assert ProductAncestorChain.has_broken_or_cyclic_ancestor_path(repo, orphan)

    def test_has_broken_path_detects_cycle(self) -> None:
        """Cycle A → B → A."""
        repo = _Repo()
        a = _node("a", ProductType.OTHER_SEALED, parent="b")
        b = _node("b", ProductType.OTHER_SEALED, parent="a")
        repo.save(a)
        repo.save(b)
        assert ProductAncestorChain.has_broken_or_cyclic_ancestor_path(repo, a)

    def test_child_is_ancestor_false_when_parent_link_missing(self) -> None:
        """Sans pré-contrôle attach : lien parent introuvable → pas de détection cycle."""
        repo = _Repo()
        leaf = _node("leaf", ProductType.PLAY_BOOSTER, parent="missing")
        repo.save(leaf)
        assert not ProductAncestorChain.child_is_ancestor_of_parent(
            repo,
            leaf,
            InternalProductId("other"),
        )

    def test_child_is_ancestor_true_when_ancestor_walk_revisits_node(self) -> None:
        """Cycle profond : la remontée revoit un nœud déjà visité."""
        repo = _Repo()
        p = _node("p", ProductType.OTHER_SEALED, parent="a")
        a = _node("a", ProductType.OTHER_SEALED, parent="b")
        b = _node("b", ProductType.OTHER_SEALED, parent="a")
        repo.save(p)
        repo.save(a)
        repo.save(b)
        assert ProductAncestorChain.child_is_ancestor_of_parent(
            repo,
            p,
            InternalProductId("z"),
        )
