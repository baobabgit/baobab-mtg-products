"""Tests pour :class:`GetSealedProductSnapshotService`."""

from typing import Dict, Optional

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.exceptions.query.product_reference_not_found_for_query_error import (
    ProductReferenceNotFoundForQueryError,
)
from baobab_mtg_products.services.query.get_sealed_product_snapshot_service import (
    GetSealedProductSnapshotService,
)


class _Repo:
    """Dépôt instance minimal."""

    def __init__(self) -> None:
        self.by_id: dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> ProductInstance | None:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        _barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

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

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product


class _RefRepo:
    """Dépôt références minimal."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductReference] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> ProductReference | None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self.by_id.get(reference_id.value)

    def find_by_commercial_barcode(self, barcode: object) -> ProductReference | None:
        """Non utilisé."""
        del barcode

    def save(self, reference: ProductReference) -> None:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        self.by_id[reference.reference_id.value] = reference


class TestGetSealedProductSnapshotService:
    """Lecture nominale ou rejet."""

    def test_load_returns_instance_and_reference(self) -> None:
        """Produit présent : instantané aligné instance + référence."""
        pid = InternalProductId("p1")
        ref = ProductReference(
            ProductReferenceId("ref-p1"),
            name="Bundle FDN",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
        )
        inst = ProductInstance(
            internal_id=pid,
            reference_id=ref.reference_id,
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
        )
        repo = _Repo()
        ref_repo = _RefRepo()
        repo.save(inst)
        ref_repo.save(ref)
        out = GetSealedProductSnapshotService(pid, repo, ref_repo).load()
        assert out.product is inst
        assert out.reference is ref
        assert out.reference.name == "Bundle FDN"

    def test_missing_instance_raises(self) -> None:
        """Identifiant instance inconnu."""
        with pytest.raises(ProductNotFoundForQueryError):
            GetSealedProductSnapshotService(
                InternalProductId("ghost"),
                _Repo(),
                _RefRepo(),
            ).load()

    def test_missing_reference_raises(self) -> None:
        """Référence manquante pour une instance connue."""
        pid = InternalProductId("p2")
        inst = ProductInstance(
            internal_id=pid,
            reference_id=ProductReferenceId("absent"),
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.SEALED,
        )
        repo = _Repo()
        repo.save(inst)
        with pytest.raises(ProductReferenceNotFoundForQueryError):
            GetSealedProductSnapshotService(pid, repo, _RefRepo()).load()
