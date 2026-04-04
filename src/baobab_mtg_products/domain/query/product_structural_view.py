"""Vue agrégée produit + parent + enfants directs pour la consultation."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_mtg_products.domain.products.product_instance import ProductInstance


@dataclass(frozen=True, slots=True)
class ProductStructuralView:
    """Instantané structurel : instance cible, parent résolu, enfants directs.

    :param product: Produit demandé.
    :type product: ProductInstance
    :param parent: Parent effectif si ``product.parent_id`` est renseigné et résolu.
    :type parent: ProductInstance | None
    :param direct_children: Instances dont le ``parent_id`` vaut ``product.internal_id``.
    :type direct_children: tuple[ProductInstance, ...]
    """

    product: ProductInstance
    parent: ProductInstance | None
    direct_children: tuple[ProductInstance, ...]
