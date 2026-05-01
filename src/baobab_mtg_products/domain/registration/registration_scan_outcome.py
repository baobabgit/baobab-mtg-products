"""Issue métier d'un enregistrement déclenché par scan."""

from enum import Enum


class RegistrationScanOutcome(str, Enum):
    """Classement du résultat d'un scan pour l'enregistrement.

    **Scan commercial** (EAN) : ne doit jamais impliquer une instance unique « déjà
    identifiée » par le seul code commercial ; les issues ``NEW_*`` décrivent la
    création d'une nouvelle instance et la référence associée est portée par
    :attr:`RegistrationScanResult.resolved_reference` lorsqu'elle est connue.

    **Scan interne** : ``EXISTING_PRODUCT`` signifie qu'une instance physique précise
    a été retrouvée ; ``INTERNAL_BARCODE_UNKNOWN`` signifie qu'aucune instance ne
    porte ce code (aucune création implicite).
    """

    EXISTING_PRODUCT = "existing_product"
    INTERNAL_BARCODE_UNKNOWN = "internal_barcode_unknown"
    NEW_KNOWN_FROM_CATALOG = "new_known_from_catalog"
    NEW_PENDING_QUALIFICATION = "new_pending_qualification"
    NEW_INSTANCE_SHARED_REFERENCE = "new_instance_shared_reference"
