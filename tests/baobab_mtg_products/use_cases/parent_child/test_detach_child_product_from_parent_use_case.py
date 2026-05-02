"""Tests pour :class:`DetachChildProductFromParentUseCase`."""

from typing import Dict, List, Optional, Tuple

import pytest

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
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

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product

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

    def record_product_opened(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Non utilisé."""
        del product_id, external_card_id, sequence_in_opening

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Non utilisé."""
        del product_id, scan_payload

    def record_product_instance_created(self, product_id: str, reference_id: str) -> None:
        """Non utilisé."""
        del product_id, reference_id

    def record_production_code_assigned(self, product_id: str, production_code: str) -> None:
        """Non utilisé."""
        del product_id, production_code

    def record_container_deconditioned(
        self,
        container_id: str,
        *,
        children_processed: int,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del container_id, children_processed


class _CollectionStub:
    """Double collection."""

    def __init__(self) -> None:
        self.provenance: list[ProductProvenanceForCollection] = []
        self.links: list[ProductParentLinkForCollectionEvent] = []

    def publish_product_provenance(self, provenance: ProductProvenanceForCollection) -> None:
        """Voir :class:`CollectionPort`."""
        self.provenance.append(provenance)

    def publish_parent_child_link(self, link: ProductParentLinkForCollectionEvent) -> None:
        """Voir :class:`CollectionPort`."""
        self.links.append(link)


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

    def test_collection_port_after_detach(self) -> None:
        """Détachement : provenance sans parent + lien inactif."""
        repo = _Repo()
        root = _node("r", ProductType.DISPLAY)
        child = _node("c", ProductType.PLAY_BOOSTER, parent="r")
        repo.save(root)
        repo.save(child)
        collection = _CollectionStub()
        DetachChildProductFromParentUseCase(
            child.internal_id,
            repo,
            _Events(),
            collection=collection,
        ).execute()
        assert len(collection.provenance) == 1
        assert collection.provenance[0].parent_product_id is None
        assert len(collection.links) == 1
        link = collection.links[0]
        assert link.attached is False
        assert link.relationship_kind_value is None
        assert link.parent_product_id == "r"

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
