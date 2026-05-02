"""Tests pour :class:`DeconditionContainerUseCase`."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pytest

from baobab_mtg_products.domain.deconditioning.decondition_child_specification import (
    DeconditionChildSpecification,
)
from baobab_mtg_products.domain.deconditioning.decondition_container_command import (
    DeconditionContainerCommand,
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
from baobab_mtg_products.exceptions.deconditioning import (
    container_already_deconditioned_error as _cad,
    product_not_deconditionable_container_error as _pnd,
)
from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.exceptions.registration.missing_product_ref_workflow_error import (
    ProductReferenceNotFoundForWorkflowError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.exceptions.relationship.circular_product_parentage_error import (
    CircularProductParentageError,
)
from baobab_mtg_products.exceptions.relationship.product_already_has_parent_error import (
    ProductAlreadyHasParentError,
)
from baobab_mtg_products.use_cases.deconditioning.decondition_container_use_case import (
    DeconditionContainerUseCase,
)


class _Repo:
    """Dépôt instances en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}
        self.save_count = 0

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        for inst in self.by_id.values():
            if inst.internal_barcode is not None and inst.internal_barcode.value == barcode.value:
                return inst
        return None

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.save_count += 1
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


class _RefRepo:
    """Dépôt références."""

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

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference


class _IdFactory:
    """Identifiants internes prévisibles."""

    def __init__(self, ids: List[str]) -> None:
        self._ids = list(ids)

    def new_product_id(self) -> InternalProductId:
        """Voir :class:`InternalProductIdFactoryPort`."""
        return InternalProductId(self._ids.pop(0))


