"""Implémentations mémoire conformes aux ports références et instances.

Doubles de test pour ``ProductReferenceRepositoryPort`` et ``ProductRepositoryPort``.
Pas d’adaptateur SQL de production.

Unicité (indicatif, comme une couche SQL) :

- ``internal_id`` : clé primaire ; ``save`` remplace l’exemplaire de même id.
- ``internal_barcode`` : deux instances distinctes partageant une valeur non nulle →
  ``DuplicateInternalBarcodeError`` depuis ``save`` (politique stricte du double ;
  le ``Protocol`` ne mandate pas la levée).
- ``commercial_barcode`` sur les références : au plus une référence par valeur ;
  conflit → ``InvalidProductReferenceError``.
- ``production_code`` : non unique ; ``list_by_production_code`` retourne toutes les lignes
  (tuple trié par ``internal_id``).

Note : ``ProductRepositoryPort`` ne prévoit pas de recherche par EAN ; l’EAN est sur
``ProductReference``.
"""

from __future__ import annotations

from typing import Dict, Optional

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.production_code import ProductionCode
from baobab_mtg_products.exceptions.product.duplicate_internal_barcode_error import (
    DuplicateInternalBarcodeError,
)
from baobab_mtg_products.exceptions.product.invalid_product_reference_error import (
    InvalidProductReferenceError,
)


class InMemoryProductReferenceRepository:
    """Double mémoire pour :class:`ProductReferenceRepositoryPort`."""

    def __init__(self) -> None:
        self._by_id: Dict[str, ProductReference] = {}
        self._commercial_to_ref_id: Dict[str, str] = {}

    def find_by_id(self, reference_id: ProductReferenceId) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        return self._by_id.get(reference_id.value)

    def find_by_commercial_barcode(
        self,
        barcode: CommercialBarcode,
    ) -> Optional[ProductReference]:
        """Voir :class:`ProductReferenceRepositoryPort`."""
        rid = self._commercial_to_ref_id.get(barcode.value)
        if rid is None:
            return None
        return self._by_id.get(rid)

    def save(self, reference: ProductReference) -> None:
        """Enregistre ou remplace une référence ; indexe le code commercial si présent.

        :raises InvalidProductReferenceError: si l’EAN est déjà lié à une autre référence.
        """
        previous = self._by_id.get(reference.reference_id.value)
        if previous is not None and previous.commercial_barcode is not None:
            self._commercial_to_ref_id.pop(previous.commercial_barcode.value, None)

        if reference.commercial_barcode is not None:
            existing_owner = self._commercial_to_ref_id.get(reference.commercial_barcode.value)
            if existing_owner is not None and existing_owner != reference.reference_id.value:
                raise InvalidProductReferenceError(
                    "Ce code-barres commercial est déjà associé à une autre référence catalogue.",
                )
            self._commercial_to_ref_id[reference.commercial_barcode.value] = (
                reference.reference_id.value
            )

        self._by_id[reference.reference_id.value] = reference


class InMemoryProductRepository:
    """Double mémoire pour :class:`ProductRepositoryPort` (instances physiques uniquement)."""

    def __init__(self) -> None:
        self._by_id: Dict[str, ProductInstance] = {}

    def find_by_id(self, product_id: InternalProductId) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`."""
        return self._by_id.get(product_id.value)

    def find_by_internal_barcode(
        self,
        barcode: InternalBarcode,
    ) -> Optional[ProductInstance]:
        """Voir :class:`ProductRepositoryPort`.

        Une implémentation correcte ne doit pas résoudre silencieusement plusieurs exemplaires
        pour un même code interne ; ce double retourne au plus une instance.
        """
        for instance in self._by_id.values():
            if (
                instance.internal_barcode is not None
                and instance.internal_barcode.value == barcode.value
            ):
                return instance
        return None

    def list_by_reference_id(
        self,
        reference_id: ProductReferenceId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [p for p in self._by_id.values() if p.reference_id.value == reference_id.value]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_by_production_code(
        self,
        code: ProductionCode,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        rows = [
            p
            for p in self._by_id.values()
            if p.production_code is not None and p.production_code.value == code.value
        ]
        rows.sort(key=lambda p: p.internal_id.value)
        return tuple(rows)

    def list_direct_children_of_parent(
        self,
        parent_id: InternalProductId,
    ) -> tuple[ProductInstance, ...]:
        """Voir :class:`ProductRepositoryPort`."""
        kids = [
            p
            for p in self._by_id.values()
            if p.parent_id is not None and p.parent_id.value == parent_id.value
        ]
        kids.sort(key=lambda p: p.internal_id.value)
        return tuple(kids)

    def save(self, product: ProductInstance) -> None:
        """Enregistre ou remplace une instance.

        :raises DuplicateInternalBarcodeError: si un autre exemplaire porte déjà ce code interne.
        """
        if product.internal_barcode is not None:
            for pid, other in self._by_id.items():
                if pid == product.internal_id.value:
                    continue
                if (
                    other.internal_barcode is not None
                    and other.internal_barcode.value == product.internal_barcode.value
                ):
                    raise DuplicateInternalBarcodeError(
                        "Ce code-barres interne est déjà attribué à une autre instance.",
                    )
        self._by_id[product.internal_id.value] = product
