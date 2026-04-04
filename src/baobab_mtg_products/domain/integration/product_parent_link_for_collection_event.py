"""Événement de lien parent-enfant pour la collection."""

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.exceptions.integration.invalid_integration_payload_error import (
    InvalidIntegrationPayloadError,
)


@dataclass(frozen=True, slots=True)
class ProductParentLinkForCollectionEvent:
    """Décrit un rattachement effectif ou sa levée pour l'intégration collection.

    :param child_product_id: Identifiant de l'enfant.
    :type child_product_id: str
    :param parent_product_id: Identifiant du parent concerné.
    :type parent_product_id: str
    :param relationship_kind_value: Kind métier du rattachement (vide si détaché).
    :type relationship_kind_value: str | None
    :param attached: ``True`` si le lien est actif après l'opération.
    :type attached: bool
    :raises InvalidIntegrationPayloadError: si ``attached`` est vrai sans kind renseigné.
    """

    child_product_id: str
    parent_product_id: str
    relationship_kind_value: Optional[str]
    attached: bool

    def __post_init__(self) -> None:
        if self.attached:
            kind = (self.relationship_kind_value or "").strip()
            if not kind:
                raise InvalidIntegrationPayloadError(
                    "Un rattachement actif exige un relationship_kind_value non vide.",
                )
