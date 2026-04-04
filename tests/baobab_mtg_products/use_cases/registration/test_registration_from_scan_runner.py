"""Tests pour :class:`RegistrationFromScanRunner`."""

from typing import Dict, List, Optional

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
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
    """Double de dépôt en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}
        self.by_com: Dict[str, ProductInstance] = {}
        self.by_int: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_com.get(barcode.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_int.get(barcode.value)

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product
        if product.commercial_barcode is not None:
            self.by_com[product.commercial_barcode.value] = product
        if product.internal_barcode is not None:
            self.by_int[product.internal_barcode.value] = product

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

    def resolve_commercial(self, barcode: CommercialBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        del barcode
        if self._raise_c:
            raise AmbiguousBarcodeResolutionError("Plusieurs produits correspondent.")
        return self._commercial

    def resolve_internal(self, barcode: InternalBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        del barcode
        if self._raise_i:
            raise AmbiguousBarcodeResolutionError("Plusieurs produits correspondent.")
        return self._internal


class _FakeIdFactory:
    """Fournit des identifiants prévisibles."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


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


class TestRegistrationFromScanRunner:
    """Branches principales du flux scan → persistance."""

    def test_commercial_existing_records_scan_only(self) -> None:
        """Produit connu : scan journalisé, pas de nouvel enregistrement."""
        repo = _FakeRepo()
        events = _FakeEvents()
        existing = ProductInstance(
            InternalProductId("old"),
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
            commercial_barcode=CommercialBarcode("12345678"),
        )
        repo.save(existing)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["unused"]),
            events,
        )
        result = runner.register_via_commercial(CommercialBarcode("12345678"))
        assert result.outcome is RegistrationScanOutcome.EXISTING_PRODUCT
        assert result.product.internal_id.value == "old"
        assert not events.regs
        assert events.scans == [("old", "commercial", "12345678")]

    def test_commercial_new_known_from_catalog(self) -> None:
        """Catalogue complet : statut qualifié et issue « new known »."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["n1"]),
            events,
        )
        result = runner.register_via_commercial(CommercialBarcode("12345678"))
        assert result.outcome is RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG
        assert result.product.status is ProductStatus.QUALIFIED
        assert result.product.product_type is ProductType.BUNDLE
        assert events.regs == ["n1"]
        assert len(events.scans) == 1

    def test_commercial_new_pending_qualification(self) -> None:
        """Catalogue vide : placeholder set et type « autre scellé »."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["u1"]),
            events,
        )
        result = runner.register_via_commercial(CommercialBarcode("87654321"))
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
        assert result.product.status is ProductStatus.REGISTERED
        assert result.product.product_type is ProductType.OTHER_SEALED
        assert result.product.set_code.value == "QQ"

    def test_set_override_still_pending_if_type_missing(self) -> None:
        """Override partiel : set fourni mais type encore générique."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["o1"]),
            events,
        )
        result = runner.register_via_commercial(
            CommercialBarcode("11111111"),
            set_code_override=MtgSetCode("MH3"),
        )
        assert result.product.set_code.value == "MH3"
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION

    def test_serial_number_attached_on_create(self) -> None:
        """Le numéro de série optionnel est posé sur la nouvelle instance."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(ProductType.DRAFT_BOOSTER, MtgSetCode("ABC")),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["s1"]),
            events,
        )
        serial = SerialNumber("SN-1")
        result = runner.register_via_commercial(
            CommercialBarcode("22222222"),
            serial_number=serial,
        )
        assert result.product.serial_number == serial

    def test_internal_existing_records_scan_only(self) -> None:
        """Produit connu par code interne : journalisation du scan uniquement."""
        repo = _FakeRepo()
        events = _FakeEvents()
        internal = InternalBarcode("known-tag")
        existing = ProductInstance(
            InternalProductId("int-old"),
            ProductType.SET_BOOSTER,
            MtgSetCode("MH2"),
            ProductStatus.SEALED,
            internal_barcode=internal,
        )
        repo.save(existing)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["unused-internal"]),
            events,
        )
        result = runner.register_via_internal(internal)
        assert result.outcome is RegistrationScanOutcome.EXISTING_PRODUCT
        assert not events.regs
        assert events.scans == [("int-old", "internal", "known-tag")]

    def test_internal_scan_persists_internal_barcode(self) -> None:
        """Scan interne : code interne renseigné sur l'instance."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(ProductType.PLAY_BOOSTER, MtgSetCode("MH1")),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["i1"]),
            events,
        )
        internal = InternalBarcode("tag-1")
        result = runner.register_via_internal(internal)
        assert result.product.internal_barcode == internal
        assert result.outcome is RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG

    def test_both_overrides_produce_qualified_without_catalog(self) -> None:
        """Overrides opérateur complets : pas d'attente de qualification."""
        repo = _FakeRepo()
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["f1"]),
            events,
        )
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
        events = _FakeEvents()
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
            raise_on_commercial=True,
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["x"]),
            events,
        )
        with pytest.raises(AmbiguousBarcodeResolutionError):
            runner.register_via_commercial(CommercialBarcode("33333333"))

    def test_collection_receives_provenance_when_configured(self) -> None:
        """Si un port collection est injecté, chaque issue publie la provenance."""
        repo = _FakeRepo()
        events = _FakeEvents()
        collection = _FakeCollection()
        existing = ProductInstance(
            InternalProductId("old"),
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
            commercial_barcode=CommercialBarcode("12345678"),
        )
        repo.save(existing)
        resolution = _FakeResolution(
            ResolvedFromScan(None, None),
            ResolvedFromScan(None, None),
        )
        runner = RegistrationFromScanRunner(
            repo,
            resolution,
            _FakeIdFactory(["unused"]),
            events,
            collection=collection,
        )
        runner.register_via_commercial(CommercialBarcode("12345678"))
        assert len(collection.provenance) == 1
        assert collection.provenance[0].internal_product_id == "old"

        runner2 = RegistrationFromScanRunner(
            repo,
            _FakeResolution(
                ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
                ResolvedFromScan(None, None),
            ),
            _FakeIdFactory(["n2"]),
            events,
            collection=collection,
        )
        runner2.register_via_commercial(CommercialBarcode("99999999"))
        assert len(collection.provenance) == 2
        assert collection.provenance[1].internal_product_id == "n2"
