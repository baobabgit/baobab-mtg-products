"""Message métier pour les statistiques lors de l'ouverture d'un scellé."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SealedProductOpenedStatisticsEvent:
    """Charge utile stable pour agréger les ouvertures.

    :param product_id: Identifiant interne du produit ouvert.
    :type product_id: str
    :param previous_status_value: Statut immédiatement avant ouverture.
    :type previous_status_value: str
    :param product_type_value: Type de produit au moment de l'ouverture.
    :type product_type_value: str
    :param set_code_value: Code de set au moment de l'ouverture.
    :type set_code_value: str
    """

    product_id: str
    previous_status_value: str
    product_type_value: str
    set_code_value: str
