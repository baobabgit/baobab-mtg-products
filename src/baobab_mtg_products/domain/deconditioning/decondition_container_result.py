"""Résultat explicite du déconditionnement d'un contenant."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_mtg_products.domain.products.product_instance import ProductInstance


@dataclass(frozen=True, slots=True)
class DeconditionContainerResult:
    """Contenant mis à jour et exemplaires enfants tels que persistés après l'opération.

    :param container: Instance du contenant avec statut :attr:`~ProductStatus.DECONDITIONED`.
    :type container: ProductInstance
    :param children: Enfants créés ou rattachés, dans l'ordre de traitement de la commande.
    :type children: tuple[ProductInstance, ...]
    """

    container: ProductInstance
    children: tuple[ProductInstance, ...]
