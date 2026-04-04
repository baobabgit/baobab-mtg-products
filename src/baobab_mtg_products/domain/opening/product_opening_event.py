"""Événement métier décrivant l'ouverture réussie d'un produit scellé."""

from dataclasses import dataclass

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_status import ProductStatus


@dataclass(frozen=True, slots=True)
class ProductOpeningEvent:
    """Fait d'ouverture : produit source et statut immédiatement avant transition.

    :param source_product_id: Instance qui vient d'être passée à « opened ».
    :type source_product_id: InternalProductId
    :param previous_status: Statut métier avant ouverture (audit / rejeu).
    :type previous_status: ProductStatus
    """

    source_product_id: InternalProductId
    previous_status: ProductStatus
