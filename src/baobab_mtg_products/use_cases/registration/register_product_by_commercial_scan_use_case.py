"""Cas d'usage : enregistrement suite à un scan de code-barres commercial."""

from typing import Optional

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.domain.registration.registration_scan_result import (
    RegistrationScanResult,
)
from baobab_mtg_products.use_cases.registration.registration_from_scan_runner import (
    RegistrationFromScanRunner,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class RegisterProductByCommercialScanUseCase(UseCase[RegistrationScanResult]):
    """Encapsule un scan commercial unique avec overrides optionnels.

    L'EAN résout une référence catalogue ; chaque enregistrement matérialise une
    nouvelle instance physique, y compris si l'EAN est déjà connu. Pour une résolution
    référence sans persister d'instance, utiliser
    ``ResolveProductReferenceFromCommercialBarcodeUseCase``.

    :param barcode: Code-barres scanné sur le conditionnement.
    :type barcode: CommercialBarcode
    :param runner: Orchestrateur injecté (dépôt, catalogue, ids, événements).
    :type runner: RegistrationFromScanRunner
    :param serial_number: Numéro de série connu au moment du scan.
    :type serial_number: SerialNumber | None
    :param set_code_override: Forçage du set si le catalogue est incomplet.
    :type set_code_override: MtgSetCode | None
    :param product_type_override: Forçage du type si le catalogue est incomplet.
    :type product_type_override: ProductType | None
    """

    def __init__(
        self,
        barcode: CommercialBarcode,
        runner: RegistrationFromScanRunner,
        *,
        serial_number: Optional[SerialNumber] = None,
        set_code_override: Optional[MtgSetCode] = None,
        product_type_override: Optional[ProductType] = None,
    ) -> None:
        self._barcode = barcode
        self._runner = runner
        self._serial_number = serial_number
        self._set_code_override = set_code_override
        self._product_type_override = product_type_override

    def execute(self) -> RegistrationScanResult:
        """Exécute le scan commercial : nouvelle instance et résolution de référence.

        :return: Résultat typé après persistance (référence dans ``resolved_reference``).
        :rtype: RegistrationScanResult
        """
        return self._runner.register_via_commercial(
            self._barcode,
            serial_number=self._serial_number,
            set_code_override=self._set_code_override,
            product_type_override=self._product_type_override,
        )
