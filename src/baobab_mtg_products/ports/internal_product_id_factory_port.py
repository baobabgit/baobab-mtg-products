"""Port de génération d'identifiants internes uniques."""

from typing import Protocol

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId


class InternalProductIdFactoryPort(Protocol):
    """Contrat pour produire des :class:`InternalProductId` uniques côté domaine."""

    def new_product_id(self) -> InternalProductId:
        """Génère un nouvel identifiant pour une instance à créer.

        :return: Identifiant unique dans la couche de persistance visée.
        :rtype: InternalProductId
        """
        ...
