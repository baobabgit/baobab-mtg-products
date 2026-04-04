"""Identifiant externe de carte (collection, API tierce, etc.), opaque pour le domaine."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.opening.invalid_external_card_id_error import (
    InvalidExternalCardIdError,
)

_MAX_LEN = 512


@dataclass(frozen=True, slots=True)
class ExternalCardId:
    """Référence stable fournie par l'adaptateur (hors périmètre possession globale).

    :param value: Identifiant non vide après normalisation.
    :type value: str
    :raises InvalidExternalCardIdError: si la valeur est vide ou trop longue.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidExternalCardIdError(
                "L'identifiant externe de carte ne peut pas être vide.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidExternalCardIdError(
                f"L'identifiant externe de carte dépasse la longueur maximale ({_MAX_LEN}).",
            )
        object.__setattr__(self, "value", normalized)
