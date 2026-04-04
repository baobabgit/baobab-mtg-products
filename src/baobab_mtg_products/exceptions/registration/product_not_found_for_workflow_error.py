"""Erreur lorsqu'un identifiant attendu n'existe pas dans le dépôt."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductNotFoundForWorkflowError(BaobabMtgProductsException):
    """Produit introuvable pour poursuivre un cas d'usage (qualification, etc.).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
