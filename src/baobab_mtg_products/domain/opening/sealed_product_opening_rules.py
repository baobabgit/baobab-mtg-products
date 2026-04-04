"""Règles d'éligibilité à l'ouverture d'une instance scellée."""

from typing import FrozenSet

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.opening.product_already_opened_error import (
    ProductAlreadyOpenedError,
)
from baobab_mtg_products.exceptions.opening.product_not_openable_error import (
    ProductNotOpenableError,
)
from baobab_mtg_products.exceptions.opening.product_not_ready_for_opening_error import (
    ProductNotReadyForOpeningError,
)

_ALLOWED_PRE_OPEN_STATUSES: FrozenSet[ProductStatus] = frozenset(
    {
        ProductStatus.SEALED,
        ProductStatus.QUALIFIED,
    },
)


class SealedProductOpeningRules:
    """Vérifie type et statut avant de passer une instance à « opened »."""

    @staticmethod
    def assert_product_may_be_opened(instance: ProductInstance) -> None:
        """Lève une exception si l'ouverture est interdite.

        :param instance: Produit candidat à l'ouverture.
        :type instance: ProductInstance
        :raises ProductAlreadyOpenedError: si le statut est déjà ``opened``.
        :raises ProductNotReadyForOpeningError: si le statut n'est ni ``sealed`` ni ``qualified``.
        :raises ProductNotOpenableError: si le type ne peut pas être ouvert (ex. display).
        """
        if instance.status is ProductStatus.OPENED:
            raise ProductAlreadyOpenedError(
                "Ce produit est déjà ouvert.",
            )
        if instance.status not in _ALLOWED_PRE_OPEN_STATUSES:
            raise ProductNotReadyForOpeningError(
                "Seuls les produits « sealed » ou « qualified » peuvent être ouverts.",
            )
        if instance.product_type is ProductType.DISPLAY:
            raise ProductNotOpenableError(
                "Une display n'est pas ouverte comme unité scellée dans ce modèle.",
            )
