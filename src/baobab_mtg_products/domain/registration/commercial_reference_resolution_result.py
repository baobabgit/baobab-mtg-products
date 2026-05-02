"""Résultat explicite d'une résolution EAN → référence catalogue (sans instance)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan


@dataclass(frozen=True, slots=True)
class CommercialReferenceResolutionResult:
    """Données retournées par la résolution d'un code-barres commercial.

    Au plus une des deux sources est renseignée : soit une référence déjà persistée
    en dépôt catalogue, soit un gabarit issu du port de résolution (catalogue externe).

    :param reference_from_repository: Référence trouvée par code commercial en persistance.
    :type reference_from_repository: ProductReference | None
    :param catalog_resolution: Résolution catalogue lorsqu'aucune référence persistée ne correspond.
    :type catalog_resolution: ResolvedFromScan | None
    """

    reference_from_repository: Optional[ProductReference] = None
    catalog_resolution: Optional[ResolvedFromScan] = None

    @property
    def has_persistent_reference(self) -> bool:
        """Indique si une :class:`ProductReference` est déjà stockée pour cet EAN.

        :return: ``True`` lorsque :attr:`reference_from_repository` est renseignée.
        :rtype: bool
        """
        return self.reference_from_repository is not None
