"""Erreur lorsque le parent effectif ne correspond pas au parent attendu au détachement."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class DetachParentMismatchError(BaobabMtgProductsException):
    """Le parent courant de l'enfant diffère de l'identifiant explicitement attendu.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
