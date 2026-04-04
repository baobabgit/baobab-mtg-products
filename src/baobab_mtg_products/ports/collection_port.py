"""Port vers une brique de collection (intégration future, sans implémentation)."""

from typing import Protocol


class CollectionPort(Protocol):
    """Contrat minimal pour notifier la collection des faits métier pertinents.

    Ce :class:`typing.Protocol` évite tout couplage à une API ou un framework ;
    les adaptateurs concrets seront fournis par les applications hôtes.

    :param product_id: Identifiant interne du produit concerné.
    :type product_id: str
    """

    def notify_product_registered(self, product_id: str) -> None:
        """Signale qu'un produit a été enregistré pour la première fois.

        :param product_id: Identifiant du produit enregistré.
        :type product_id: str
        """
        ...
