"""Erreur de workflow lorsque la référence attendue pour une instance est introuvable."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductReferenceNotFoundForWorkflowError(BaobabMtgProductsException):
    """Levée lorsqu'une opération métier nécessite la référence produit persistée absente.

    :param message: Détail lisible pour l'appelant.
    :type message: str
    """
