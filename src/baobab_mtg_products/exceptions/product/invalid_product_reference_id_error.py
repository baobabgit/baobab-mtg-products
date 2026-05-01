"""Erreur lorsque l'identifiant de référence produit est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductReferenceIdError(BaobabMtgProductsException):
    """Levée lorsque la valeur d'un identifiant de référence produit est rejetée.

    :param message: Détail lisible de la violation d'invariant.
    :type message: str
    """
