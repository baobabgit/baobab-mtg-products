"""Tests pour :class:`AssignProductionCodeToProductInstanceUseCase`."""

from typing import Dict, Optional

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.instance import (
    AssignProductionCodeToProductInstanceUseCase,
)


class _Repo:
    """Dépôt instances en mémoire."""

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
    """Capture association code de production."""

    def __init__(self) -> None:
        self.assigned: list[tuple[str, str]] = []

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
        """Non utilisé."""
        del product_id, reference_id

    def record_production_code_assigned(self, product_id: str, production_code: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.assigned.append((product_id, production_code))


class TestAssignProductionCodeToProductInstanceUseCase:
    """Saisie différée du code de lot et journalisation."""

    def test_assigns_code_and_records_event(self) -> None:
        """Mise à jour persistante et événement dédié."""
        pid = InternalProductId("p-assign")
        ref = ProductReferenceId("ref-1")
        inst = ProductInstance(
            internal_id=pid,
            reference_id=ref,
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
        )
        repo = _Repo()
        repo.save(inst)
        events = _Events()
        code = ProductionCode("LOT-7")
        out = AssignProductionCodeToProductInstanceUseCase(
            pid,
            code,
            repo,
            events,
        ).execute()
        assert out.production_code == code
        assert repo.find_by_id(pid) is not None
        assert repo.find_by_id(pid).production_code == code
        assert events.assigned == [(pid.value, code.value)]

    def test_unknown_product_raises(self) -> None:
        """Aucune ambiguïté : identifiant inconnu → erreur métier explicite."""
        repo = _Repo()
        events = _Events()
        uc = AssignProductionCodeToProductInstanceUseCase(
            InternalProductId("ghost"),
            ProductionCode("X"),
            repo,
            events,
        )
        with pytest.raises(ProductNotFoundForWorkflowError):
            uc.execute()
