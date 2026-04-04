"""Erreur levée lorsque l'identifiant interne d'un produit est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductIdentifierError(BaobabMtgProductsException):
    """Identifiant interne de produit absent, vide ou hors limites après normalisation.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