class _Events:
    """Spy journal workflow."""

    def __init__(self) -> None:
        self.attached: List[Tuple[str, str, str]] = []
        self.instance_created: List[Tuple[str, str]] = []
        self.container_deconditioned: List[Tuple[str, int]] = []
        self.card_revealed: List[Tuple[str, str, int]] = []
        self.opening_scan: List[Tuple[str, str]] = []

    def record_scan(self, product_id: str, channel: str, barcode_value: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id, channel, barcode_value

    def record_registration(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        del product_id

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
        self.attached.append((child_id, parent_id, relationship_kind))

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
        self.card_revealed.append((product_id, external_card_id, sequence_in_opening))

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.opening_scan.append((product_id, scan_payload))

    def record_product_instance_created(self, product_id: str, reference_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.instance_created.append((product_id, reference_id))

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
        self.container_deconditioned.append((container_id, children_processed))


def _ref(
    rid: str,
    name: str,
    ptype: ProductType,
    *,
    set_code: str = "MH3",
) -> ProductReference:
    return ProductReference(
        ProductReferenceId(rid),
        name=name,
        product_type=ptype,
        set_code=MtgSetCode(set_code),
        requires_qualification=False,
    )


class TestDeconditionContainerUseCase:
    """Cas nominaux et erreurs métier (fakes de ports)."""

    def test_display_deconditions_into_fifteen_play_boosters(self) -> None:
        """Display → 15 enfants, parent_id cohérent, liste enfants triée stable."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_disp = _ref("ref-d", "Display", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb", "Play Booster", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_disp)
        ref_repo.save(ref_pb)
        display = ProductInstance(
            InternalProductId("disp-1"),
            ref_disp.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(display)
        ids = [f"pb-{i:02d}" for i in range(1, 16)]
        specs = tuple(
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
                internal_barcode=InternalBarcode(f"INT-PB-{i:02d}"),
            )
            for i in range(1, 16)
        )
        cmd = DeconditionContainerCommand(InternalProductId("disp-1"), specs)
        result = DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(ids), events).execute()
        assert result.container.status is ProductStatus.DECONDITIONED
        assert len(result.children) == 15
        kids = repo.list_direct_children_of_parent(InternalProductId("disp-1"))
        assert len(kids) == 15
        assert [k.internal_id.value for k in kids] == ids
        assert all(k.parent_id == InternalProductId("disp-1") for k in kids)
        assert events.container_deconditioned == [("disp-1", 15)]

    def test_bundle_deconditions_into_subproducts(self) -> None:
        """Bundle → sous-produits avec kinds/types conformes."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_b = _ref("ref-b", "Bundle", ProductType.BUNDLE, set_code="FDN")
        ref_sub_a = _ref("ref-sa", "Sub A", ProductType.PLAY_BOOSTER, set_code="FDN")
        ref_sub_b = _ref("ref-sb", "Sub B", ProductType.SET_BOOSTER, set_code="FDN")
        for r in (ref_b, ref_sub_a, ref_sub_b):
            ref_repo.save(r)
        bundle = ProductInstance(
            InternalProductId("bundle-1"),
            ref_b.reference_id,
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            ProductStatus.SEALED,
        )
        repo.save(bundle)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
                reference_id=ref_sub_a.reference_id,
            ),
            DeconditionChildSpecification(
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
                reference_id=ref_sub_b.reference_id,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("bundle-1"), specs)
        DeconditionContainerUseCase(
            cmd,
            repo,
            ref_repo,
            _IdFactory(["sub-a", "sub-b"]),
            events,
        ).execute()
        kids = repo.list_direct_children_of_parent(InternalProductId("bundle-1"))
        assert len(kids) == 2
        assert {k.product_type for k in kids} == {ProductType.PLAY_BOOSTER, ProductType.SET_BOOSTER}

    def test_attach_only_orphans_under_container(self) -> None:
        """Uniquement rattachement d'instances sans parent."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_b = _ref("ref-b2", "Bundle", ProductType.BUNDLE, set_code="FDN")
        ref_p = _ref("ref-p2", "PB", ProductType.PLAY_BOOSTER, set_code="FDN")
        ref_repo.save(ref_b)
        ref_repo.save(ref_p)
        bundle = ProductInstance(
            InternalProductId("b-root"),
            ref_b.reference_id,
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            ProductStatus.SEALED,
        )
        repo.save(bundle)
        orphans = [
            ProductInstance(
                InternalProductId(f"o-{i}"),
                ref_p.reference_id,
                ProductType.PLAY_BOOSTER,
                MtgSetCode("FDN"),
                ProductStatus.SEALED,
            )
            for i in range(3)
        ]
        for o in orphans:
            repo.save(o)
        specs = tuple(
            DeconditionChildSpecification(
                ProductRelationshipKind.BUNDLE_CONTAINS_SUBPRODUCT,
                existing_child_id=o.internal_id,
            )
            for o in orphans
        )
        cmd = DeconditionContainerCommand(InternalProductId("b-root"), specs)
        DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory([]), events).execute()
        assert len(repo.list_direct_children_of_parent(InternalProductId("b-root"))) == 3
        assert len(events.instance_created) == 0

    def test_create_children_from_references_saves_each(self) -> None:
        """Persistance de chaque enfant créé et mise à jour du contenant."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_d = _ref("ref-d3", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb3", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d3"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(disp)
        initial_saves = repo.save_count
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("d3"), specs)
        DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["c1"]), events).execute()
        assert repo.save_count > initial_saves
        assert repo.by_id["c1"].parent_id == InternalProductId("d3")

    def test_container_not_found_raises(self) -> None:
        """ProductNotFoundForWorkflowError."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_pb = _ref("ref-x", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_pb)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("missing"), specs)
        with pytest.raises(ProductNotFoundForWorkflowError):
            DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["n"]), _Events()).execute()

    def test_booster_as_container_target_rejected(self) -> None:
        """Cible non contenant."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_pb = _ref("ref-pb4", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_pb)
        booster_inst = ProductInstance(
            InternalProductId("pb-root"),
            ref_pb.reference_id,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(booster_inst)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                reference_id=ref_pb.reference_id,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("pb-root"), specs)
        with pytest.raises(_pnd.ProductNotDeconditionableContainerError):
            DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["x"]), _Events()).execute()

    def test_child_already_has_parent_rejected(self) -> None:
        """ProductAlreadyHasParentError."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_d = _ref("ref-d4", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb5", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("disp-x"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(disp)
        attached = ProductInstance(
            InternalProductId("kid-attached"),
            ref_pb.reference_id,
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
            parent_id=disp.internal_id,
        )
        repo.save(attached)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                existing_child_id=attached.internal_id,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("disp-x"), specs)
        with pytest.raises(ProductAlreadyHasParentError):
            DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory([]), _Events()).execute()

    def test_cycle_prevention_uses_ancestor_rules(self) -> None:
        """CircularProductParentageError sur lien invalide."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_b = _ref("ref-b3", "B", ProductType.BUNDLE)
        ref_d = _ref("ref-d5", "D", ProductType.DISPLAY)
        ref_repo.save(ref_b)
        ref_repo.save(ref_d)
        bundle = ProductInstance(
            InternalProductId("bundle-p"),
            ref_b.reference_id,
            ProductType.BUNDLE,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        display = ProductInstance(
            InternalProductId("disp-under"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
            parent_id=bundle.internal_id,
        )
        repo.save(bundle)
        repo.save(display)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
                existing_child_id=bundle.internal_id,
            ),
        )
        cmd = DeconditionContainerCommand(display.internal_id, specs)
        with pytest.raises(CircularProductParentageError):
            DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory([]), _Events()).execute()

    def test_missing_reference_when_creating_child_raises(self) -> None:
        """Référence catalogue absente."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_d = _ref("ref-d6", "D", ProductType.DISPLAY)
        ref_repo.save(ref_d)
        disp = ProductInstance(
            InternalProductId("d6"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(disp)
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ProductReferenceId("ghost-ref"),
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("d6"), specs)
        with pytest.raises(ProductReferenceNotFoundForWorkflowError):
            DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["n"]), _Events()).execute()

    def test_duplicate_internal_barcode_on_create_raises(self) -> None:
        """DuplicateInternalBarcodeError."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_d = _ref("ref-d7", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb6", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d7"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(disp)
        dup = InternalBarcode("SAME-INTERNAL")
        specs = (
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
                internal_barcode=dup,
            ),
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
                internal_barcode=dup,
            ),
        )
        cmd = DeconditionContainerCommand(InternalProductId("d7"), specs)
        with pytest.raises(DuplicateInternalBarcodeError):
            DeconditionContainerUseCase(
                cmd,
                repo,
                ref_repo,
                _IdFactory(["a", "b"]),
                _Events(),
            ).execute()

    def test_no_card_reveal_events_emitted(self) -> None:
        """Aucun événement révélation carte / scan ouverture carte."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_d = _ref("ref-d8", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb7", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d8"),
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
        cmd = DeconditionContainerCommand(InternalProductId("d8"), specs)
        DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["c1"]), events).execute()
        assert not events.card_revealed
        assert not events.opening_scan

    def test_container_decondition_event_recorded(self) -> None:
        """Événement déconditionnement traceable."""
        repo = _Repo()
        ref_repo = _RefRepo()
        events = _Events()
        ref_d = _ref("ref-d9", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb8", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d9"),
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
        cmd = DeconditionContainerCommand(InternalProductId("d9"), specs)
        DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["z1"]), events).execute()
        assert events.container_deconditioned == [("d9", 1)]

    def test_partial_children_allowed_five_of_fifteen(self) -> None:
        """Commande partielle acceptée."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_d = _ref("ref-d10", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb9", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d10"),
            ref_d.reference_id,
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(disp)
        specs = tuple(
            DeconditionChildSpecification(
                ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER,
                reference_id=ref_pb.reference_id,
            )
            for _ in range(5)
        )
        ids = [f"p{i}" for i in range(5)]
        cmd = DeconditionContainerCommand(InternalProductId("d10"), specs)
        result = DeconditionContainerUseCase(
            cmd,
            repo,
            ref_repo,
            _IdFactory(ids),
            _Events(),
        ).execute()
        assert len(result.children) == 5

    def test_idempotent_second_call_fails_or_noop(self) -> None:
        """Second passage : erreur défensive."""
        repo = _Repo()
        ref_repo = _RefRepo()
        ref_d = _ref("ref-d11", "D", ProductType.DISPLAY)
        ref_pb = _ref("ref-pb10", "PB", ProductType.PLAY_BOOSTER)
        ref_repo.save(ref_d)
        ref_repo.save(ref_pb)
        disp = ProductInstance(
            InternalProductId("d11"),
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
        cmd = DeconditionContainerCommand(InternalProductId("d11"), specs)
        uc = DeconditionContainerUseCase(cmd, repo, ref_repo, _IdFactory(["one"]), _Events())
        uc.execute()
        with pytest.raises(_cad.ContainerAlreadyDeconditionedError):
            uc.execute()
