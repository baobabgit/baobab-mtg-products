"""Tests pour :class:`AttachChildProductToParentUseCase`."""

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
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.circular_product_parentage_error import (
    CircularProductParentageError,
)
from baobab_mtg_products.exceptions.relationship.incomplete_product_hierarchy_error import (
    IncompleteProductHierarchyError,
)
from baobab_mtg_products.exceptions.relationship.incompatible_parent_child_types_error import (
    IncompatibleParentChildTypesError,
)
from baobab_mtg_products.exceptions.relationship.invalid_product_relationship_link_error import (
    InvalidProductRelationshipLinkError,
)
from baobab_mtg_products.exceptions.relationship.product_already_has_parent_error import (
    ProductAlreadyHasParentError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.parent_child.attach_child_product_to_parent_use_case import (
    AttachChildProductToParentUseCase,
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
    """Capture rattachements."""

    def __init__(self) -> None:
        self.attached: List[Tuple[str, str, str]] = []

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
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.attached.append((child_id, parent_id, relationship_kind))

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Non utilisé."""
        del child_id, previous_parent_id

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


class TestAttachChildProductToParentUseCase:
    """Flux nominal et rejets."""

    def test_display_booster_attach_persists_and_events(self) -> None:
        """Rattachement display → booster."""
        repo = _Repo()
        display = _node("d", ProductType.DISPLAY)
        booster = _node("b", ProductType.PLAY_BOOSTER)
        repo.save(display)
        repo.save(booster)
        events = _Events()
        rel = AttachChildProductToParentUseCase(
            display.internal_id,
            booster.internal_id,
            ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
            repo,
            events,
        ).execute()
        assert rel.kind is ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER
        updated = repo.find_by_id(booster.internal_id)
        assert updated is not None
        assert updated.parent_id is not None
        assert updated.parent_id.value == "d"
        assert events.attached == [("b", "d", "display_contains_booster")]

    def test_collection_port_receives_provenance_and_link(self) -> None:
        """Rattachement : provenance enfant mise à jour + lien actif."""
        repo = _Repo()
        display = _node("d", ProductType.DISPLAY)
        booster = _node("b", ProductType.PLAY_BOOSTER)
        repo.save(display)
        repo.save(booster)
        collection = _CollectionStub()
        AttachChildProductToParentUseCase(
            display.internal_id,
            booster.internal_id,
            ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
            repo,
            _Events(),
            collection=collection,
        ).execute()
        assert len(collection.provenance) == 1
        assert collection.provenance[0].internal_product_id == "b"
        assert collection.provenance[0].parent_product_id == "d"
        assert len(collection.links) == 1
        assert collection.links[0].attached is True
        assert collection.links[0].relationship_kind_value == "display_contains_booster"

    def test_booster_without_parent_remains_valid_model(self) -> None:
        """Booster sans parent : attach optionnel."""
        repo = _Repo()
        booster = _node("solo", ProductType.SET_BOOSTER)
        repo.save(booster)
        assert repo.find_by_id(booster.internal_id) is not None
        assert repo.find_by_id(booster.internal_id).parent_id is None

    def test_rejects_same_id(self) -> None:
        """Parent et enfant identiques."""
        repo = _Repo()
        p = _node("x", ProductType.DISPLAY)
        repo.save(p)
        with pytest.raises(InvalidProductRelationshipLinkError):
            AttachChildProductToParentUseCase(
                InternalProductId("x"),
                InternalProductId("x"),
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                repo,
                _Events(),
            ).execute()

    def test_rejects_missing_parent(self) -> None:
        """Parent inconnu."""
        repo = _Repo()
        c = _node("c", ProductType.PLAY_BOOSTER)
        repo.save(c)
        with pytest.raises(ProductNotFoundForWorkflowError):
            AttachChildProductToParentUseCase(
                InternalProductId("missing"),
                c.internal_id,
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                repo,
                _Events(),
            ).execute()

    def test_rejects_missing_child(self) -> None:
        """Enfant inconnu."""
        repo = _Repo()
        p = _node("p", ProductType.BUNDLE)
        repo.save(p)
        with pytest.raises(ProductNotFoundForWorkflowError):
            AttachChildProductToParentUseCase(
                p.internal_id,
                InternalProductId("nope"),
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
                repo,
                _Events(),
            ).execute()

    def test_rejects_child_already_attached(self) -> None:
        """Enfant déjà rattaché."""
        repo = _Repo()
        root = _node("r", ProductType.BUNDLE)
        child = _node("c", ProductType.PLAY_BOOSTER, parent="r")
        repo.save(root)
        repo.save(child)
        other = _node("o", ProductType.BUNDLE)
        repo.save(other)
        with pytest.raises(ProductAlreadyHasParentError):
            AttachChildProductToParentUseCase(
                other.internal_id,
                child.internal_id,
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                repo,
                _Events(),
            ).execute()

    def test_rejects_incompatible_types(self) -> None:
        """Kind display avec parent non-display."""
        repo = _Repo()
        b = _node("b", ProductType.BUNDLE)
        p = _node("p", ProductType.PLAY_BOOSTER)
        repo.save(b)
        repo.save(p)
        with pytest.raises(IncompatibleParentChildTypesError):
            AttachChildProductToParentUseCase(
                b.internal_id,
                p.internal_id,
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                repo,
                _Events(),
            ).execute()

    def test_rejects_cycle(self) -> None:
        """B ancêtre de A : rattacher B sous A interdit."""
        repo = _Repo()
        b = _node("b", ProductType.BUNDLE)
        a = _node("a", ProductType.PLAY_BOOSTER, parent="b")
        repo.save(b)
        repo.save(a)
        with pytest.raises(CircularProductParentageError):
            AttachChildProductToParentUseCase(
                a.internal_id,
                b.internal_id,
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                repo,
                _Events(),
            ).execute()

    def test_rejects_broken_parent_chain(self) -> None:
        """Parent avec ancêtre fantôme."""
        repo = _Repo()
        ghost_child = _node("c", ProductType.PLAY_BOOSTER, parent="ghost")
        booster = _node("b", ProductType.PLAY_BOOSTER)
        repo.save(ghost_child)
        repo.save(booster)
        with pytest.raises(IncompleteProductHierarchyError):
            AttachChildProductToParentUseCase(
                ghost_child.internal_id,
                booster.internal_id,
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                repo,
                _Events(),
            ).execute()
