"""Erreur lorsque la charge utile d'un scan carte en ouverture est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidOpeningCardScanPayloadError(BaobabMtgProductsException):
    """Scan carte vide ou aberrant pour le journal d'ouverture.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
