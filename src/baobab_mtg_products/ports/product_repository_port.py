"""Port de persistance des instances produit."""

from typing import Optional, Protocol

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance


class ProductRepositoryPort(Protocol):
    """Contrat minimal pour stocker et retrouver des :class:`ProductInstance`."""

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Retourne le produit par identifiant interne.

        :param product_id: Clé métier stable.
        :type product_id: InternalProductId
        :return: Instance si présente, sinon ``None``.
        :rtype: ProductInstance | None
        """
        ...

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Retourne le produit déjà enregistré pour ce code interne.

        :param barcode: Code-barres interne normalisé.
        :type barcode: InternalBarcode
        :return: Instance si trouvée, sinon ``None``.
        :rtype: ProductInstance | None
        """
        ...

    def list_direct_children_of_parent(
        self,
        parent_id: InternalProductId,
    ) -> tuple[ProductInstance, ...]:
        """Retourne les instances dont ``parent_id`` pointe vers ce parent.

        L'ordre des éléments doit être stable pour des jeux de tests reproductibles
        (ex. tri par identifiant interne).

        :param parent_id: Identifiant du parent structurel.
        :type parent_id: InternalProductId
        :return: Enfants directs uniquement (pas les descendants).
        :rtype: tuple[ProductInstance, ...]
        """
        ...

    def save(self, product: ProductInstance) -> None:
        """Enregistre ou remplace une instance.

        :param product: Agrégat à persister.
        :type product: ProductInstance
        """
        ...
