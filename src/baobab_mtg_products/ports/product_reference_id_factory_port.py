"""Port de génération d'identifiants pour les références produit."""

from typing import Protocol

from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId


class ProductReferenceIdFactoryPort(Protocol):
    """Contrat pour produire des :class:`ProductReferenceId` uniques côté domaine."""

    def new_reference_id(self) -> ProductReferenceId:
        """Génère un nouvel identifiant pour une référence à créer.

        :return: Identifiant unique dans la couche de persistance visée.
        :rtype: ProductReferenceId
        """
        ...
