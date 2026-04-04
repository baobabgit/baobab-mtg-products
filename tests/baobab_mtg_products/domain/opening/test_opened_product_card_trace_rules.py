"""Tests pour :class:`OpenedProductCardTraceRules`."""

import pytest

from baobab_mtg_products.domain.opening.opened_product_card_trace_rules import (
    OpenedProductCardTraceRules,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.opening.product_not_opened_for_card_trace_error import (
    ProductNotOpenedForCardTraceError,
)


def _inst(status: ProductStatus) -> ProductInstance:
    return ProductInstance(
        InternalProductId("p"),
        ProductType.DRAFT_BOOSTER,
        MtgSetCode("TS"),
        status,
    )


class TestOpenedProductCardTraceRules:
    """Accès aux traces carte."""

    def test_opened_ok(self) -> None:
        """Produit ouvert : traces autorisées."""
        OpenedProductCardTraceRules.assert_product_is_opened_for_card_tracing(
            _inst(ProductStatus.OPENED),
        )

    def test_sealed_rejected(self) -> None:
        """Pas de trace carte avant ouverture."""
        with pytest.raises(ProductNotOpenedForCardTraceError):
            OpenedProductCardTraceRules.assert_product_is_opened_for_card_tracing(
                _inst(ProductStatus.SEALED),
            )
