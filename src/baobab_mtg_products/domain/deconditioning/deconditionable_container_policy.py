"""Politique des types d'instances pouvant être déconditionnés comme contenants."""

from __future__ import annotations

from typing import FrozenSet

from baobab_mtg_products.domain.products.product_type import ProductType


class DeconditionableContainerPolicy:
    """Indique si une instance peut être la cible du flux :class:`DeconditionContainerUseCase`.

    Les boosters et formats assimilés ne sont pas des contenants au sens déconditionnement
    (distinct de l'ouverture pour cartes).
    """

    _DECONDITIONABLE: FrozenSet[ProductType] = frozenset(
        {
            ProductType.DISPLAY,
            ProductType.BUNDLE,
            ProductType.PRERELEASE_KIT,
            ProductType.COMMANDER_DECK,
            ProductType.OTHER_SEALED,
        },
    )

    @classmethod
    def is_deconditionable_container(cls, product_type: ProductType) -> bool:
        """Retourne ``True`` si le type peut être déconditionné (sortie de sous-produits).

        :param product_type: Type catalogue porté par l'instance contenant.
        :type product_type: ProductType
        :return: ``True`` lorsque le déconditionnement est autorisé pour ce type.
        :rtype: bool
        """
        return product_type in cls._DECONDITIONABLE
