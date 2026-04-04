"""Tests pour :class:`SealedProductOpeningRules`."""

import pytest

from baobab_mtg_products.domain.opening.sealed_product_opening_rules import (
    SealedProductOpeningRules,
)
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


def _inst(
    pid: str,
    ptype: ProductType,
    status: ProductStatus,
) -> ProductInstance:
    return ProductInstance(
        InternalProductId(pid),
        ptype,
        MtgSetCode("TS"),
        status,
    )


class TestSealedProductOpeningRules:
    """Règles d'éligibilité."""

    def test_sealed_booster_ok(self) -> None:
        """Booster scellé ouvrable."""
        SealedProductOpeningRules.assert_product_may_be_opened(
            _inst("b", ProductType.PLAY_BOOSTER, ProductStatus.SEALED),
        )

    def test_qualified_ok(self) -> None:
        """Qualifié équivalent scellé pour ouverture."""
        SealedProductOpeningRules.assert_product_may_be_opened(
            _inst("b", ProductType.SET_BOOSTER, ProductStatus.QUALIFIED),
        )

    def test_opened_rejected(self) -> None:
        """Pas de double ouverture."""
        with pytest.raises(ProductAlreadyOpenedError):
            SealedProductOpeningRules.assert_product_may_be_opened(
                _inst("b", ProductType.PLAY_BOOSTER, ProductStatus.OPENED),
            )

    def test_registered_rejected(self) -> None:
        """Enregistré non qualifié."""
        with pytest.raises(ProductNotReadyForOpeningError):
            SealedProductOpeningRules.assert_product_may_be_opened(
                _inst("b", ProductType.PLAY_BOOSTER, ProductStatus.REGISTERED),
            )

    def test_display_rejected(self) -> None:
        """Display non ouvrable."""
        with pytest.raises(ProductNotOpenableError):
            SealedProductOpeningRules.assert_product_may_be_opened(
                _inst("d", ProductType.DISPLAY, ProductStatus.SEALED),
            )
