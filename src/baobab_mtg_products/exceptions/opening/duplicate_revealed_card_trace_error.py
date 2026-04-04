"""Erreur lorsqu'on enregistre deux fois la même carte pour un même produit ouvert."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class DuplicateRevealedCardTraceError(BaobabMtgProductsException):
    """La provenance produit + identifiant carte est déjà enregistrée.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
