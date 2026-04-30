"""Port de persistance des références produit commerciales."""

from typing import Optional, Protocol

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId


class ProductReferenceRepositoryPort(Protocol):
    """Contrat minimal pour stocker et retrouver des :class:`ProductReference`."""

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Retourne la référence par identifiant stable.

        :param reference_id: Clé métier de la référence.
        :type reference_id: ProductReferenceId
        :return: Référence si présente, sinon ``None``.
        :rtype: ProductReference | None
        """
        ...

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductReference]:
        """Retourne la référence déjà enregistrée pour ce code-barres commercial.

        :param barcode: Code-barres commercial normalisé.
        :type barcode: CommercialBarcode
        :return: Référence si trouvée, sinon ``None``.
        :rtype: ProductReference | None
        """
        ...

    def save(self, reference: ProductReference) -> None:
        """Enregistre ou remplace une référence.

        :param reference: Agrégat référence à persister.
        :type reference: ProductReference
        """
        ...
