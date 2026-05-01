"""Service : vue parent, produit et enfants directs avec références catalogue."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.query.product_structural_view import ProductStructuralView
from baobab_mtg_products.exceptions.query.missing_referenced_parent_product_error import (
    MissingReferencedParentProductError,
)
from baobab_mtg_products.exceptions.query.product_not_found_for_query_error import (
    ProductNotFoundForQueryError,
)
from baobab_mtg_products.exceptions.query.product_reference_not_found_for_query_error import (
    ProductReferenceNotFoundForQueryError,
)
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort


class GetProductStructuralViewService:
    """Assemble une vue structurelle cohérente à partir des dépôts instance et référence.

    :param product_id: Produit central de la consultation.
    :type product_id: InternalProductId
    :param repository: Persistance des instances (parent / enfants résolus ici).
    :type repository: ProductRepositoryPort
    :param reference_repository: Persistance des références catalogue.
    :type reference_repository: ProductReferenceRepositoryPort
    :raises ProductNotFoundForQueryError: si le produit central est absent.
    :raises MissingReferencedParentProductError: si ``parent_id`` est défini mais orphelin.
    :raises ProductReferenceNotFoundForQueryError: si une référence attendue est absente.
    """

    def __init__(
        self,
        product_id: InternalProductId,
        repository: ProductRepositoryPort,
        reference_repository: ProductReferenceRepositoryPort,
    ) -> None:
        self._product_id = product_id
        self._repository = repository
        self._reference_repository = reference_repository

    def _require_reference(self, instance: ProductInstance) -> ProductReference:
        reference = self._reference_repository.find_by_id(instance.reference_id)
        if reference is None:
            raise ProductReferenceNotFoundForQueryError(
                "Une référence catalogue attendue pour cette instance est introuvable.",
            )
        return reference

    def load(self) -> ProductStructuralView:
        """Construit la vue à partir des lectures dépôt.

        :return: Produits, références, parent éventuel et enfants directs.
        :rtype: ProductStructuralView
        """
        product = self._repository.find_by_id(self._product_id)
        if product is None:
            raise ProductNotFoundForQueryError(
                "Aucun produit ne correspond à l'identifiant demandé pour la vue structurelle.",
            )
        product_reference = self._require_reference(product)
        parent = None
        parent_reference = None
        if product.parent_id is not None:
            parent = self._repository.find_by_id(product.parent_id)
            if parent is None:
                raise MissingReferencedParentProductError(
                    "Le parent référencé par ce produit est absent du dépôt.",
                )
            parent_reference = self._require_reference(parent)
        children = self._repository.list_direct_children_of_parent(product.internal_id)
        child_refs = tuple(self._require_reference(child) for child in children)
        return ProductStructuralView(
            product=product,
            product_reference=product_reference,
            parent=parent,
            parent_reference=parent_reference,
            direct_children=children,
            child_references=child_refs,
        )
