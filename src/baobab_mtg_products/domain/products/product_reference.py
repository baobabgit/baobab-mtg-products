"""Référence commerciale et catalogue partagée par plusieurs exemplaires physiques."""

from __future__ import annotations

from typing import Optional, cast

from baobab_mtg_products.domain.entity import DomainEntity
from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.product.invalid_product_reference_error import (
    InvalidProductReferenceError,
)

_DERIVED_FIELD_UNSET = object()


class ProductReference(DomainEntity):
    """Description catalogue d'un produit scellé, sans correspondance 1:1 au physique.

    Le code-barres commercial et les attributs descriptifs (nom, visuel) vivent
    ici ; plusieurs :class:`ProductInstance` peuvent partager la même référence.

    :param reference_id: Identifiant stable de la référence.
    :type reference_id: ProductReferenceId
    :param name: Nom affichable pour l'utilisateur ou les intégrations.
    :type name: str
    :param product_type: Catégorie de produit scellé issue du catalogue ou par défaut.
    :type product_type: ProductType
    :param set_code: Code d'extension Magic associé.
    :type set_code: MtgSetCode
    :param requires_qualification: ``True`` si type ou set proviennent encore de placeholders.
    :type requires_qualification: bool
    :param commercial_barcode: Code-barres du conditionnement, si la référence y est liée.
    :type commercial_barcode: CommercialBarcode | None
    :param image_uri: URI du visuel produit, si disponible.
    :type image_uri: str | None
    :raises InvalidProductReferenceError: si le nom est vide après normalisation.
    """

    def __init__(
        self,
        reference_id: ProductReferenceId,
        name: str,
        product_type: ProductType,
        set_code: MtgSetCode,
        requires_qualification: bool,
        *,
        commercial_barcode: Optional[CommercialBarcode] = None,
        image_uri: Optional[str] = None,
    ) -> None:
        normalized_name = name.strip()
        if not normalized_name:
            raise InvalidProductReferenceError(
                "Le nom d'une référence produit ne peut pas être vide.",
            )

        self._reference_id: ProductReferenceId = reference_id
        self._name: str = normalized_name
        self._product_type: ProductType = product_type
        self._set_code: MtgSetCode = set_code
        self._requires_qualification: bool = requires_qualification
        self._commercial_barcode: Optional[CommercialBarcode] = commercial_barcode
        img: Optional[str] = None
        if image_uri is not None:
            stripped_img = image_uri.strip()
            img = stripped_img if stripped_img else None
        self._image_uri: Optional[str] = img

    @property
    def reference_id(self) -> ProductReferenceId:
        """Identifiant de la référence."""
        return self._reference_id

    @property
    def name(self) -> str:
        """Nom affichable."""
        return self._name

    @property
    def product_type(self) -> ProductType:
        """Type de produit scellé (source catalogue ou valeur par défaut)."""
        return self._product_type

    @property
    def set_code(self) -> MtgSetCode:
        """Code de set Magic."""
        return self._set_code

    @property
    def requires_qualification(self) -> bool:
        """Indique si une qualification opérateur reste nécessaire sur la référence."""
        return self._requires_qualification

    @property
    def commercial_barcode(self) -> Optional[CommercialBarcode]:
        """Code-barres commercial associé à cette référence, le cas échéant."""
        return self._commercial_barcode

    @property
    def image_uri(self) -> Optional[str]:
        """URI du visuel produit, si renseigné."""
        return self._image_uri

    def domain_identity(self) -> str:
        """Identité métier stable : valeur de :class:`ProductReferenceId`.

        :return: Identifiant textuel de la référence.
        :rtype: str
        """
        return self._reference_id.value

    def derived_with(
        self,
        *,
        name: str | object = _DERIVED_FIELD_UNSET,
        product_type: ProductType | object = _DERIVED_FIELD_UNSET,
        set_code: MtgSetCode | object = _DERIVED_FIELD_UNSET,
        requires_qualification: bool | object = _DERIVED_FIELD_UNSET,
        commercial_barcode: Optional[CommercialBarcode] | object = _DERIVED_FIELD_UNSET,
        image_uri: Optional[str] | object = _DERIVED_FIELD_UNSET,
    ) -> ProductReference:
        """Construit une nouvelle référence en ne remplaçant que les champs fournis.

        :param name: Nouveau nom, si fourni.
        :param product_type: Nouveau type, si fourni.
        :param set_code: Nouveau code de set, si fourni.
        :param requires_qualification: Nouvel indicateur de qualification requise.
        :param commercial_barcode: Nouveau code-barres commercial (y compris ``None``).
        :param image_uri: Nouvelle URI d'image (y compris ``None``).
        :return: Copie logique avec les champs fusionnés.
        :rtype: ProductReference
        """
        next_name = self._name if name is _DERIVED_FIELD_UNSET else cast(str, name)
        next_type = (
            self._product_type
            if product_type is _DERIVED_FIELD_UNSET
            else cast(ProductType, product_type)
        )
        next_set = (
            self._set_code if set_code is _DERIVED_FIELD_UNSET else cast(MtgSetCode, set_code)
        )
        next_rq = (
            self._requires_qualification
            if requires_qualification is _DERIVED_FIELD_UNSET
            else cast(bool, requires_qualification)
        )
        next_com = (
            self._commercial_barcode
            if commercial_barcode is _DERIVED_FIELD_UNSET
            else cast(Optional[CommercialBarcode], commercial_barcode)
        )
        next_img = (
            self._image_uri if image_uri is _DERIVED_FIELD_UNSET else cast(Optional[str], image_uri)
        )
        return ProductReference(
            reference_id=self._reference_id,
            name=next_name,
            product_type=next_type,
            set_code=next_set,
            requires_qualification=next_rq,
            commercial_barcode=next_com,
            image_uri=next_img,
        )
