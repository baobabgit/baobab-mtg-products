"""Service : vue parent, produit et enfants directs."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.query.product_structural_view import ProductStructuralView
from baobab_mtg_products.exceptions.query.missing_referenced_parent_product_error import (
    MissingReferencedParentProductError,
)
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort


class GetProductStructuralViewService:
    """Assemble une vue structurelle cohérente à partir du dépôt.

    :param product_id: Produit central de la consultation.
    :type product_id: InternalProductId
    :param repository: Persistance des instances (parent / enfants résolus ici).
    :type repository: ProductRepositoryPort
    :raises ProductNotFoundForQueryError: si le produit central est absent.
    :raises MissingReferencedParentProductError: si ``parent_id`` est défini mais orphelin.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        repository: ProductRepositoryPort,
    ) -> None:
        self._product_id = product_id
        self._repository = repository

    def load(self) -> ProductStructuralView:
        """Construit la vue à partir des lectures dépôt.

        :return: Produit, parent éventuel et enfants directs.
        :rtype: ProductStructuralView
        """
        product = self._repository.find_by_id(self._product_id)
        if product is None:
            raise ProductNotFoundForQueryError(
                "Aucun produit ne correspond à l'identifiant demandé pour la vue structurelle.",
            )
        parent = None
        if product.parent_id is not None:
            parent = self._repository.find_by_id(product.parent_id)
            if parent is None:
                raise MissingReferencedParentProductError(
                    "Le parent référencé par ce produit est absent du dépôt.",
                )
        children = self._repository.list_direct_children_of_parent(product.internal_id)
        return ProductStructuralView(
            product=product,
            parent=parent,
            direct_children=children,
        )
