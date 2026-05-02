"""Erreur lorsque la spécification d'un enfant est ambiguë ou invalide."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)


class InvalidDeconditionChildSpecificationError(BaobabMtgProductsException):
    """Création depuis référence et rattachement d'une instance existante s'excluent."""
