"""Code de production ou de lot — identifiant métier non unique."""

from dataclasses import dataclass

from baobab_mtg_products.exceptions.product.invalid_production_code_error import (
    InvalidProductionCodeError,
)

_MAX_LEN = 128


@dataclass(frozen=True, slots=True)
class ProductionCode:
    """Value object pour un code de production / lot fabricant.

    Contrairement au :class:`~baobab_mtg_products.domain.products.serial_number.SerialNumber`
    (numéro de série souvent pensé comme piste qualité unitaire), le code de production
    identifie un **lot** ou une **vague** de fabrication : plusieurs instances physiques
    peuvent partager la même valeur sans ambiguïté sur l'identité de l'exemplaire, qui
    reste portée par
    :class:`~baobab_mtg_products.domain.products.internal_product_id.InternalProductId`.

    :param value: Code non vide après normalisation.
    :type value: str
    :raises InvalidProductionCodeError: si la valeur est vide ou trop longue.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidProductionCodeError(
                "Le code de production ne peut pas être vide lorsqu'il est fourni.",
            )
        if len(normalized) > _MAX_LEN:
            raise InvalidProductionCodeError(
                f"Le code de production dépasse {_MAX_LEN} caractères.",
            )
        object.__setattr__(self, "value", normalized)
