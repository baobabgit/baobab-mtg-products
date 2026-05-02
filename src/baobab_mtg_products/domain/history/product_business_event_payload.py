"""Données contextuelles optionnelles d'un événement métier."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ProductBusinessEventPayload:
    """Champs tous optionnels selon le type d'événement.

    :param scan_channel: ``commercial`` ou ``internal`` pour un scan produit.
    :type scan_channel: str | None
    :param barcode_value: Valeur de code-barres ou équivalent scanné.
    :type barcode_value: str | None
    :param parent_id: Identifiant du parent (rattachement / détachement).
    :type parent_id: str | None
    :param relationship_kind: Valeur textuelle du type de lien parent-enfant.
    :type relationship_kind: str | None
    :param previous_parent_id: Parent au moment du détachement.
    :type previous_parent_id: str | None
    :param external_card_id: Identifiant carte externe (révélation).
    :type external_card_id: str | None
    :param sequence_in_opening: Rang d'enregistrement carte (révélation).
    :type sequence_in_opening: str | None
    :param scan_payload: Charge utile brute d'un scan carte en ouverture.
    :type scan_payload: str | None
    :param reference_id: Identifiant de référence catalogue (création d'instance).
    :type reference_id: str | None
    :param production_code_value: Code de production associé (événement d'assignation).
    :type production_code_value: str | None
    :param deconditioned_children_count: Nombre d'enfants traités lors du déconditionnement.
    :type deconditioned_children_count: int | None
    """

    scan_channel: Optional[str] = None
    barcode_value: Optional[str] = None
    parent_id: Optional[str] = None
    relationship_kind: Optional[str] = None
    previous_parent_id: Optional[str] = None
    external_card_id: Optional[str] = None
    sequence_in_opening: Optional[str] = None
    scan_payload: Optional[str] = None
    reference_id: Optional[str] = None
    production_code_value: Optional[str] = None
    deconditioned_children_count: Optional[int] = None
