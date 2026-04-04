"""Tests pour :class:`RegistrationScanResult`."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
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
