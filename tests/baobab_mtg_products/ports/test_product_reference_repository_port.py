"""Tests de contrat du port :class:`ProductReferenceRepositoryPort` (double mémoire)."""

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.product.invalid_product_reference_error import (
    InvalidProductReferenceError,
)
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from tests.support.in_memory_product_repositories import InMemoryProductReferenceRepository


def _reference(
    reference_id: str,
    *,
    commercial_barcode: str | None = None,
) -> ProductReference:
    return ProductReference(
        ProductReferenceId(reference_id),
        name=f"nom-{reference_id}",
        product_type=ProductType.BUNDLE,
        set_code=MtgSetCode("FDN"),
        requires_qualification=False,
        commercial_barcode=CommercialBarcode(commercial_barcode) if commercial_barcode else None,
    )


class TestProductReferenceRepositoryPort:
    """Contrat dépôt références avec :class:`InMemoryProductReferenceRepository`."""

    def test_find_by_id_returns_none_when_unknown(self) -> None:
        """Une référence absente se traduit par ``None``, pas par une séquence vide."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        assert adapter.find_by_id(ProductReferenceId("inconnue")) is None

    def test_find_by_commercial_barcode_returns_none_when_unknown(self) -> None:
        """EAN inconnu → ``None``."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        assert adapter.find_by_commercial_barcode(CommercialBarcode("0404040404040")) is None

    def test_save_find_by_id_roundtrip(self) -> None:
        """Persistance et résolution par ``reference_id``."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        ref = _reference("r1", commercial_barcode="99990001")
        adapter.save(ref)
        assert adapter.find_by_id(ProductReferenceId("r1")) is ref

    def test_save_find_by_commercial_barcode_roundtrip(self) -> None:
        """Le code-barres commercial reste au niveau référence ; résolution ``Optional``."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        ref = _reference("r-ean", commercial_barcode="087207027866")
        adapter.save(ref)
        assert adapter.find_by_commercial_barcode(CommercialBarcode("087207027866")) is ref

    def test_commercial_barcode_maps_to_at_most_one_reference_in_memory_adapter(self) -> None:
        """Deux références distinctes ne peuvent pas partager le même EAN (double strict)."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        adapter.save(_reference("r-a", commercial_barcode="111100001111"))
        with pytest.raises(InvalidProductReferenceError):
            adapter.save(_reference("r-b", commercial_barcode="111100001111"))

    def test_updating_same_reference_reindexes_commercial_barcode(self) -> None:
        """Ré-enregistrer la même ``reference_id`` avec un autre EAN libère l’ancien index."""
        adapter: ProductReferenceRepositoryPort = InMemoryProductReferenceRepository()
        adapter.save(_reference("r1", commercial_barcode="111100001111"))
        updated = _reference("r1", commercial_barcode="222200002222")
        adapter.save(updated)
        assert adapter.find_by_commercial_barcode(CommercialBarcode("111100001111")) is None
        assert adapter.find_by_commercial_barcode(CommercialBarcode("222200002222")) is updated
