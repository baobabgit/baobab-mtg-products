"""Tests pour le cas d'usage scan commercial."""

from unittest.mock import MagicMock

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)
from baobab_mtg_products.use_cases.registration import (
    RegisterProductByCommercialScanUseCase,
)


class TestRegisterProductByCommercialScanUseCase:
    """Délégation vers le runner d'enregistrement."""

    def test_commercial_use_case_delegates_to_runner(self) -> None:
        """Plan 11 §13 — délégation stricte au runner (pas de logique dupliquée)."""
        self.test_execute_forwards_to_runner()

    def test_execute_forwards_to_runner(self) -> None:
        """Les paramètres sont transmis au runner injecté."""
        runner = MagicMock()
        expected = MagicMock(spec=RegistrationScanResult)
        runner.register_via_commercial.return_value = expected
        barcode = CommercialBarcode("12345678")
        use_case = RegisterProductByCommercialScanUseCase(
            barcode,
            runner,
            set_code_override=MtgSetCode("MH3"),
            product_type_override=ProductType.BUNDLE,
        )
        assert use_case.execute() is expected
        runner.register_via_commercial.assert_called_once_with(
            barcode,
            serial_number=None,
            set_code_override=MtgSetCode("MH3"),
            product_type_override=ProductType.BUNDLE,
        )

    def test_execute_returns_runner_outcome(self) -> None:
        """Le résultat du runner est celui du cas d'usage."""
        runner = MagicMock()
        outcome = RegistrationScanOutcome.EXISTING_PRODUCT
        runner.register_via_commercial.return_value = RegistrationScanResult(
            MagicMock(),
            outcome,
        )
        use_case = RegisterProductByCommercialScanUseCase(
            CommercialBarcode("87654321"),
            runner,
        )
        assert use_case.execute().outcome is outcome
