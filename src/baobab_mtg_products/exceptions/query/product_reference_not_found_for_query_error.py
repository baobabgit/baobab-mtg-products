"""Erreur de consultation lorsque la référence liée à une instance est introuvable."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductReferenceNotFoundForQueryError(BaobabMtgProductsException):
    """Levée lorsqu'une instance référence un identifiant de référence absent du dépôt.

    :param message: Détail lisible pour l'appelant.
    :type message: str
    """
