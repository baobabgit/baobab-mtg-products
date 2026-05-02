"""Spécification d'un enfant à créer ou à rattacher lors du déconditionnement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
import baobab_mtg_products.exceptions.deconditioning.invalid_decondition_child_specification_error as _ice  # noqa: E501 pylint: disable=line-too-long

_InvalidChildSpecErr = _ice.InvalidDeconditionChildSpecificationError


@dataclass(frozen=True, slots=True)
class DeconditionChildSpecification:
    """Décrit un enfant soit créé depuis une référence, soit rattaché s'il existe déjà.

    Les deux modes s'excluent mutuellement.

    :param relationship_kind: Règle de compatibilité parent / enfant pour le rattachement.
    :type relationship_kind: ProductRelationshipKind
    :param reference_id: Référence catalogue pour création d'une nouvelle instance.
    :type reference_id: ProductReferenceId | None
    :param internal_barcode: Code-barres interne optionnel pour la création (unicité).
    :type internal_barcode: InternalBarcode | None
    :param existing_child_id: Identifiant d'une instance existante sans parent à rattacher.
    :type existing_child_id: InternalProductId | None
    """

    relationship_kind: ProductRelationshipKind
    reference_id: Optional[ProductReferenceId] = None
    internal_barcode: Optional[InternalBarcode] = None
    existing_child_id: Optional[InternalProductId] = None

    def __post_init__(self) -> None:
        create = self.reference_id is not None
        attach = self.existing_child_id is not None
        if create == attach:
            raise _InvalidChildSpecErr(
                "Chaque enfant doit être soit créé depuis une référence catalogue, "
                "soit rattaché via son identifiant interne existant.",
            )
        if not create and self.internal_barcode is not None:
            raise _InvalidChildSpecErr(
                "Un code-barres interne de création n'est pertinent que pour une "
                "nouvelle instance.",
            )
