"""Modèles du workflow d'enregistrement et de scan."""

from baobab_mtg_products.domain.registration.registration_defaults import RegistrationDefaults
from baobab_mtg_products.domain.registration.registration_scan_outcome import (
    RegistrationScanOutcome,
)
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan

__all__ = [
    "RegistrationDefaults",
    "RegistrationScanOutcome",
    "RegistrationScanResult",
    "ResolvedFromScan",
]
