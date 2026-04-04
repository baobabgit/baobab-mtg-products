"""Erreur lorsque l'état courant interdit la qualification."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidQualificationStateError(BaobabMtgProductsException):
    """Le statut ou le contexte du produit n'autorise pas la qualification.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
