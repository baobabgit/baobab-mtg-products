"""Tests pour :class:`RegistrationScanOutcome`."""

from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)


class TestRegistrationScanOutcome:
    """Valeurs d'issue de scan : exhaustivité et unicité des chaînes."""

    def test_enum_string_values_stable(self) -> None:
        """Les issues exposées ont des valeurs sérialisables stables."""
        assert RegistrationScanOutcome.EXISTING_PRODUCT.value == "existing_product"
        assert RegistrationScanOutcome.NEW_KNOWN_FROM_CATALOG.value == "new_known_from_catalog"
        assert (
            RegistrationScanOutcome.NEW_PENDING_QUALIFICATION.value == "new_pending_qualification"
        )
        assert (
            RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE.value
            == "new_instance_shared_reference"
        )
        assert RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN.value == "internal_barcode_unknown"

    def test_all_members_have_distinct_values(self) -> None:
        """Aucune collision de valeur entre membres de l'énumération."""
        values = [member.value for member in RegistrationScanOutcome]
        assert len(values) == len(set(values))
