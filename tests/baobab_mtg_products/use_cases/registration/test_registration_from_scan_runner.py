"""Tests pour :class:`RegistrationFromScanRunner`."""

from typing import Dict, List, Optional

import pytest

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
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan
from baobab_mtg_products.exceptions.registration.ambiguous_barcode_resolution_error import (
    AmbiguousBarcodeResolutionError,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.use_cases.registration.registration_from_scan_runner import (
    RegistrationFromScanRunner,
)


class _FakeRepo:
    """Double de dépôt instance en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}
        self.by_int: Dict[str, ProductInstance] = {}
        self.find_by_internal_barcode_calls = 0

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
    """Double de résolution catalogue paramétrable."""

    def __init__(
        self,
        commercial: ResolvedFromScan,
        internal: ResolvedFromScan,
        *,
        raise_on_commercial: bool = False,
        raise_on_internal: bool = False,
    ) -> None:
        self._commercial = commercial
        self._internal = internal
        self._raise_c = raise_on_commercial
        self._raise_i = raise_on_internal
        self.resolve_commercial_calls = 0
        self.resolve_internal_calls = 0

    def resolve_commercial(self, barcode: CommercialBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        self.resolve_commercial_calls += 1
        del barcode
        if self._raise_c:
            raise AmbiguousBarcodeResolutionError("Plusieurs produits correspondent.")
        return self._commercial

    def resolve_internal(self, barcode: InternalBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        self.resolve_internal_calls += 1
        del barcode
        if self._raise_i:
            raise AmbiguousBarcodeResolutionError("Plusieurs produits correspondent.")
        return self._internal


class _FakeIdFactory:
    """Fournit des identifiants d'instance prévisibles."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


class _FakeRefIdFactory:
    """Fournit des identifiants de référence prévisibles."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_reference_id(self) -> ProductReferenceId:
        """Voir :class:`ProductReferenceIdFactoryPort`."""
        return ProductReferenceId(self._ids.pop(0))


class _FakeEvents:
    """Capture les événements émis."""

    def __init__(self) -> None:
        self.scans: List[tuple[str, str, str]] = []
        self.regs: List[str] = []
        self.quals: List[str] = []

    def record_scan(self, product_id: str, channel: str, barcode_value: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.scans.append((product_id, channel, barcode_value))

    def record_registration(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.regs.append(product_id)

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


class _FakeCollection:
    """Double du port collection."""

    def __init__(self) -> None:
        self.provenance: list[ProductProvenanceForCollection] = []

    def publish_product_provenance(self, provenance: ProductProvenanceForCollection) -> None:
        """Voir :class:`CollectionPort`."""
        self.provenance.append(provenance)

    def publish_parent_child_link(self, link: object) -> None:
        """Non utilisé dans ces tests."""
        del link


def _runner(
    repo: _FakeRepo,
    ref_repo: _FakeRefRepo,
    resolution: _FakeResolution,
    instance_ids: List[str],
    ref_ids: List[str],
    events: _FakeEvents,
    collection: Optional[_FakeCollection] = None,
) -> RegistrationFromScanRunner:
    return RegistrationFromScanRunner(
        repo,
        ref_repo,
        resolution,
        _FakeIdFactory(instance_ids),
        _FakeRefIdFactory(ref_ids),
        events,
        collection=collection,
    )


def _inventory_two_displays_fifteen_boosters_one_bundle() -> None:
    """Scénario inventaire — voir le test homonyme sur :class:`TestRegistrationFromScanRunner`."""
    # pylint: disable=too-many-locals,too-many-statements
    repo = _FakeRepo()
    ref_repo = _FakeRefRepo()
    events = _FakeEvents()
    ean_display = CommercialBarcode("4006381333930")
    ean_bundle = CommercialBarcode("88888888")
    ref_display = ProductReference(
        ProductReferenceId("ref-mh3-display"),
        name="Display MH3",
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("MH3"),
        requires_qualification=False,
        commercial_barcode=ean_display,
    )
    ref_booster = ProductReference(
        ProductReferenceId("ref-mh3-play"),
        name="Play Booster MH3",
        product_type=ProductType.PLAY_BOOSTER,
        set_code=MtgSetCode("MH3"),
        requires_qualification=False,
    )
    ref_bundle = ProductReference(
        ProductReferenceId("ref-fdn-bundle"),
        name="Bundle FDN",
        product_type=ProductType.BUNDLE,
        set_code=MtgSetCode("FDN"),
        requires_qualification=False,
        commercial_barcode=ean_bundle,
    )
    ref_repo.save(ref_display)
    ref_repo.save(ref_booster)
    ref_repo.save(ref_bundle)
    resolution = _FakeResolution(
        ResolvedFromScan(None, None),
        ResolvedFromScan(None, None),
    )
    runner = _runner(
        repo,
        ref_repo,
        resolution,
        ["disp-1", "disp-2", "bundle-scan", "disp-3"],
        [],
        events,
    )
    r_disp_a = runner.register_via_commercial(ean_display)
    r_disp_b = runner.register_via_commercial(ean_display)
    assert r_disp_a.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
    assert r_disp_b.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
    assert r_disp_a.product is not None and r_disp_b.product is not None
    assert r_disp_a.product.internal_id.value != r_disp_b.product.internal_id.value
    assert r_disp_a.resolved_reference is r_disp_b.resolved_reference is ref_display
    displays = repo.list_by_reference_id(ref_display.reference_id)
    assert len(displays) == 2
    parent_a = r_disp_a.product.internal_id
    parent_b = r_disp_b.product.internal_id
    for d_idx, parent in enumerate((parent_a, parent_b), start=1):
        for k in range(1, 16):
            internal = InternalBarcode(f"INT-MH3-D{d_idx}-PB-{k:02d}")
            booster = ProductInstance(
                internal_id=InternalProductId(f"boost-d{d_idx}-{k:02d}"),
                reference_id=ref_booster.reference_id,
                product_type=ProductType.PLAY_BOOSTER,
                set_code=MtgSetCode("MH3"),
                status=ProductStatus.SEALED,
                internal_barcode=internal,
                parent_id=parent,
            )
            repo.save(booster)
    r_bundle = runner.register_via_commercial(ean_bundle)
    assert r_bundle.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
    assert r_bundle.resolved_reference is ref_bundle
    assert r_bundle.product.internal_id.value == "bundle-scan"
    assert len(repo.list_by_reference_id(ref_booster.reference_id)) == 30
    assert len(repo.list_by_reference_id(ref_bundle.reference_id)) == 1
    assert len(repo.list_direct_children_of_parent(parent_a)) == 15
    assert len(repo.list_direct_children_of_parent(parent_b)) == 15
    ghost_display = ProductInstance(
        internal_id=InternalProductId("pre-existing-display"),
        reference_id=ref_display.reference_id,
        product_type=ProductType.DISPLAY,
        set_code=MtgSetCode("MH3"),
        status=ProductStatus.SEALED,
    )
    repo.save(ghost_display)
    r_after_ghost = runner.register_via_commercial(ean_display)
    assert r_after_ghost.product.internal_id.value == "disp-3"
    assert r_after_ghost.product.internal_id.value != ghost_display.internal_id.value
    assert r_after_ghost.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
    probe = runner.register_via_internal(InternalBarcode("INT-MH3-D1-PB-08"))
    assert probe.outcome is RegistrationScanOutcome.EXISTING_PRODUCT
    assert probe.product is not None
    assert probe.product.internal_id.value == "boost-d1-08"
    assert probe.resolved_reference == ref_booster
    unknown = runner.register_via_internal(InternalBarcode("INT-NEVER-STORED-99"))
    assert unknown.outcome is RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN
    assert unknown.product is None
    assert unknown.resolved_reference is None
    assert events.regs == ["disp-1", "disp-2", "bundle-scan", "disp-3"]
    assert events.scans == [
        ("disp-1", "commercial", "4006381333930"),
        ("disp-2", "commercial", "4006381333930"),
        ("bundle-scan", "commercial", "88888888"),
        ("disp-3", "commercial", "4006381333930"),
        ("boost-d1-08", "internal", "INT-MH3-D1-PB-08"),
    ]
    assert resolution.resolve_internal_calls == 0


class TestRegistrationFromScanRunner:  # pylint: disable=too-many-public-methods
    """Branches principales du flux scan → persistance."""

    def test_commercial_shared_reference_uses_catalog_display_name(self) -> None:
        """Le nom catalogue proposé par :class:`ResolvedFromScan` prime sur les fallback."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(
                ProductType.BUNDLE,
                MtgSetCode("FDN"),
                display_name="  Nom catalogue  ",
            ),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["id-n"], ["ref-dn"], events)
        runner.register_via_commercial(CommercialBarcode("55555555"))
        assert ref_repo.by_id["ref-dn"].name == "Nom catalogue"

    def test_commercial_shared_reference_pending_when_reference_incomplete(self) -> None:
        """Référence encore à qualifier : nouvelle instance « registered »."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        shared_ref = ProductReference(
            ProductReferenceId("ref-pend"),
            name="Pending ref",
            product_type=ProductType.OTHER_SEALED,
            set_code=MtgSetCode("QQ"),
            requires_qualification=True,
            commercial_barcode=CommercialBarcode("66666666"),
        )
        ref_repo.save(shared_ref)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["new-p"], [], events)
        result = runner.register_via_commercial(CommercialBarcode("66666666"))
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
        assert result.product.status is ProductStatus.REGISTERED

    def test_commercial_shared_reference_creates_new_instance(self) -> None:
        """Même code commercial : nouvelle instance, référence réutilisée."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        shared_ref = ProductReference(
            ProductReferenceId("ref-shared"),
            name="MH3 Play",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("12345678"),
        )
        ref_repo.save(shared_ref)
        existing_inst = ProductInstance(
            internal_id=InternalProductId("old"),
            reference_id=shared_ref.reference_id,
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            status=ProductStatus.SEALED,
        )
        repo.save(existing_inst)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["new-a"], [], events)
        result = runner.register_via_commercial(CommercialBarcode("12345678"))
        assert result.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
        assert result.product.internal_id.value == "new-a"
        assert result.product.reference_id.value == "ref-shared"
        assert result.resolved_reference is shared_ref
        assert events.regs == ["new-a"]
        assert events.scans == [("new-a", "commercial", "12345678")]

    def test_commercial_new_known_from_catalog(self) -> None:
        """Catalogue complet : statut qualifié et issue « new known »."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["n1"], ["r1"], events)
        result = runner.register_via_commercial(CommercialBarcode("12345678"))
        assert result.outcome is RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG
        assert result.product.status is ProductStatus.QUALIFIED
        assert result.product.product_type is ProductType.BUNDLE
        assert ref_repo.by_id["r1"].commercial_barcode is not None
        assert result.resolved_reference is ref_repo.by_id["r1"]
        assert events.regs == ["n1"]
        assert len(events.scans) == 1

    def test_commercial_new_pending_qualification(self) -> None:
        """Catalogue vide : placeholder set et type « autre scellé »."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["u1"], ["r2"], events)
        result = runner.register_via_commercial(CommercialBarcode("87654321"))
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
        assert result.product.status is ProductStatus.REGISTERED
        assert result.product.product_type is ProductType.OTHER_SEALED
        assert result.product.set_code.value == "QQ"
        assert result.resolved_reference is ref_repo.by_id["r2"]
        assert result.resolved_reference.requires_qualification is True

    def test_set_override_still_pending_if_type_missing(self) -> None:
        """Override partiel : set fourni mais type encore générique."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["o1"], ["r3"], events)
        result = runner.register_via_commercial(
            CommercialBarcode("11111111"),
            set_code_override=MtgSetCode("MH3"),
        )
        assert result.product.set_code.value == "MH3"
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION

    def test_serial_number_attached_on_create(self) -> None:
        """Le numéro de série optionnel est posé sur la nouvelle instance."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.DRAFT_BOOSTER, MtgSetCode("ABC")),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["s1"], ["r4"], events)
        serial = SerialNumber("SN-1")
        result = runner.register_via_commercial(
            CommercialBarcode("22222222"),
            serial_number=serial,
        )
        assert result.product.serial_number == serial

    def test_internal_existing_records_scan_only(self) -> None:
        """Produit connu par code interne : journalisation du scan uniquement."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        internal = InternalBarcode("known-tag")
        ref = ProductReference(
            ProductReferenceId("ref-int"),
            name="Internal ref",
            product_type=ProductType.SET_BOOSTER,
            set_code=MtgSetCode("MH2"),
            requires_qualification=False,
        )
        ref_repo.save(ref)
        existing = ProductInstance(
            internal_id=InternalProductId("int-old"),
            reference_id=ref.reference_id,
            product_type=ProductType.SET_BOOSTER,
            set_code=MtgSetCode("MH2"),
            status=ProductStatus.SEALED,
            internal_barcode=internal,
        )
        repo.save(existing)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(
            repo,
            ref_repo,
            resolution,
            ["unused-internal"],
            [],
            events,
        )
        result = runner.register_via_internal(internal)
        assert result.outcome is RegistrationScanOutcome.EXISTING_PRODUCT
        assert result.resolved_reference is ref
        assert not events.regs
        assert events.scans == [("int-old", "internal", "known-tag")]

    def test_internal_unknown_barcode_does_not_materialize(self) -> None:
        """Code interne inconnu : pas d'instance ni d'enregistrement implicite."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(ProductType.PLAY_BOOSTER, MtgSetCode("MH1")),
        )
        runner = _runner(repo, ref_repo, resolution, ["i1"], ["r5"], events)
        internal = InternalBarcode("tag-unknown")
        result = runner.register_via_internal(internal)
        assert result.product is None
        assert result.outcome is RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN
        assert result.resolved_reference is None
        assert not events.regs
        assert not events.scans
        assert len(repo.by_id) == 0
        assert resolution.resolve_internal_calls == 0

    def test_two_commercial_scans_same_ean_two_instances(self) -> None:
        """Scénario deux displays : deux scans EAN identiques → deux instances distinctes."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        shared_ref = ProductReference(
            ProductReferenceId("ref-display"),
            name="Display MH3",
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("4006381333930"),
        )
        ref_repo.save(shared_ref)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["disp-a", "disp-b"], [], events)
        r1 = runner.register_via_commercial(CommercialBarcode("4006381333930"))
        r2 = runner.register_via_commercial(CommercialBarcode("4006381333930"))
        assert r1.product.internal_id.value != r2.product.internal_id.value
        assert r1.product.reference_id == r2.product.reference_id == shared_ref.reference_id
        assert r1.resolved_reference is r2.resolved_reference is shared_ref
        rows = repo.list_by_reference_id(shared_ref.reference_id)
        assert len(rows) == 2
        assert events.regs == ["disp-a", "disp-b"]
        assert r1.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
        assert r2.outcome is RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE
        assert events.scans == [
            ("disp-a", "commercial", "4006381333930"),
            ("disp-b", "commercial", "4006381333930"),
        ]
        assert repo.find_by_internal_barcode_calls == 0
        assert resolution.resolve_commercial_calls == 0

    def test_two_commercial_scans_same_ean_create_two_distinct_instances(self) -> None:
        """Plan 11 §6 — alias explicite : même EAN, deux instances, pas de lookup interne."""
        self.test_two_commercial_scans_same_ean_two_instances()

    def test_commercial_scan_existing_reference_creates_new_instance_and_exposes_reference(
        self,
    ) -> None:
        """Plan 11 §7 — référence persistée + nouvelle instance + ``resolved_reference``."""
        self.test_commercial_shared_reference_creates_new_instance()

    def test_commercial_scan_catalog_complete_creates_reference_and_instance(self) -> None:
        """Plan 11 §8 — catalogue complet → référence créée + instance qualifiée."""
        self.test_commercial_new_known_from_catalog()

    def test_commercial_scan_catalog_incomplete_creates_pending_qualification_instance(
        self,
    ) -> None:
        """Plan 11 §9 — résolution vide → pending qualification."""
        self.test_commercial_new_pending_qualification()

    def test_both_overrides_produce_qualified_without_catalog(self) -> None:
        """Overrides opérateur complets : pas d'attente de qualification."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(repo, ref_repo, resolution, ["f1"], ["r6"], events)
        result = runner.register_via_commercial(
            CommercialBarcode("44444444"),
            product_type_override=ProductType.BUNDLE,
            set_code_override=MtgSetCode("FDN"),
        )
        assert result.outcome is RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG
        assert result.product.status is ProductStatus.QUALIFIED

    def test_ambiguous_resolution_propagates(self) -> None:
        """Une ambiguïté catalogue remonte telle quelle."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
            raise_on_commercial=True,
        )
        runner = _runner(repo, ref_repo, resolution, ["x"], [], events)
        with pytest.raises(AmbiguousBarcodeResolutionError):
            runner.register_via_commercial(CommercialBarcode("33333333"))
        assert len(repo.by_id) == 0
        assert not events.regs
        assert not events.scans

    def test_commercial_scan_ambiguous_catalog_resolution_propagates_error(self) -> None:
        """Plan 11 §10 — l’ambiguïté n’est pas avalée et rien n’est persisté."""
        self.test_ambiguous_resolution_propagates()

    def test_internal_scan_known_barcode_returns_exact_instance(self) -> None:
        """Plan 11 §11 — instance retrouvée par code interne, scan journalisé."""
        self.test_internal_existing_records_scan_only()

    def test_internal_scan_unknown_barcode_returns_explicit_unknown_result(self) -> None:
        """Plan 11 §12 — inconnu explicite, pas de catalogue interne."""
        self.test_internal_unknown_barcode_does_not_materialize()

    def test_collection_receives_provenance_when_configured(
        self,
    ) -> None:  # pylint: disable=too-many-locals
        """Si un port collection est injecté, chaque issue publie la provenance."""
        repo = _FakeRepo()
        ref_repo = _FakeRefRepo()
        events = _FakeEvents()
        collection = _FakeCollection()
        shared_ref = ProductReference(
            ProductReferenceId("ref-col"),
            name="Col",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("12345678"),
        )
        ref_repo.save(shared_ref)
        repo.save(
            ProductInstance(
                internal_id=InternalProductId("old"),
                reference_id=shared_ref.reference_id,
                product_type=ProductType.PLAY_BOOSTER,
                set_code=MtgSetCode("MH3"),
                status=ProductStatus.SEALED,
            ),
        )
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = _runner(
            repo,
            ref_repo,
            resolution,
            ["new-col"],
            [],
            events,
            collection=collection,
        )
        runner.register_via_commercial(CommercialBarcode("12345678"))
        assert len(collection.provenance) == 1
        assert collection.provenance[0].internal_product_id == "new-col"

        runner2 = _runner(
            repo,
            ref_repo,
            _FakeResolution(
                ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
                ResolvedFromScan(None, None),
            ),
            ["n2"],
            ["r-new"],
            events,
            collection=collection,
        )
        runner2.register_via_commercial(CommercialBarcode("99999999"))
        assert len(collection.provenance) == 2
        assert collection.provenance[1].internal_product_id == "n2"

    def test_inventory_two_displays_fifteen_boosters_one_bundle(self) -> None:
        """Inventaire : 2 displays (même EAN), 15 boosters par display, 1 bundle, scan interne.

        Démonstration sans déconditionnement complet : les instances booster sont
        matérialisées en dépôt avec parent (comme après rattachement structurel). Les
        scans commerciaux ne fusionnent jamais deux exemplaires ; le bundle est créé par
        scan commercial sur sa référence déjà catalogue.
        """
        _inventory_two_displays_fifteen_boosters_one_bundle()
