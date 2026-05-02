"""Commande agrégée pour déconditionner un contenant physique."""

from __future__ import annotations

from dataclasses import dataclass

from baobab_mtg_products.domain.deconditioning.decondition_child_specification import (
    DeconditionChildSpecification,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
import baobab_mtg_products.exceptions.deconditioning.decondition_container_empty_children_error as _dce  # noqa: E501 pylint: disable=line-too-long


@dataclass(frozen=True, slots=True)
class DeconditionContainerCommand:
    """Paramètres du déconditionnement : contenant cible et liste d'enfants.

    :param container_internal_id: Instance physique du contenant (display, bundle, etc.).
    :type container_internal_id: InternalProductId
    :param children: Spécifications ordonnées des enfants à créer ou rattacher.
    :type children: tuple[DeconditionChildSpecification, ...]
    """

    container_internal_id: InternalProductId
    children: tuple[DeconditionChildSpecification, ...]

    def __post_init__(self) -> None:
        if len(self.children) == 0:
            raise _dce.DeconditionContainerEmptyChildrenError(
                "Au moins un enfant doit être fourni pour déconditionner un contenant.",
            )
