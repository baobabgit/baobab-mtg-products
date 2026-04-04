"""Tests pour :class:`DetachChildProductFromParentUseCase`."""

from typing import Dict, List, Optional, Tuple

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.relationship.child_product_not_attached_error import (
    ChildProductNotAttachedError,
)
from baobab_mtg_products.exceptions.relationship.detach_parent_mismatch_error import (
    DetachParentMismatchError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.parent_child.detach_child_product_from_parent_use_case import (
    DetachChildProductFromParentUseCase,
)


class _Repo:
    """Dépôt en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product


class _Events:
    """Capture détachements."""

    def __init__(self) -> None:
        self.detached: List[Tuple[str, str]] = []

    def record_scan(self, *args: object) -> None:
        """Non utilisé."""
        del args

    def record_registration(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_qualified(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Non utilisé."""
        del child_id, parent_id, relationship_kind

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.detached.append((child_id, previous_parent_id))


def _node(
    pid: str,
    ptype: ProductType,
    *,
    parent: Optional[str] = None,
) -> ProductInstance:
    return ProductInstance(
        InternalProductId(pid),
        ptype,
        MtgSetCode("TS"),
        ProductStatus.SEALED,
        parent_id=InternalProductId(parent) if parent else None,
    )


class TestDetachChildProductFromParentUseCase:
    """Détachement et garde-fous."""

    def test_detach_clears_parent_and_records_event(self) -> None:
        """Fin du lien parent → enfant."""
        repo = _Repo()
        root = _node("r", ProductType.DISPLAY)
        child = _node("c", ProductType.PLAY_BOOSTER, parent="r")
        repo.save(root)
        repo.save(child)
        events = _Events()
        DetachChildProductFromParentUseCase(child.internal_id, repo, events).execute()
        updated = repo.find_by_id(child.internal_id)
        assert updated is not None
        assert updated.parent_id is None
        assert events.detached == [("c", "r")]

    def test_rejects_unknown_child(self) -> None:
        """Instance inconnue."""
        with pytest.raises(ProductNotFoundForWorkflowError):
            DetachChildProductFromParentUseCase(
                InternalProductId("nope"),
                _Repo(),
                _Events(),
            ).execute()

    def test_rejects_when_not_attached(self) -> None:
        """Produit indépendant."""
        repo = _Repo()
        solo = _node("s", ProductType.COLLECTOR_BOOSTER)
        repo.save(solo)
        with pytest.raises(ChildProductNotAttachedError):
            DetachChildProductFromParentUseCase(solo.internal_id, repo, _Events()).execute()

    def test_expected_parent_mismatch(self) -> None:
        """Contrôle optionnel du parent attendu."""
        repo = _Repo()
        root = _node("r", ProductType.BUNDLE)
        child = _node("c", ProductType.PRERELEASE_KIT, parent="r")
        repo.save(root)
        repo.save(child)
        with pytest.raises(DetachParentMismatchError):
            DetachChildProductFromParentUseCase(
                child.internal_id,
                repo,
                _Events(),
                expected_parent_id=InternalProductId("other"),
            ).execute()

    def test_expected_parent_match_succeeds(self) -> None:
        """expected_parent_id correct."""
        repo = _Repo()
        root = _node("r", ProductType.BUNDLE)
        child = _node("c", ProductType.PRERELEASE_KIT, parent="r")
        repo.save(root)
        repo.save(child)
        events = _Events()
        DetachChildProductFromParentUseCase(
            child.internal_id,
            repo,
            events,
            expected_parent_id=root.internal_id,
        ).execute()
        assert repo.find_by_id(child.internal_id) is not None
        assert repo.find_by_id(child.internal_id).parent_id is None
        assert events.detached == [("c", "r")]
