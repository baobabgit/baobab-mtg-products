"""Tests pour :class:`ProductReference`."""

import pytest

from baobab_mtg_products.domain.products.commercial_barcode import CommercialBarcode
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_reference import ProductReference
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.exceptions.product.invalid_product_reference_error import (
    InvalidProductReferenceError,
)


class TestProductReference:
    """Invariants et copies dérivées d'une référence catalogue."""

    def test_domain_identity_is_reference_id_value(self) -> None:
        """:meth:`domain_identity` renvoie l'identifiant stable."""
        ref = ProductReference(
            ProductReferenceId("r1"),
            name="Booster MH3",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("12345678"),
        )
        assert ref.domain_identity() == "r1"
        assert ref.commercial_barcode is not None

    def test_rejects_blank_name(self) -> None:
        """Le nom affichable ne peut pas être vide."""
        with pytest.raises(InvalidProductReferenceError):
            ProductReference(
                ProductReferenceId("r2"),
                name="   ",
                product_type=ProductType.BUNDLE,
                set_code=MtgSetCode("FDN"),
                requires_qualification=False,
            )

    def test_blank_image_uri_normalized_to_none(self) -> None:
        """Une URI d'image vide ou uniquement des espaces devient ``None``."""
        ref = ProductReference(
            ProductReferenceId("r-img"),
            name="With img",
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            requires_qualification=False,
            image_uri="   ",
        )
        assert ref.image_uri is None

    def test_derived_with_updates_fields(self) -> None:
        """:meth:`derived_with` produit une nouvelle référence cohérente."""
        base = ProductReference(
            ProductReferenceId("r3"),
            name="X",
            product_type=ProductType.OTHER_SEALED,
            set_code=MtgSetCode("QQ"),
            requires_qualification=True,
        )
        next_ref = base.derived_with(
            name="Qualifié",
            product_type=ProductType.DRAFT_BOOSTER,
            set_code=MtgSetCode("MH2"),
            requires_qualification=False,
        )
        assert next_ref.reference_id.value == "r3"
        assert next_ref.name == "Qualifié"
        assert next_ref.requires_qualification is False

    def test_accessors_expose_optional_barcode_and_image(self) -> None:
        """Les accesseurs reflètent les champs optionnels renseignés."""
        ref = ProductReference(
            ProductReferenceId("r-opt"),
            name="Opt",
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH1"),
            requires_qualification=False,
            commercial_barcode=CommercialBarcode("12345678"),
            image_uri="https://example.local/card.png",
        )
        assert ref.commercial_barcode is not None
        assert ref.image_uri == "https://example.local/card.png"
        assert ref.domain_identity() == "r-opt"
