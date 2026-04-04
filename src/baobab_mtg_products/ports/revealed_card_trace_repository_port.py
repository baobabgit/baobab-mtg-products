"""Port de persistance des traces carte ↔ produit ouvert."""

from typing import Protocol

from baobab_mtg_products.domain.opening.external_card_id import ExternalCardId
from baobab_mtg_products.domain.opening.revealed_card_trace import RevealedCardTrace
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId


class RevealedCardTraceRepositoryPort(Protocol):
    """Contrat append-only pour la provenance des cartes révélées."""

    def count_traces_for_product(self, product_id: InternalProductId) -> int:
        """Nombre de cartes déjà tracées pour ce produit ouvert.

        :param product_id: Source de provenance.
        :type product_id: InternalProductId
        :return: Cardinal actuel (prochain index = cette valeur).
        :rtype: int
        """
        ...

    def has_trace_for_product_and_card(
        self,
        product_id: InternalProductId,
        external_card_id: ExternalCardId,
    ) -> bool:
        """Indique si la paire produit + carte est déjà enregistrée.

        :param product_id: Produit ouvert source.
        :type product_id: InternalProductId
        :param external_card_id: Identifiant carte externe.
        :type external_card_id: ExternalCardId
        :return: ``True`` si doublon métier.
        :rtype: bool
        """
        ...

    def append_trace(self, trace: RevealedCardTrace) -> None:
        """Enregistre une nouvelle trace (idempotent côté domaine via doublons refusés amont).

        :param trace: Lien produit ouvert → carte.
        :type trace: RevealedCardTrace
        """
        ...
