"""Service : obtenir l'instance produit courante par identifiant interne."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort


class GetSealedProductSnapshotService:
    """Consultation nominale d'un scellé persisté (pas de mutation).

    :param product_id: Identifiant interne cible.
    :type product_id: InternalProductId
    :param repository: Source de vérité des instances.
    :type repository: ProductRepositoryPort
    :raises ProductNotFoundForQueryError: si l'identifiant est inconnu du dépôt.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        repository: ProductRepositoryPort,
    ) -> None:
        self._product_id = product_id
        self._repository = repository

    def load(self) -> ProductInstance:
        """Retourne l'agrégat tel que stocké.

        :return: Instance produit.
        :rtype: ProductInstance
        """
        found = self._repository.find_by_id(self._product_id)
        if found is None:
            raise ProductNotFoundForQueryError(
                "Aucun produit ne correspond à l'identifiant demandé pour consultation.",
            )
        return found
