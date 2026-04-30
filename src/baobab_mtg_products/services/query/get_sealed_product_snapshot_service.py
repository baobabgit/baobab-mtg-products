"""Service : obtenir l'instance produit et sa référence par identifiant interne."""

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.query.sealed_product_snapshot import SealedProductSnapshot
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


class GetSealedProductSnapshotService:
    """Consultation nominale d'un scellé persisté avec sa référence catalogue.

    :param product_id: Identifiant interne cible.
    :type product_id: InternalProductId
    :param repository: Source de vérité des instances physiques.
    :type repository: ProductRepositoryPort
    :param reference_repository: Source de vérité des références catalogue.
    :type reference_repository: ProductReferenceRepositoryPort
    :raises ProductNotFoundForQueryError: si l'identifiant instance est inconnu du dépôt.
    :raises ProductReferenceNotFoundForQueryError: si la référence liée est orpheline.
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

    def load(self) -> SealedProductSnapshot:
        """Retourne l'instance et la référence alignées.

        :return: Instantané produit + référence.
        :rtype: SealedProductSnapshot
        """
        found = self._repository.find_by_id(self._product_id)
        if found is None:
            raise ProductNotFoundForQueryError(
                "Aucun produit ne correspond à l'identifiant demandé pour consultation.",
            )
        reference = self._reference_repository.find_by_id(found.reference_id)
        if reference is None:
            raise ProductReferenceNotFoundForQueryError(
                "La référence catalogue associée à ce produit est introuvable.",
            )
        return SealedProductSnapshot(product=found, reference=reference)
