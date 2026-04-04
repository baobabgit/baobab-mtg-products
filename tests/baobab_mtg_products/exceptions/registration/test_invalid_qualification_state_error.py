"""Tests pour InvalidQualificationStateError."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.registration.invalid_qualification_state_error import (
    InvalidQualificationStateError,
)


class TestInvalidQualificationStateError:
    """Hiérarchie d'exception."""

    def test_inherits_base(self) -> None:
        """Extension de l'exception racine métier."""
        assert issubclass(InvalidQualificationStateError, BaobabMtgProductsException)
