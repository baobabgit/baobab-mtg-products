"""Contrats négatifs : le scan commercial ne résout pas une instance par code interne."""

from typing import Dict, List, Optional

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan
from baobab_mtg_products.use_cases.registration.registration_from_scan_runner import (
    RegistrationFromScanRunner,
)


class _TrackingInstanceRepo:
    """Dépôt instance qui compte les lectures par code interne."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}
        self.by_int: Dict[str, ProductInstance] = {}
        self.find_by_internal_barcode_calls: int = 0

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        self.find_by_internal_barcode_calls += 1
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


class _FakeRefRepo:
    """Double de dépôt références."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductReference] = {}
        self.by_com: Dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_id.get(reference_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_com.get(barcode.value)

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference
        if reference.commercial_barcode is not None:
            self.by_com[reference.commercial_barcode.value] = reference


class _FakeResolution:
    """Résolution catalogue."""

    def __init__(self, commercial: ResolvedFromScan, internal: ResolvedFromScan) -> None:
        self._commercial = commercial
        self._internal = internal

    def resolve_commercial(self, barcode: CommercialBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        del barcode
        return self._commercial

    def resolve_internal(self, barcode: InternalBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        del barcode
        return self._internal


class _FakeIdFactory:
    """Identifiants instance."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


class _FakeRefIdFactory:
    """Identifiants référence."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_reference_id(self) -> ProductReferenceId:
        """Voir :class:`ProductReferenceIdFactoryPort`."""
        return ProductReferenceId(self._ids.pop(0))


class _FakeEvents:
    """Journal minimal."""

    def __init__(self) -> None:
        self.scans: List[tuple[str, str, str]] = []
        self.regs: List[str] = []

    def record_scan(self, product_id: str, channel: str, barcode_value: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.scans.append((product_id, channel, barcode_value))

    def record_registration(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.regs.append(product_id)

    def record_product_qualified(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id

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


class TestRegistrationFromScanRunnerContractNegatives:
    """Contrats : scan commercial sans résolution instance par code interne."""

    def test_commercial_scan_never_calls_find_by_internal_barcode_when_ref_exists(self) -> None:
        """Référence déjà persistée : création instance sans lecture par code interne."""
        repo = _TrackingInstanceRepo()
        ref_repo = _FakeRefRepo()
        ean = CommercialBarcode("11111111")
        ref = ProductReference(
            ProductReferenceId("ref-ean"),
            name="Display",
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
            commercial_barcode=ean,
        )
        ref_repo.save(ref)
        resolution = _FakeResolution(ResolvedFromScan(None, None), ResolvedFromScan(None, None))
        runner = RegistrationFromScanRunner(
            repo,
            ref_repo,
            resolution,
            _FakeIdFactory(["i-new"]),
            _FakeRefIdFactory([]),
            _FakeEvents(),
        )
        runner.register_via_commercial(ean)
        assert repo.find_by_internal_barcode_calls == 0

    def test_commercial_scan_never_calls_find_by_internal_barcode_when_catalog_materializes(
        self,
    ) -> None:
        """Pas de ref en dépôt : matérialisation catalogue sans lecture par code interne."""
        repo = _TrackingInstanceRepo()
        ref_repo = _FakeRefRepo()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            ref_repo,
            resolution,
            _FakeIdFactory(["i-cat"]),
            _FakeRefIdFactory(["ref-new"]),
            _FakeEvents(),
        )
        runner.register_via_commercial(CommercialBarcode("22222222"))
        assert repo.find_by_internal_barcode_calls == 0

    def test_internal_scan_calls_find_by_internal_barcode_once(self) -> None:
        """Scan interne : une lecture par code interne attendue."""
        repo = _TrackingInstanceRepo()
        ref_repo = _FakeRefRepo()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.PLAY_BOOSTER, MtgSetCode("MH1")),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            ref_repo,
            resolution,
            _FakeIdFactory(["i1"]),
            _FakeRefIdFactory(["r1"]),
            _FakeEvents(),
        )
        internal = InternalBarcode("INT-ONLY")
        runner.register_via_internal(internal)
        assert repo.find_by_internal_barcode_calls == 1
