"""Couple produit / issue après un scan d'enregistrement."""

from dataclasses import dataclass

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)


@dataclass(frozen=True, slots=True)
class RegistrationScanResult:
    """Résultat typé d'un cas d'usage de scan + persistance.

    :param product: Instance telle que persistée ou retrouvée.
    :type product: ProductInstance
    :param outcome: Nature du résultat (existant, nouveau qualifié, à qualifier).
    :type outcome: RegistrationScanOutcome
    """

    product: ProductInstance
    outcome: RegistrationScanOutcome
