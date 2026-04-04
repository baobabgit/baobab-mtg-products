"""Message métier pour les statistiques lors d'un scan de carte en ouverture."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpeningCardScanStatisticsEvent:
    """Scan brut ou normalisé pendant la session post-ouverture.

    :param product_id: Produit ouvert concerné.
    :type product_id: str
    :param scan_payload: Valeur auditée (opaque pour la lib).
    :type scan_payload: str
    """

    product_id: str
    scan_payload: str
