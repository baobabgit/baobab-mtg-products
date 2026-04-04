"""Instantané de provenance produit pour synchronisation avec la collection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.domain.products.product_instance import ProductInstance


@dataclass(frozen=True, slots=True)
class ProductProvenanceForCollection:
    """Données minimales pour refléter un scellé dans une brique collection.

    :param internal_product_id: Identifiant interne stable.
    :type internal_product_id: str
    :param product_type_value: Valeur d'énumération du type scellé.
    :type product_type_value: str
    :param set_code_value: Code d'extension (normalisé côté domaine).
    :type set_code_value: str
    :param product_status_value: Statut métier courant.
    :type product_status_value: str
    :param parent_product_id: Parent structurel, si présent.
    :type parent_product_id: str | None
    """

    internal_product_id: str
    product_type_value: str
    set_code_value: str
    product_status_value: str
    parent_product_id: Optional[str]

    @classmethod
    def from_product_instance(cls, instance: ProductInstance) -> ProductProvenanceForCollection:
        """Construit l'instantané à partir de l'agrégat persisté.

        :param instance: Source métier.
        :type instance: ProductInstance
        :return: DTO prêt pour le port collection.
        :rtype: ProductProvenanceForCollection
        """
        parent: Optional[str] = instance.parent_id.value if instance.parent_id is not None else None
        return cls(
            internal_product_id=instance.internal_id.value,
            product_type_value=instance.product_type.value,
            set_code_value=instance.set_code.value,
            product_status_value=instance.status.value,
            parent_product_id=parent,
        )
