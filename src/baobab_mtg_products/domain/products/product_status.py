"""Énumération des statuts métier d'une instance de produit scellé."""

from enum import Enum


class ProductStatus(str, Enum):
    """État du cycle de vie connu au moment de la modélisation de référence.

    Les workflows détaillés (scan, rattachement, déconditionnement) viendront enrichir les
    transitions ; ces valeurs restent stables pour qualifier une instance.

    ``DECONDITIONED`` : contenant dont les sous-produits physiques ont été sortis
    (distinct de l'ouverture d'un booster pour révélation de cartes).
    """

    REGISTERED = "registered"
    QUALIFIED = "qualified"
    SEALED = "sealed"
    OPENED = "opened"
    DECONDITIONED = "deconditioned"
