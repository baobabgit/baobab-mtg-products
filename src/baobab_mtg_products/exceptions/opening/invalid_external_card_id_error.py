"""Erreur lorsque l'identifiant externe d'une carte est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidExternalCardIdError(BaobabMtgProductsException):
    """Valeur d'identifiant carte externe refusée (vide, trop longue, etc.).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
