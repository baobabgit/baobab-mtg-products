"""Erreur lorsque le couple parent/enfant d'une relation est invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidProductRelationshipLinkError(BaobabMtgProductsException):
    """Lien structurel refusé (ex. parent et enfant identiques).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
