"""Erreur lorsqu'un événement métier viole l'ordre ou l'état attendu du journal."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class ProductHistoryCoherenceError(BaobabMtgProductsException):
    """Rejet d'append : prérequis manquant, doublon interdit ou lien parent incohérent.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
