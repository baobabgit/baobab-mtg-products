"""Tests pour :class:`OpeningCardScanPayload`."""

import pytest

from baobab_mtg_products.domain.opening.opening_card_scan_payload import OpeningCardScanPayload
from baobab_mtg_products.exceptions.opening.invalid_opening_card_scan_payload_error import (
    InvalidOpeningCardScanPayloadError,
)


class TestOpeningCardScanPayload:
    """Charge utile de scan en ouverture."""

    def test_accepts_non_empty(self) -> None:
        """Valeur minimale valide."""
        p = OpeningCardScanPayload("uuid-or-raw-scan")
        assert p.value == "uuid-or-raw-scan"

    def test_rejects_blank(self) -> None:
        """Scan vide."""
        with pytest.raises(InvalidOpeningCardScanPayloadError):
            OpeningCardScanPayload(" \t ")

    def test_rejects_too_long(self) -> None:
        """Limite de longueur."""
        with pytest.raises(InvalidOpeningCardScanPayloadError):
            OpeningCardScanPayload("z" * 4097)
