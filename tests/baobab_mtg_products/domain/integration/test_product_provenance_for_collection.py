"""Tests pour :class:`ProductProvenanceForCollection`."""

from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_reference_id import ProductReferenceId
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.domain.products.product_type import ProductType


class TestProductProvenanceForCollection:
    """Construction depuis :class:`ProductInstance`."""

    def test_from_product_instance_maps_fields(self) -> None:
        """Les champs reflètent l'agrégat source."""
        parent = InternalProductId("par")
        inst = ProductInstance(
            internal_id=InternalProductId("ch"),
            reference_id=ProductReferenceId("ref-ch"),
            product_type=ProductType.PLAY_BOOSTER,
            set_code=MtgSetCode("MH3"),
            status=ProductStatus.SEALED,
            parent_id=parent,
        )
        dto = ProductProvenanceForCollection.from_product_instance(inst)
        assert dto.internal_product_id == "ch"
        assert dto.product_reference_id == "ref-ch"
        assert dto.product_type_value == "play_booster"
        assert dto.set_code_value == "MH3"
        assert dto.product_status_value == "sealed"
        assert dto.parent_product_id == "par"

    def test_from_product_instance_without_parent(self) -> None:
        """Sans parent, le champ reste nul."""
        inst = ProductInstance(
            internal_id=InternalProductId("solo"),
            reference_id=ProductReferenceId("ref-solo"),
            product_type=ProductType.BUNDLE,
            set_code=MtgSetCode("FDN"),
            status=ProductStatus.QUALIFIED,
        )
        dto = ProductProvenanceForCollection.from_product_instance(inst)
        assert dto.parent_product_id is None
