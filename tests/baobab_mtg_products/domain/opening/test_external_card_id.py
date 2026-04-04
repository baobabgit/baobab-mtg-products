"""Tests pour :class:`ExternalCardId`."""

import pytest

from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.exceptions.opening.invalid_external_card_id_error import (
    InvalidExternalCardIdError,
)


class TestExternalCardId:
    """Validation des identifiants carte externes."""

    def test_strips_and_stores(self) -> None:
        """Normalisation des espaces."""
        cid = ExternalCardId("  scryfall:abc  ")
        assert cid.value == "scryfall:abc"

    def test_rejects_empty(self) -> None:
        """Identifiant vide."""
        with pytest.raises(InvalidExternalCardIdError):
            ExternalCardId("   ")

    def test_rejects_too_long(self) -> None:
        """Limite de longueur."""
        with pytest.raises(InvalidExternalCardIdError):
            ExternalCardId("x" * 513)
