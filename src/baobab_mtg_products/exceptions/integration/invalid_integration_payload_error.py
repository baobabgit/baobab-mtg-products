"""Erreur lorsque un message d'intégration collection / statistiques est incomplet."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidIntegrationPayloadError(BaobabMtgProductsException):
    """Champs obligatoires manquants pour un DTO d'intégration (ex. lien parent).

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
