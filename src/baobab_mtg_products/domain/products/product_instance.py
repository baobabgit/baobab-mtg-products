"""Instance concrète d'un produit scellé et ses métadonnées de provenance."""

from typing import Optional

from baobab_mtg_products.domain.entity import DomainEntity
from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.exceptions.product.invalid_product_instance_error import (
    InvalidProductInstanceError,
)


class ProductInstance(DomainEntity):
    """Représentation métier d'un produit scellé réel (achat, stock, ouverture).

    Invariants de base : identifiant interne unique, type et set renseignés,
    pas d'auto-référence comme parent.

    :param internal_id: Identifiant interne unique de l'instance.
    :type internal_id: InternalProductId
    :param product_type: Catégorie de produit scellé.
    :type product_type: ProductType
    :param set_code: Code d'extension Magic associé.
    :type set_code: MtgSetCode
    :param status: Statut métier courant.
    :type status: ProductStatus
    :param serial_number: Numéro de série fabricant, si connu.
    :type serial_number: SerialNumber | None
    :param commercial_barcode: Code-barres du conditionnement commercial.
    :type commercial_barcode: CommercialBarcode | None
    :param internal_barcode: Code-barres ou identifiant interne alternatif.
    :type internal_barcode: InternalBarcode | None
    :param parent_id: Identifiant du produit parent (display, bundle, etc.).
    :type parent_id: InternalProductId | None
    :raises InvalidProductInstanceError: si un invariant métier est violé.
    """

    def __init__(
        self,
        internal_id: InternalProductId,
        product_type: ProductType,
        set_code: MtgSetCode,
        status: ProductStatus,
        serial_number: Optional[SerialNumber] = None,
        commercial_barcode: Optional[CommercialBarcode] = None,
        internal_barcode: Optional[InternalBarcode] = None,
        parent_id: Optional[InternalProductId] = None,
    ) -> None:
        if parent_id is not None and parent_id.value == internal_id.value:
            raise InvalidProductInstanceError(
                "Un produit ne peut pas être son propre parent.",
            )

        self._internal_id: InternalProductId = internal_id
        self._product_type: ProductType = product_type
        self._set_code: MtgSetCode = set_code
        self._status: ProductStatus = status
        self._serial_number: Optional[SerialNumber] = serial_number
        self._commercial_barcode: Optional[CommercialBarcode] = commercial_barcode
        self._internal_barcode: Optional[InternalBarcode] = internal_barcode
        self._parent_id: Optional[InternalProductId] = parent_id

    @property
    def internal_id(self) -> InternalProductId:
        """Identifiant interne unique."""
        return self._internal_id

    @property
    def product_type(self) -> ProductType:
        """Type de produit scellé."""
        return self._product_type

    @property
    def set_code(self) -> MtgSetCode:
        """Code de set Magic."""
        return self._set_code

    @property
    def status(self) -> ProductStatus:
        """Statut métier."""
        return self._status

    @property
    def serial_number(self) -> Optional[SerialNumber]:
        """Numéro de série, si présent."""
        return self._serial_number

    @property
    def commercial_barcode(self) -> Optional[CommercialBarcode]:
        """Code-barres commercial, si connu."""
        return self._commercial_barcode

    @property
    def internal_barcode(self) -> Optional[InternalBarcode]:
        """Code-barres interne, si connu."""
        return self._internal_barcode

    @property
    def parent_id(self) -> Optional[InternalProductId]:
        """Référence optionnelle vers le produit parent."""
        return self._parent_id

    def domain_identity(self) -> str:
        """Identité métier stable : identifiant interne.

        :return: Valeur de :class:`InternalProductId`.
        :rtype: str
        """
        return self._internal_id.value
