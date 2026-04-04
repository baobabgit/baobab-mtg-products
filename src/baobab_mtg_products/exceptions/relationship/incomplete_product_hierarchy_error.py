"""Erreur lorsque la chaîne des parents référence une instance absente du dépôt."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class IncompleteProductHierarchyError(BaobabMtgProductsException):
    """Hiérarchie incohérente : un ``parent_id`` ne peut pas être résolu.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
