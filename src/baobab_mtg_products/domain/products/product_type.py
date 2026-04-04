"""Énumération des types de produits scellés couverts par le périmètre minimal."""

from enum import Enum


class ProductType(str, Enum):
    """Catégorie métier d'un produit scellé Magic: The Gathering.

    Couverture minimale alignée sur le cahier des charges (display, boosters,
    bundle, prerelease, etc.) avec une valeur générique pour les autres formats
    scellés du périmètre.
    """

    DISPLAY = "display"
    PLAY_BOOSTER = "play_booster"
    COLLECTOR_BOOSTER = "collector_booster"
    DRAFT_BOOSTER = "draft_booster"
    SET_BOOSTER = "set_booster"
    BUNDLE = "bundle"
    PRERELEASE_KIT = "prerelease_kit"
    COMMANDER_DECK = "commander_deck"
    OTHER_SEALED = "other_sealed"
