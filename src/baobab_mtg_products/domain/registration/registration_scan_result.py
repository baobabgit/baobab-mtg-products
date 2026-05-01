"""Couple produit / issue après un scan d'enregistrement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)


@dataclass(frozen=True, slots=True)
class RegistrationScanResult:
    """Résultat typé d'un cas d'usage de scan + persistance ou résolution seule.

    Pour un scan **interne** sans instance enregistrée, :attr:`product` vaut ``None``
    et :attr:`outcome` est :attr:`RegistrationScanOutcome.INTERNAL_BARCODE_UNKNOWN`.

    Après un scan **commercial** ayant abouti à une instance, :attr:`resolved_reference`
    peut renseigner la référence catalogue utilisée (réutilisée ou créée).

    :param product: Instance persistée ou retrouvée, ou ``None`` si inconnu interne.
    :type product: ProductInstance | None
    :param outcome: Nature du résultat (existant, nouveau qualifié, à qualifier, etc.).
    :type outcome: RegistrationScanOutcome
    :param resolved_reference: Référence catalogue alignée sur l'instance, si connue.
    :type resolved_reference: ProductReference | None
    """

    product: Optional[ProductInstance]
    outcome: RegistrationScanOutcome
    resolved_reference: Optional[ProductReference] = None
