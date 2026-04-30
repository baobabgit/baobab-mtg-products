"""Vue agrégée produit + parent + enfants directs pour la consultation."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference


@dataclass(frozen=True, slots=True)
class ProductStructuralView:
    """Instantané structurel : instances et références résolues pour la hiérarchie.

    :param product: Produit demandé.
    :type product: ProductInstance
    :param product_reference: Référence catalogue du produit central.
    :type product_reference: ProductReference
    :param parent: Parent effectif si ``product.parent_id`` est renseigné et résolu.
    :type parent: ProductInstance | None
    :param parent_reference: Référence du parent, si ``parent`` est présent.
    :type parent_reference: ProductReference | None
    :param direct_children: Instances dont le ``parent_id`` vaut ``product.internal_id``.
    :type direct_children: tuple[ProductInstance, ...]
    :param child_references: Références alignées sur ``direct_children`` (même ordre).
    :type child_references: tuple[ProductReference, ...]
    """

    product: ProductInstance
    product_reference: ProductReference
    parent: ProductInstance | None
    parent_reference: ProductReference | None
    direct_children: tuple[ProductInstance, ...]
    child_references: tuple[ProductReference, ...]
