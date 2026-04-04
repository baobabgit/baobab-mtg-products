"""Tests pour :class:`RevealedCardTrace`."""

import pytest

from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.domain.opening.revealed_card_trace import RevealedCardTrace
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.exceptions.opening.invalid_revealed_card_sequence_error import (
    InvalidRevealedCardSequenceError,
)


class TestRevealedCardTrace:
    """Provenance carte ↔ produit ouvert."""

    def test_sequence_zero_ok(self) -> None:
        """Première carte."""
        t = RevealedCardTrace(
            InternalProductId("b"),
            ExternalCardId("c1"),
            0,
        )
        assert t.sequence_in_opening == 0

    def test_negative_sequence_rejected(self) -> None:
        """Séquence invalide."""
        with pytest.raises(InvalidRevealedCardSequenceError):
            RevealedCardTrace(
                InternalProductId("b"),
                ExternalCardId("c1"),
                -1,
            )
