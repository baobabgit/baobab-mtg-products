"""Issue métier d'un enregistrement déclenché par scan."""

from enum import Enum


class RegistrationScanOutcome(str, Enum):
    """Classement du résultat d'un scan pour l'enregistrement."""

    EXISTING_PRODUCT = "existing_product"
    NEW_KNOWN_FROM_CATALOG = "new_known_from_catalog"
    NEW_PENDING_QUALIFICATION = "new_pending_qualification"
    NEW_INSTANCE_SHARED_REFERENCE = "new_instance_shared_reference"
