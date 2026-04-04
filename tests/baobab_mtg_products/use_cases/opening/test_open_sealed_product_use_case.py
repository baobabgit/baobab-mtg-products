"""Tests pour :class:`OpenSealedProductUseCase`."""

from typing import Dict, List, Optional, Tuple

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.opening.product_already_opened_error import (
    ProductAlreadyOpenedError,
)
from baobab_mtg_products.exceptions.opening.product_not_openable_error import (
    ProductNotOpenableError,
)
from baobab_mtg_products.exceptions.opening.product_not_ready_for_opening_error import (
    ProductNotReadyForOpeningError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.use_cases.opening.open_sealed_product_use_case import (
    OpenSealedProductUseCase,
)


class _Repo:
    """Dépôt en mémoire."""

    def __init__(self) -> None:
        self.by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self.by_id.get(product_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Non utilisé."""
        del barcode

    def save(self, product: ProductInstance) -> None:
        """Voir :class:`ProductRepositoryPort`."""
        self.by_id[product.internal_id.value] = product


class _Events:
    """Capture ouvertures."""

    def __init__(self) -> None:
        self.opened: List[str] = []
        self.revealed: List[Tuple[str, str, int]] = []
        self.scans: List[Tuple[str, str]] = []

    def record_scan(self, *args: object) -> None:
        """Non utilisé."""
        del args

    def record_registration(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_qualified(self, product_id: str) -> None:
        """Non utilisé."""
        del product_id

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Non utilisé."""
        del child_id, parent_id, relationship_kind

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Non utilisé."""
        del child_id, previous_parent_id

    def record_product_opened(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self.opened.append(product_id)

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Non utilisé."""
        self.revealed.append((product_id, external_card_id, sequence_in_opening))

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Non utilisé."""
        self.scans.append((product_id, scan_payload))


def _booster(status: ProductStatus = ProductStatus.SEALED) -> ProductInstance:
    return ProductInstance(
        InternalProductId("b1"),
        ProductType.PLAY_BOOSTER,
        MtgSetCode("MH3"),
        status,
    )


class TestOpenSealedProductUseCase:
    """Ouverture nominale et rejets."""

    def test_opens_sealed_product_once(self) -> None:
        """Transition sealed → opened."""
        repo = _Repo()
        inst = _booster()
        repo.save(inst)
        events = _Events()
        uc = OpenSealedProductUseCase(inst.internal_id, repo, events)
        out = uc.execute()
        assert out.updated_product.status is ProductStatus.OPENED
        assert out.opening_event.previous_status is ProductStatus.SEALED
        assert repo.find_by_id(inst.internal_id) is not None
        assert repo.find_by_id(inst.internal_id).status is ProductStatus.OPENED
        assert events.opened == ["b1"]

    def test_second_open_raises(self) -> None:
        """Une seule ouverture métier."""
        repo = _Repo()
        inst = _booster(ProductStatus.OPENED)
        repo.save(inst)
        with pytest.raises(ProductAlreadyOpenedError):
            OpenSealedProductUseCase(inst.internal_id, repo, _Events()).execute()

    def test_unknown_product(self) -> None:
        """Identifiant absent."""
        with pytest.raises(ProductNotFoundForWorkflowError):
            OpenSealedProductUseCase(
                InternalProductId("ghost"),
                _Repo(),
                _Events(),
            ).execute()

    def test_display_not_openable(self) -> None:
        """Type display."""
        repo = _Repo()
        d = ProductInstance(
            InternalProductId("d1"),
            ProductType.DISPLAY,
            MtgSetCode("MH3"),
            ProductStatus.SEALED,
        )
        repo.save(d)
        with pytest.raises(ProductNotOpenableError):
            OpenSealedProductUseCase(d.internal_id, repo, _Events()).execute()

    def test_registered_not_ready(self) -> None:
        """Statut registered."""
        repo = _Repo()
        p = _booster(ProductStatus.REGISTERED)
        repo.save(p)
        with pytest.raises(ProductNotReadyForOpeningError):
            OpenSealedProductUseCase(p.internal_id, repo, _Events()).execute()
