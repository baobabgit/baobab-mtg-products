"""Tests pour :class:`~baobab_mtg_products.domain.products.product_instance.ProductInstance`."""

import pytest

from baobab_mtg_products.domain.products.internal_barcode import InternalBarcode
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.products.serial_number import SerialNumber
from baobab_mtg_products.exceptions.product.invalid_product_instance_error import (
    InvalidProductInstanceError,
)


class TestProductInstance:
    """Invariants et accesseurs d'une instance de produit scellé."""

    def _minimal_instance(self) -> ProductInstance:
        """Construit une instance valide avec champs obligatoires uniquement."""
        return ProductInstance(
            internal_id=InternalProductId("p-1"),
            reference_id=ProductReferenceId("ref-1"),
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            status=ProductStatus.REGISTERED,
        )

    def test_nominal_with_optional_fields(self) -> None:
        """Tous les attributs optionnels peuvent être renseignés."""
        parent = InternalProductId("display-1")
        instance = ProductInstance(
            internal_id=InternalProductId("p-2"),
            reference_id=ProductReferenceId("ref-2"),
            product_type=ProductType.DISPLAY,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.QUALIFIED,
            serial_number=SerialNumber("SER-9"),
            internal_barcode=InternalBarcode("int-42"),
            parent_id=parent,
        )
        assert instance.serial_number is not None
        assert instance.serial_number.value == "SER-9"
        assert instance.internal_barcode is not None
        assert instance.parent_id == parent

    def test_domain_identity_matches_internal_id(self) -> None:
        """:meth:`domain_identity` reflète l'identifiant interne."""
        instance = self._minimal_instance()
        assert instance.domain_identity() == "p-1"

    def test_required_properties_on_minimal_instance(self) -> None:
        """Les accesseurs des champs obligatoires exposent les value objects."""
        instance = self._minimal_instance()
        assert instance.internal_id.value == "p-1"
        assert instance.reference_id.value == "ref-1"
        assert instance.product_type is ProductType.PLAY_BOOSTER
        assert instance.set_code.value == "MH3"
        assert instance.status is ProductStatus.REGISTERED
        assert instance.serial_number is None
        assert instance.internal_barcode is None
        assert instance.parent_id is None

    def test_rejects_self_parent_reference(self) -> None:
        """Un produit ne peut pas référencer lui-même comme parent."""
        pid = InternalProductId("same")
        with pytest.raises(InvalidProductInstanceError) as exc:
            ProductInstance(
                internal_id=pid,
                reference_id=ProductReferenceId("ref-x"),
                product_type=ProductType.BUNDLE,
                set_code=MtgSetCode("BIG"),
                status=ProductStatus.SEALED,
                parent_id=pid,
            )
        assert "parent" in exc.value.message.lower()

    def test_derived_with_replaces_selected_fields(self) -> None:
        """:meth:`derived_with` conserve l'identité et met à jour les champs passés."""
        base = self._minimal_instance()
        derived = base.derived_with(
            status=ProductStatus.QUALIFIED,
            product_type=ProductType.COLLECTOR_BOOSTER,
        )
        assert derived.internal_id.value == base.internal_id.value
        assert derived.reference_id.value == base.reference_id.value
        assert derived.status is ProductStatus.QUALIFIED
        assert derived.product_type is ProductType.COLLECTOR_BOOSTER
        assert derived.set_code.value == base.set_code.value
