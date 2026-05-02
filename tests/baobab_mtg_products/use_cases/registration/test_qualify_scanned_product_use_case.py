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
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.domain.registration.registration_defaults import RegistrationDefaults
from baobab_mtg_products.exceptions.registration.invalid_qualification_state_error import (
    InvalidQualificationStateError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.exceptions.registration.missing_product_ref_workflow_error import (
    ProductReferenceNotFoundForWorkflowError,
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

    def find_by_internal_barcode(self, barcode: object) -> Optional[ProductInstance]:
        """Non utilisé ici."""
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


class _RefRepoStub:
    """Dépôt références pour la qualification."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_id.get(reference_id.value)

    def find_by_commercial_barcode(self, barcode: object) -> Optional[ProductReference]:
        """Non utilisé."""
        del barcode

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference


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

    def record_product_instance_created(self, product_id: str, reference_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id, reference_id

    def record_production_code_assigned(self, product_id: str, production_code: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
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
        """Non utilisé."""
        del link


class TestQualifyScannedProductUseCase:
    """Qualification après scan incomplet."""

    def test_qualify_updates_repository_reference_and_events(self) -> None:
        """Statut « qualified », référence alignée et événement émis."""
        pid = InternalProductId("q1")
        ref = ProductReference(
            ProductReferenceId("ref-q1"),
            name="Pending",
            product_type=ProductType.OTHER_SEALED,
            set_code=RegistrationDefaults.placeholder_set_code(),
            requires_qualification=True,
        )
        pending = ProductInstance(
            internal_id=pid,
            reference_id=ref.reference_id,
            product_type=ProductType.OTHER_SEALED,
            set_code=RegistrationDefaults.placeholder_set_code(),
            status=ProductStatus.REGISTERED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = pending
        ref_repo = _RefRepoStub()
        ref_repo.by_id[ref.reference_id.value] = ref
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            ref_repo,
            events,
        )
        updated = use_case.execute()
        assert updated.status is ProductStatus.QUALIFIED
        assert updated.product_type is ProductType.PLAY_BOOSTER
        assert repo.by_id[pid.value].set_code.value == "MH3"
        saved_ref = ref_repo.by_id[ref.reference_id.value]
        assert saved_ref.product_type is ProductType.PLAY_BOOSTER
        assert saved_ref.requires_qualification is False
        assert events.quals == ["q1"]

    def test_collection_port_receives_provenance_when_injected(self) -> None:
        """Après qualification, la provenance reflète le produit qualifié."""
        pid = InternalProductId("q2")
        ref = ProductReference(
            ProductReferenceId("ref-q2"),
            name="P",
            product_type=ProductType.OTHER_SEALED,
            set_code=RegistrationDefaults.placeholder_set_code(),
            requires_qualification=True,
        )
        pending = ProductInstance(
            internal_id=pid,
            reference_id=ref.reference_id,
            product_type=ProductType.OTHER_SEALED,
            set_code=RegistrationDefaults.placeholder_set_code(),
            status=ProductStatus.REGISTERED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = pending
        ref_repo = _RefRepoStub()
        ref_repo.by_id[ref.reference_id.value] = ref
        collection = _CollectionStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            ref_repo,
            _EventsStub(),
            collection=collection,
        )
        use_case.execute()
        assert len(collection.provenance) == 1
        assert collection.provenance[0].internal_product_id == "q2"
        assert collection.provenance[0].product_reference_id == "ref-q2"
        assert collection.provenance[0].product_status_value == "qualified"

    def test_missing_product_raises(self) -> None:
        """Identifiant inconnu : erreur explicite."""
        repo = _RepoStub()
        ref_repo = _RefRepoStub()
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            InternalProductId("ghost"),
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            repo,
            ref_repo,
            events,
        )
        with pytest.raises(ProductNotFoundForWorkflowError):
            use_case.execute()

    def test_missing_reference_raises(self) -> None:
        """Référence absente : erreur dédiée."""
        pid = InternalProductId("orphan")
        pending = ProductInstance(
            internal_id=pid,
            reference_id=ProductReferenceId("missing-ref"),
            product_type=ProductType.OTHER_SEALED,
            set_code=RegistrationDefaults.placeholder_set_code(),
            status=ProductStatus.REGISTERED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = pending
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            _RefRepoStub(),
            _EventsStub(),
        )
        with pytest.raises(ProductReferenceNotFoundForWorkflowError):
            use_case.execute()

    def test_non_registered_raises(self) -> None:
        """Un produit déjà qualifié ne repasse pas par ce flux."""
        pid = InternalProductId("bad")
        ref = ProductReference(
            ProductReferenceId("ref-bad"),
            name="B",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
        )
        already = ProductInstance(
            internal_id=pid,
            reference_id=ref.reference_id,
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.QUALIFIED,
        )
        repo = _RepoStub()
        repo.by_id[pid.value] = already
        ref_repo = _RefRepoStub()
        ref_repo.by_id[ref.reference_id.value] = ref
        events = _EventsStub()
        use_case = QualifyScannedProductUseCase(
            pid,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            repo,
            ref_repo,
            events,
        )
        with pytest.raises(InvalidQualificationStateError):
            use_case.execute()
