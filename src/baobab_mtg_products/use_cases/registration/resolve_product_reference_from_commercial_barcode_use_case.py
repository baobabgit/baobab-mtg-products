"""Cas d'usage : résoudre un EAN en référence catalogue sans créer d'instance."""

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.registration.commercial_reference_resolution_result import (
    CommercialReferenceResolutionResult,
)
from baobab_mtg_products.ports.barcode_resolution_port import BarcodeResolutionPort
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class ResolveProductReferenceFromCommercialBarcodeUseCase(
    UseCase[CommercialReferenceResolutionResult],
):
    """Expose la résolution EAN → référence distincte de la matérialisation d'un exemplaire.

    L'ambiguïté catalogue (plusieurs produits possibles) se traduit par une levée de
    ``AmbiguousBarcodeResolutionError`` depuis le port ``BarcodeResolutionPort``.

    :param barcode: Code-barres commercial scanné.
    :type barcode: CommercialBarcode
    :param reference_repository: Catalogue des références persistées.
    :type reference_repository: ProductReferenceRepositoryPort
    :param resolution: Référentiel de résolution (catalogue externe, ambiguïtés).
    :type resolution: BarcodeResolutionPort
    """

    def __init__(
        self,
        barcode: CommercialBarcode,
        reference_repository: ProductReferenceRepositoryPort,
        resolution: BarcodeResolutionPort,
    ) -> None:
        self._barcode = barcode
        self._reference_repository = reference_repository
        self._resolution = resolution

    def execute(self) -> CommercialReferenceResolutionResult:
        """Retourne la référence persistée ou le gabarit catalogue, sans persister d'instance.

        :return: Résolution typée (référentiel puis catalogue si besoin).
        :rtype: CommercialReferenceResolutionResult
        """
        from_repo = self._reference_repository.find_by_commercial_barcode(self._barcode)
        if from_repo is not None:
            return CommercialReferenceResolutionResult(
                reference_from_repository=from_repo,
                catalog_resolution=None,
            )
        catalog = self._resolution.resolve_commercial(self._barcode)
        return CommercialReferenceResolutionResult(
            reference_from_repository=None,
            catalog_resolution=catalog,
        )
