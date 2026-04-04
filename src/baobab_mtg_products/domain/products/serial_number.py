"""Numéro de série optionnel gravé ou imprimé sur le produit scellé."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_serial_number_error import (
    InvalidSerialNumberError,
)

_MAX_LEN = 128


@dataclass(frozen=True, slots=True)
class SerialNumber:
    """Value object pour un numéro de série fabricant / piste qualité.

    :param value: Numéro non vide après normalisation.
    :type value: str
    :raises InvalidSerialNumberError: si la valeur est vide ou trop longue.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidSerialNumberError(
                "Le numéro de série ne peut pas être vide lorsqu'il est fourni.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidSerialNumberError(
                f"Le numéro de série dépasse {_MAX_LEN} caractères.",
            )
        object.__setattr__(self, "value", normalized)
