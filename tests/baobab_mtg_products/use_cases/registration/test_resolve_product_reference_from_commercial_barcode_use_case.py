"""Tests pour :class:`ResolveProductReferenceFromCommercialBarcodeUseCase`."""

from typing import Optional

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan
from baobab_mtg_products.use_cases.registration import (
    ResolveProductReferenceFromCommercialBarcodeUseCase,
)


class _RefRepo:
    """Dépôt références minimal."""

    def __init__(self) -> None:
        self.by_com: dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        del reference_id

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> ProductReference | None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_com.get(barcode.value)

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        del reference


class _Resolution:
    """Double résolution catalogue."""

    def __init__(self, resolved: ResolvedFromScan) -> None:
        self._resolved = resolved

    def resolve_commercial(self, barcode: CommercialBarcode) -> ResolvedFromScan:
        """Voir :class:`BarcodeResolutionPort`."""
        del barcode
        return self._resolved

    def resolve_internal(self, barcode: InternalBarcode) -> ResolvedFromScan:
        """Non utilisé."""
        del barcode
        return ResolvedFromScan(None, None)


class TestResolveProductReferenceFromCommercialBarcodeUseCase:
    """Résolution EAN sans création d'instance."""

    def test_returns_persistent_reference_when_ean_known(self) -> None:
        """EAN déjà lié à une référence persistée."""
        ref = ProductReference(
            ProductReferenceId("ref-1"),
            name="Boîte",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("11111111"),
        )
        ref_repo = _RefRepo()
        ref_repo.by_com["11111111"] = ref
        uc = ResolveProductReferenceFromCommercialBarcodeUseCase(
            CommercialBarcode("11111111"),
            ref_repo,
            _Resolution(ResolvedFromScan(None, None)),
        )
        out = uc.execute()
        assert out.has_persistent_reference
        assert out.reference_from_repository is ref
        assert out.catalog_resolution is None

    def test_returns_catalog_stub_when_not_in_repository(self) -> None:
        """EAN absent du dépôt : gabarit issu du port de résolution."""
        ref_repo = _RefRepo()
        catalog = ResolvedFromScan(ProductType.DISPLAY, MtgSetCode("MH3"))
        uc = ResolveProductReferenceFromCommercialBarcodeUseCase(
            CommercialBarcode("22222222"),
            ref_repo,
            _Resolution(catalog),
        )
        out = uc.execute()
        assert not out.has_persistent_reference
        assert out.reference_from_repository is None
        assert out.catalog_resolution == catalog
