"""Tests pour :class:`RegistrationDefaults`."""

from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.registration_defaults import RegistrationDefaults


class TestRegistrationDefaults:
    """Valeurs réservées pour l'attente de qualification."""

    def test_placeholder_set_is_stable(self) -> None:
        """Le placeholder est un code de set valide deux lettres."""
        code = RegistrationDefaults.placeholder_set_code()
        assert code.value == "QQ"

    def test_unknown_type_is_other_sealed(self) -> None:
        """Le type par défaut est « autre scellé »."""
        assert RegistrationDefaults.unknown_product_type() is ProductType.OTHER_SEALED

    def test_is_placeholder_set_detects_qq(self) -> None:
        """Le helper reconnaît le marqueur réservé."""
        assert RegistrationDefaults.is_placeholder_set(MtgSetCode("QQ")) is True
        assert RegistrationDefaults.is_placeholder_set(MtgSetCode("MH3")) is False
