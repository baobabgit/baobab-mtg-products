"""Instance concrète d'un produit scellé et ses métadonnées de provenance."""

from __future__ import annotations

from typing import Optional, cast

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

_DERIVED_FIELD_UNSET = object()


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

    def derived_with(
        self,
        *,
        product_type: ProductType | object = _DERIVED_FIELD_UNSET,
        set_code: MtgSetCode | object = _DERIVED_FIELD_UNSET,
        status: ProductStatus | object = _DERIVED_FIELD_UNSET,
        serial_number: Optional[SerialNumber] | object = _DERIVED_FIELD_UNSET,
        commercial_barcode: Optional[CommercialBarcode] | object = _DERIVED_FIELD_UNSET,
        internal_barcode: Optional[InternalBarcode] | object = _DERIVED_FIELD_UNSET,
        parent_id: Optional[InternalProductId] | object = _DERIVED_FIELD_UNSET,
    ) -> ProductInstance:
        """Construit une nouvelle instance en conservant l'identité et l'historique logique.

        Seuls les paramètres explicitement fournis (autre que la sentinelle
        interne) remplacent les champs correspondants. Utile pour qualification
        ou corrections métier sans mutateur sur l'objet d'origine.

        :param product_type: Nouveau type, si fourni.
        :param set_code: Nouveau code de set, si fourni.
        :param status: Nouveau statut, si fourni.
        :param serial_number: Nouveau numéro de série (y compris ``None`` explicite).
        :param commercial_barcode: Nouveau code-barres commercial.
        :param internal_barcode: Nouveau code-barres interne.
        :param parent_id: Nouvelle référence parente.
        :return: Nouvelle :class:`ProductInstance` avec les champs fusionnés.
        :rtype: ProductInstance
        """
        next_type = (
            self._product_type
            if product_type is _DERIVED_FIELD_UNSET
            else cast(ProductType, product_type)
        )
        next_set = (
            self._set_code if set_code is _DERIVED_FIELD_UNSET else cast(MtgSetCode, set_code)
        )
        next_status = (
            self._status if status is _DERIVED_FIELD_UNSET else cast(ProductStatus, status)
        )
        next_serial = (
            self._serial_number
            if serial_number is _DERIVED_FIELD_UNSET
            else cast(Optional[SerialNumber], serial_number)
        )
        next_commercial = (
            self._commercial_barcode
            if commercial_barcode is _DERIVED_FIELD_UNSET
            else cast(Optional[CommercialBarcode], commercial_barcode)
        )
        next_internal = (
            self._internal_barcode
            if internal_barcode is _DERIVED_FIELD_UNSET
            else cast(Optional[InternalBarcode], internal_barcode)
        )
        next_parent = (
            self._parent_id
            if parent_id is _DERIVED_FIELD_UNSET
            else cast(Optional[InternalProductId], parent_id)
        )
        return ProductInstance(
            internal_id=self._internal_id,
            product_type=next_type,
            set_code=next_set,
            status=next_status,
            serial_number=next_serial,
            commercial_barcode=next_commercial,
            internal_barcode=next_internal,
            parent_id=next_parent,
        )
