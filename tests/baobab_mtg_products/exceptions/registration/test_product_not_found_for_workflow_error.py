"""Tests pour ProductNotFoundForWorkflowError."""

from baobab_mtg_products.exceptions.baobab_mtg_products_exception import (
    BaobabMtgProductsException,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)


class TestProductNotFoundForWorkflowError:
    """Hiérarchie d'exception."""

    def test_inherits_base(self) -> None:
        """Extension de l'exception racine métier."""
        assert issubclass(ProductNotFoundForWorkflowError, BaobabMtgProductsException)
