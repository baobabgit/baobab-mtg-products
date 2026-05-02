"""Tests pour :class:`CommercialReferenceResolutionResult`."""

from dataclasses import fields

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.commercial_reference_resolution_result import (
    CommercialReferenceResolutionResult,
)
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan


class TestCommercialReferenceResolutionResult:
    """Résolution EAN → référence sans matérialisation d’exemplaire."""

    def test_commercial_reference_resolution_result_detects_persistent_reference(self) -> None:
        """Référence déjà stockée : drapeau explicite, pas de gabarit catalogue."""
        ref = ProductReference(
            ProductReferenceId("r1"),
            name="X",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("11111111"),
        )
        out = CommercialReferenceResolutionResult(reference_from_repository=ref)
        assert out.has_persistent_reference
        assert out.reference_from_repository is ref
        assert out.catalog_resolution is None

    def test_commercial_reference_resolution_result_detects_catalog_template_only(self) -> None:
        """Aucune persistance : uniquement le gabarit issu du port de résolution."""
        template = ResolvedFromScan(ProductType.DISPLAY, MtgSetCode("MH3"))
        out = CommercialReferenceResolutionResult(catalog_resolution=template)
        assert not out.has_persistent_reference
        assert out.reference_from_repository is None
        assert out.catalog_resolution == template

    def test_commercial_reference_resolution_result_branches_are_exclusive_in_nominal_use(
        self,
    ) -> None:
        """Contrat métier : soit dépôt soit catalogue pour un même résultat nominal."""
        ref = ProductReference(
            ProductReferenceId("r2"),
            name="Y",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
        )
        persistent = CommercialReferenceResolutionResult(reference_from_repository=ref)
        assert persistent.reference_from_repository is not None
        assert persistent.catalog_resolution is None

        catalog_only = CommercialReferenceResolutionResult(
            catalog_resolution=ResolvedFromScan(ProductType.BUNDLE, MtgSetCode("FDN")),
        )
        assert catalog_only.reference_from_repository is None
        assert catalog_only.catalog_resolution is not None

    def test_commercial_reference_resolution_result_does_not_represent_a_physical_instance(
        self,
    ) -> None:
        """Ce DTO ne porte aucune :class:`ProductInstance` (résolution référence seule)."""
        names = {f.name for f in fields(CommercialReferenceResolutionResult)}
        assert names == {"reference_from_repository", "catalog_resolution"}
