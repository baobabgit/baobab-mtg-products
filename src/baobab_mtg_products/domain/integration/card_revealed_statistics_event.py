"""Message métier pour les statistiques lors de la révélation d'une carte."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CardRevealedStatisticsEvent:
    """Révélation issue d'un produit ouvert (hors possession globale).

    :param source_product_id: Produit ouvert source.
    :type source_product_id: str
    :param external_card_id: Identifiant carte côté intégration.
    :type external_card_id: str
    :param sequence_in_opening: Rang dans la session d'ouverture.
    :type sequence_in_opening: int
    """

    source_product_id: str
    external_card_id: str
    sequence_in_opening: int
