"""Tests pour QualifyScannedProductUseCase."""

from typing import Dict, Optional

import pytest

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.registration_defaults import RegistrationDefaults
from baobab_mtg_products.exceptions.registration.invalid_qualification_state_error import (
    InvalidQualificationStateError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.registration.qualify_scanned_product_use_case import (
    QualifyScannedProductUseCase,
)


class _RepoStub:
    """Dépôt minimal pour la qualification."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(self, barcode: object) -> Optional[ProductInstance]:
        """Non utilisé ici."""
        del barcode

    def find_by_internal_barcode(self, barcode: object) -> Optional[ProductInstance]:
        """Non utilisé ici."""
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


class _EventsStub:
    """Capture qualification."""

    def __init__(self) -> None:
        self.quals: list[str] = []

    def record_scan(self, *args: object) -> None:
        """Non utilisé."""
        del args

    def record_registration(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_qualified(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.quals.append(product_id)

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del child_id, parent_id, relationship_kind

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del child_id, previous_parent_id

    def record_product_opened(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id, external_card_id, sequence_in_opening

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id, scan_payload


class _CollectionStub:
    """Double collection."""

    def __init__(self) -> None:
        self.provenance: list[ProductProvenanceForCollection] = []
        self.links: list[ProductParentLinkForCollectionEvent] = []

    def publish_product_provenance(self, provenance: ProductProvenanceForCollection) -> None:
        """Voir :class:`CollectionPort`."""
        self.provenance.append(provenance)

    def publish_parent_child_link(self, link: ProductParentLinkForCollectionEvent) -> None:
        """Non utilisé."""
        del link


class TestQualifyScannedProductUseCase:
    """Qualification après scan incomplet."""

    def test_qualify_updates_repository_and_events(self) -> None:
        """Statut « qualified » et événement émis."""
        pid = InternalProductId("q1")
        pending = ProductInstance(
            pid,
            ProductType.OTHER_SEALED,
            RegistrationDefaults.placeholder_set_code(),
            ProductStatus.REGISTERED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = pending
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            events,
        )
        updated = use_case.execute()
        assert updated.status is ProductStatus.QUALIFIED
        assert updated.product_type is ProductType.PLAY_BOOSTER
        assert repo.by_id[pid.value].set_code.value == "MH3"
        assert events.quals == ["q1"]

    def test_collection_port_receives_provenance_when_injected(self) -> None:
        """Après qualification, la provenance reflète le produit qualifié."""
        pid = InternalProductId("q2")
        pending = ProductInstance(
            pid,
            ProductType.OTHER_SEALED,
            RegistrationDefaults.placeholder_set_code(),
            ProductStatus.REGISTERED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = pending
        collection = _CollectionStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            _EventsStub(),
            collection=collection,
        )
        use_case.execute()
        assert len(collection.provenance) == 1
        assert collection.provenance[0].internal_product_id == "q2"
        assert collection.provenance[0].product_status_value == "qualified"

    def test_missing_product_raises(self) -> None:
        """Identifiant inconnu : erreur explicite."""
        repo = _RepoStub()
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            InternalProductId("ghost"),
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            repo,
            events,
        )
        with pytest.raises(ProductNotFoundForWorkflowError):
            use_case.execute()

    def test_non_registered_raises(self) -> None:
        """Un produit déjà qualifié ne repasse pas par ce flux."""
        pid = InternalProductId("bad")
        already = ProductInstance(
            pid,
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            ProductStatus.QUALIFIED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = already
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            events,
        )
        with pytest.raises(InvalidQualificationStateError):
            use_case.execute()
