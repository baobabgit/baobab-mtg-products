"""Erreur lorsqu'un rattachement introduirait un cycle dans la hiérarchie."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class CircularProductParentageError(BaobabMtgProductsException):
    """Le futur enfant est déjà ancêtre du parent désigné (ou données incohérentes).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
