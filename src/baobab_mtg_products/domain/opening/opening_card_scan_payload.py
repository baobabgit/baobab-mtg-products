"""Charge utile brute d'un scan de carte pendant une session d'ouverture."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.opening.invalid_opening_card_scan_payload_error import (
    InvalidOpeningCardScanPayloadError,
)

_MAX_LEN = 4096


@dataclass(frozen=True, slots=True)
class OpeningCardScanPayload:
    """Valeur auditée passée au journal d'événements (contenu scanner / OCR, etc.).

    :param value: Texte non vide après normalisation.
    :type value: str
    :raises InvalidOpeningCardScanPayloadError: si vide ou trop long.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidOpeningCardScanPayloadError(
                "La charge utile de scan carte en ouverture ne peut pas être vide.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidOpeningCardScanPayloadError(
                f"La charge utile de scan dépasse la longueur maximale ({_MAX_LEN}).",
            )
        object.__setattr__(self, "value", normalized)
