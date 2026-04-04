"""Erreur lorsqu'on tente de rattacher un enfant déjà lié à un parent."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductAlreadyHasParentError(BaobabMtgProductsException):
    """L'enfant possède déjà une référence parente (champ ``parent_id`` renseigné).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
