"""Tests pour RegisterProductByInternalScanUseCase."""

from unittest.mock import MagicMock

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)
from baobab_mtg_products.use_cases.registration.register_product_by_internal_scan_use_case import (
    RegisterProductByInternalScanUseCase,
)


class TestRegisterProductByInternalScanUseCase:
    """Délégation vers le runner d'enregistrement."""

    def test_execute_forwards_to_runner(self) -> None:
        """Les paramètres sont transmis au runner injecté."""
        runner = MagicMock()
        expected = MagicMock(spec=RegistrationScanResult)
        runner.register_via_internal.return_value = expected
        barcode = InternalBarcode("int-1")
        use_case = RegisterProductByInternalScanUseCase(barcode, runner)
        assert use_case.execute() is expected
        runner.register_via_internal.assert_called_once_with(
            barcode,
            serial_number=None,
            set_code_override=None,
            product_type_override=None,
        )
