"""Tests historique — timeline après déconditionnement (feature 12)."""

from __future__ import annotations

from typing import Dict, Optional

from baobab_mtg_products.domain.deconditioning.decondition_child_specification import (
    DeconditionChildSpecification,
)
from baobab_mtg_products.domain.deconditioning.decondition_container_command import (
    DeconditionContainerCommand,
)
from baobab_mtg_products.domain.history.in_memory_product_business_event_ledger import (
    InMemoryProductBusinessEventLedger,
)
from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.services.query.get_product_business_timeline_service import (
    GetProductBusinessTimelineService,
)
from baobab_mtg_products.use_cases.deconditioning.decondition_container_use_case import (
    DeconditionContainerUseCase,
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
        """Voir :class:`ProductRepositoryPort`."""
        del barcode
        return None

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
        del code
        return ()

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


class _RefRepo:
    """Références."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_id.get(reference_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        del barcode
        return None

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference


class _IdFactory:
    """Fabrique simple."""

    def __init__(self, ids: list[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


def test_timeline_lists_decondition_event_for_container() -> None:
    """La timeline du contenant inclut l'événement de déconditionnement."""
    ledger = InMemoryProductBusinessEventLedger()
    ledger.record_registration("disp-1")
    repo = _Repo()
    ref_repo = _RefRepo()
    ref_d = ProductReference(
        ProductReferenceId("ref-d"),
        name="D",
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("MH3"),
        requires_qualification=False,
    )
    ref_pb = ProductReference(
        ProductReferenceId("ref-pb"),
        name="PB",
        product_type=ProductType.PLAY_BOOSTER,
        set_code=MtgSetCode("MH3"),
        requires_qualification=False,
    )
    ref_repo.save(ref_d)
    ref_repo.save(ref_pb)
    disp = ProductInstance(
        InternalProductId("disp-1"),
        ref_d.reference_id,
        ProductType.DISPLAY,
        MtgSetCode("MH3"),
        ProductStatus.SEALED,
    )
    repo.save(disp)
    specs = (
        DeconditionChildSpecification(
            ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
            reference_id=ref_pb.reference_id,
        ),
    )
    cmd = DeconditionContainerCommand(InternalProductId("disp-1"), specs)
    DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["ch1"]), ledger).execute()
    timeline = GetProductBusinessTimelineService(InternalProductId("disp-1"), ledger).load()
    kinds = [r.kind for r in timeline]
    assert ProductBusinessEventKind.CONTAINER_DECONDITIONED in kinds
