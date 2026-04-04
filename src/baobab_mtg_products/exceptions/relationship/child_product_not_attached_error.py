"""Erreur lors d'un détachement alors que l'enfant n'a pas de parent."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ChildProductNotAttachedError(BaobabMtgProductsException):
    """Impossible de détacher : l'instance n'est rattachée à aucun parent.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
