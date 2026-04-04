"""Référence parent absente du dépôt alors qu'un enfant y pointe."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class MissingReferencedParentProductError(BaobabMtgProductsException):
    """Le produit porte un ``parent_id`` mais le parent n'existe pas dans le dépôt.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
