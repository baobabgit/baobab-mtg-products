"""Tests pour :class:`GetSealedProductSnapshotService`."""

from typing import Optional

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.services.query.get_sealed_product_snapshot_service import (
    GetSealedProductSnapshotService,
)


class _Repo:
    """Dépôt minimal."""

    def __init__(self) -> None:
        self.by_id: dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> ProductInstance | None:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        _barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

    def find_by_internal_barcode(
        self,
        _barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return None

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


class TestGetSealedProductSnapshotService:
    """Lecture nominale ou rejet."""

    def test_load_returns_instance(self) -> None:
        """Produit présent : agrégat renvoyé."""
        pid = InternalProductId("p1")
        inst = ProductInstance(
            pid,
            ProductType.BUNDLE,
            MtgSetCode("FDN"),
            ProductStatus.SEALED,
        )
        repo = _Repo()
        repo.save(inst)
        out = GetSealedProductSnapshotService(pid, repo).load()
        assert out is inst

    def test_missing_raises(self) -> None:
        """Identifiant inconnu."""
        with pytest.raises(ProductNotFoundForQueryError):
            GetSealedProductSnapshotService(
                InternalProductId("ghost"),
                _Repo(),
            ).load()
