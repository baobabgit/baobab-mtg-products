"""Erreur lorsque les types de produit ne correspondent pas au kind de relation."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class IncompatibleParentChildTypesError(BaobabMtgProductsException):
    """Combinaison parent/enfant interdite pour le type de rattachement choisi.

    :param message: Détail lisible pour l'opérateur ou les logs.
    :type message: str
    """
