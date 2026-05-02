"""Tests pour :class:`RegistrationScanResult`."""

import dataclasses

import pytest

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)


class TestRegistrationScanResult:
    """DTO résultat de scan."""

    def test_holds_product_and_outcome(self) -> None:
        """Le résultat lie instance et issue."""
        product = ProductInstance(
            internal_id=InternalProductId("p"),
            reference_id=ProductReferenceId("ref-p"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("MH3"),
            status=ProductStatus.REGISTERED,
        )
        result = RegistrationScanResult(
            product,
            RegistrationScanOutcome.NEW_PENDING_QUALIFICATION,
        )
        assert result.product is product
        assert result.outcome is RegistrationScanOutcome.NEW_PENDING_QUALIFICATION
        assert result.resolved_reference is None

    def test_internal_unknown_pattern(self) -> None:
        """Résultat explicite sans instance."""
        result = RegistrationScanResult(
            None,
            RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN,
        )
        assert result.product is None
        assert result.resolved_reference is None

    def test_registration_scan_result_accepts_none_product_for_unknown_internal_barcode(
        self,
    ) -> None:
        """Plan 11 — scan interne inconnu : pas d’instance ni de référence résolue."""
        self.test_internal_unknown_pattern()

    def test_registration_scan_result_exposes_resolved_reference(self) -> None:
        """Plan 11 — après résolution catalogue / dépôt, la référence est exposée."""
        self.test_resolved_reference_optional()

    def test_registration_scan_result_is_immutable(self) -> None:
        """Le DTO est gelé : mutation interdite."""
        result = RegistrationScanResult(
            None,
            RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.product = None  # type: ignore[misc]

    def test_resolved_reference_optional(self) -> None:
        """Référence catalogue alignée sur l'instance."""
        ref = ProductReference(
            ProductReferenceId("r-x"),
            name="Ref",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
        )
        product = ProductInstance(
            internal_id=InternalProductId("p2"),
            reference_id=ref.reference_id,
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.QUALIFIED,
        )
        result = RegistrationScanResult(
            product,
            RegistrationScanOutcome.EXISTING_PRODUCT,
            resolved_reference=ref,
        )
        assert result.resolved_reference is ref
