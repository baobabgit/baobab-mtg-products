"""Port vers un référentiel résolvant un scan en gabarit produit."""

from typing import Protocol

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan


class BarcodeResolutionPort(Protocol):
    """Contrat pour traduire un code-barres en type / set issus du catalogue.

    En cas d'ambiguïté (plusieurs produits distincts possibles), l'implémentation
    doit lever :class:`AmbiguousBarcodeResolutionError`.
    """

    def resolve_commercial(self, barcode: CommercialBarcode) -> ResolvedFromScan:
        """Résout un code-barres commercial.

        :param barcode: Code scanné sur le conditionnement.
        :type barcode: CommercialBarcode
        :return: Résolution partielle ou complète.
        :rtype: ResolvedFromScan
        """
        ...

    def resolve_internal(self, barcode: InternalBarcode) -> ResolvedFromScan:
        """Résout un code-barres ou identifiant interne.

        :param barcode: Piste interne logistique.
        :type barcode: InternalBarcode
        :return: Résolution partielle ou complète.
        :rtype: ResolvedFromScan
        """
        ...
