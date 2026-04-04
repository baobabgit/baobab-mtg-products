"""Port vers une brique de statistiques (intégration future, sans implémentation)."""

from typing import Any, Mapping, Protocol


class StatisticsPort(Protocol):
    """Contrat minimal pour transmettre des événements au moteur statistique.

    La charge utile reste générique (:class:`typing.Mapping`) pour ne pas
    figer le modèle d'événements tant que le domaine n'est pas implémenté.

    :param event_type: Nom ou code d'événement métier.
    :type event_type: str
    :param payload: Données structurées associées à l'événement.
    :type payload: Mapping[str, Any]
    """

    def record_opening_event(
        self,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> None:
        """Enregistre un événement lié à une ouverture ou à la traçabilité.

        :param event_type: Type d'événement (ex. ``'product_opened'``).
        :type event_type: str
        :param payload: Contenu sérialisable de l'événement.
        :type payload: Mapping[str, Any]
        """
        ...
