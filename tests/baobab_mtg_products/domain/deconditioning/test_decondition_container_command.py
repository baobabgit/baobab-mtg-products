"""Tests unitaires — DTO / commande déconditionnement (feature 12)."""

from __future__ import annotations

import pytest

from baobab_mtg_products.domain.deconditioning.decondition_child_specification import (
    DeconditionChildSpecification,
)
from baobab_mtg_products.domain.deconditioning.decondition_container_command import (
    DeconditionContainerCommand,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
import baobab_mtg_products.exceptions.deconditioning.decondition_container_empty_children_error as _dce  # noqa: E501
import baobab_mtg_products.exceptions.deconditioning.invalid_decondition_child_specification_error as _ice  # noqa: E501


def test_command_rejects_empty_children_when_required() -> None:
    """Liste vide → erreur métier."""
    with pytest.raises(_dce.DeconditionContainerEmptyChildrenError):
        DeconditionContainerCommand(InternalProductId("c"), ())


def test_child_spec_create_vs_attach_discriminant() -> None:
    """Création vs rattachement mutuellement exclusifs."""
    with pytest.raises(_ice.InvalidDeconditionChildSpecificationError):
        DeconditionChildSpecification(ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT)
    with pytest.raises(_ice.InvalidDeconditionChildSpecificationError):
        DeconditionChildSpecification(
            ProductRelationshipKind.GENERIC_STRUCTURAL_ATTACHMENT,
            reference_id=ProductReferenceId("r1"),
            existing_child_id=InternalProductId("x"),
        )
