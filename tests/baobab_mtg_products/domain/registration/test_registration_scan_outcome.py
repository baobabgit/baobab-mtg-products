"""Tests pour :class:`RegistrationScanOutcome`."""

from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)


class TestRegistrationScanOutcome:
    """Valeurs d'issue de scan."""

    def test_enum_values(self) -> None:
        """Les trois issues principales sont définies."""
        assert RegistrationScanOutcome.EXISTING_PRODUCT.value == "existing_product"
        assert RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG.value == "new_known_from_catalog"
        assert (
            RegistrationScanOutcome.NEW_PENDING_QUALIFICATION.value == "new_pending_qualification"
        )
