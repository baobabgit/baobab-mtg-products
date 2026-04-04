"""Nature métier d'un rattachement parent → enfant."""

from enum import Enum


class ProductRelationshipKind(str, Enum):
    """Catégorie de lien structurel entre deux instances scellées.

    Précise la règle de compatibilité appliquée lors du rattachement
    (display / bundle / lien générique).
    """

    DISPLAY_CONTAINS_BOOSTER = "display_contains_booster"
    BUNDLE_CONTAINS_SUBPRODUCT = "bundle_contains_subproduct"
    GENERIC_STRUCTURAL_ATTACHMENT = "generic_structural_attachment"
