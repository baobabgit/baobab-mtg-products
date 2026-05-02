"""Tests pour :class:`CreateProductInstanceUseCase`."""

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
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.exceptions.registration.missing_product_ref_workflow_error import (
    ProductReferenceNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.instance.create_product_instance_use_case import (
    CreateProductInstanceUseCase,
)


class _RefRepo:
    """Dépôt références en mémoire."""

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


class _Repo:
    """Dépôt instances en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}
        self.by_int: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_int.get(barcode.value)

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product
        if product.internal_barcode is not None:
            self.by_int[product.internal_barcode.value] = product

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


class _IdFactory:
    """Identifiants prévisibles."""

    def __init__(self, ids: list[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


class _Events:
    """Capture événements de création."""

    def __init__(self) -> None:
        self.created: list[tuple[str, str]] = []

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
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.created.append((product_id, reference_id))

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


class TestCreateProductInstanceUseCase:
    """Création explicite, unicité du code interne, non-unicité du code de production."""

    def test_two_displays_same_reference_and_production_code(self) -> None:
        """Deux exemplaires distincts peuvent partager référence et code de lot."""
        ref_id = ProductReferenceId("ref-display-1")
        ref = ProductReference(
            ref_id,
            name="Display MH3",
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
        )
        ref_repo = _RefRepo()
        ref_repo.save(ref)
        repo = _Repo()
        lot = ProductionCode("BATCH-99")
        events = _Events()
        ids = _IdFactory(["i1", "i2"])
        uc1 = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            ids,
            events,
            production_code=lot,
        )
        uc2 = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            ids,
            events,
            production_code=lot,
        )
        a = uc1.execute()
        b = uc2.execute()
        assert a.internal_id.value != b.internal_id.value
        assert a.reference_id == ref_id == b.reference_id
        assert a.production_code == lot == b.production_code
        assert a.status is ProductStatus.QUALIFIED
        matches = repo.list_by_production_code(lot)
        assert len(matches) == 2
        assert {m.internal_id.value for m in matches} == {"i1", "i2"}
        assert events.created == [
            ("i1", ref_id.value),
            ("i2", ref_id.value),
        ]

    def test_registered_when_reference_requires_qualification(self) -> None:
        """Statut initial aligné sur la référence catalogue."""
        ref_id = ProductReferenceId("ref-pending")
        ref = ProductReference(
            ref_id,
            name="À qualifier",
            product_type=ProductType.OTHER_SEALED,
            set_code=MtgSetCode("XXX"),
            requires_qualification=True,
        )
        ref_repo = _RefRepo()
        ref_repo.save(ref)
        repo = _Repo()
        events = _Events()
        uc = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            _IdFactory(["q0"]),
            events,
        )
        inst = uc.execute()
        assert inst.status is ProductStatus.REGISTERED

    def test_create_with_unique_internal_barcode(self) -> None:
        """Code-barres interne fourni et libre : création acceptée."""
        ref_id = ProductReferenceId("ref-ub")
        ref = ProductReference(
            ref_id,
            name="Y",
            product_type=ProductType.SET_BOOSTER,
            set_code=MtgSetCode("TS"),
            requires_qualification=False,
        )
        ref_repo = _RefRepo()
        ref_repo.save(ref)
        repo = _Repo()
        events = _Events()
        bc = InternalBarcode("INT-NEW")
        uc = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            _IdFactory(["ub1"]),
            events,
            internal_barcode=bc,
        )
        inst = uc.execute()
        assert inst.internal_barcode == bc
        assert repo.find_by_internal_barcode(bc) is inst

    def test_duplicate_internal_barcode_rejected(self) -> None:
        """Le code-barres interne reste unique au niveau dépôt."""
        ref_id = ProductReferenceId("ref-bc")
        ref = ProductReference(
            ref_id,
            name="X",
            product_type=ProductType.SET_BOOSTER,
            set_code=MtgSetCode("TS"),
            requires_qualification=False,
        )
        ref_repo = _RefRepo()
        ref_repo.save(ref)
        repo = _Repo()
        bc = InternalBarcode("INT-001")
        existing = ProductInstance(
            internal_id=InternalProductId("existing"),
            reference_id=ref_id,
            product_type=ProductType.SET_BOOSTER,
            set_code=MtgSetCode("TS"),
            status=ProductStatus.QUALIFIED,
            internal_barcode=bc,
        )
        repo.save(existing)
        events = _Events()
        uc = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            _IdFactory(["new-id"]),
            events,
            internal_barcode=bc,
        )
        with pytest.raises(DuplicateInternalBarcodeError):
            uc.execute()

    def test_missing_reference_raises(self) -> None:
        """Sans référence catalogue, la création est refusée explicitement."""
        ref_id = ProductReferenceId("absent")
        ref_repo = _RefRepo()
        repo = _Repo()
        events = _Events()
        uc = CreateProductInstanceUseCase(
            ref_id,
            repo,
            ref_repo,
            _IdFactory(["x"]),
            events,
        )
        with pytest.raises(ProductReferenceNotFoundForWorkflowError):
            uc.execute()
