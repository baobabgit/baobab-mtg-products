"""Nature normalisée d'une entrée du journal métier produit."""

from enum import Enum


class ProductBusinessEventKind(str, Enum):
    """Valeurs stables pour filtrage, audit et sérialisation."""

    SCAN = "scan"
    REGISTRATION = "registration"
    QUALIFIED = "qualified"
    ATTACHED_TO_PARENT = "attached_to_parent"
    DETACHED_FROM_PARENT = "detached_from_parent"
    OPENED = "opened"
    CARD_REVEALED_FROM_OPENING = "card_revealed_from_opening"
    OPENING_CARD_SCAN = "opening_card_scan"
    INSTANCE_CREATED = "instance_created"
    PRODUCTION_CODE_ASSIGNED = "production_code_assigned"
    CONTAINER_DECONDITIONED = "container_deconditioned"
