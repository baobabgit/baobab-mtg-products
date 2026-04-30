"""Tests structurels du port :class:`ProductReferenceRepositoryPort`."""

from typing import Dict, Optional

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)


class _FakeRefRepo:
    """Adaptateur minimal."""

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


class TestProductReferenceRepositoryPort:
    """Contrat dépôt références."""

    def test_roundtrip_by_id_and_commercial(self) -> None:
        """Persistance et résolution par identifiant ou code commercial."""
        fake = _FakeRefRepo()
        adapter: ProductReferenceRepositoryPort = fake
        ref = ProductReference(
            ProductReferenceId("r1"),
            name="Test",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("9999"),
        )
        adapter.save(ref)
        assert adapter.find_by_id(ProductReferenceId("r1")) is ref
        assert adapter.find_by_commercial_barcode(CommercialBarcode("9999")) is ref
