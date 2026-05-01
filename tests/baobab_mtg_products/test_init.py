"""Tests du point d'entrée public du package."""

import importlib
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import baobab_mtg_products
from baobab_mtg_products import (
    BaobabMtgProductsException,
    GetSealedProductSnapshotService,
    ProductInstance,
    ProductNotFoundForQueryError,
    ProductStructuralView,
    ProductType,
)


class TestBaobabMtgProductsRoot:
    """Vérifie les exports et la version exposée par le package racine."""

    def test_version_is_non_empty_string(self) -> None:
        """La version doit être une chaîne non vide."""
        assert isinstance(baobab_mtg_products.__version__, str)
        assert baobab_mtg_products.__version__

    def test_exports_baobab_mtg_products_exception(self) -> None:
        """L'exception racine doit être importable depuis le package."""
        assert issubclass(BaobabMtgProductsException, Exception)

    def test_exports_product_model_symbols(self) -> None:
        """Le modèle produit de référence est exposé au niveau racine."""
        assert ProductType.DISPLAY.value == "display"
        assert ProductInstance.__name__ == "ProductInstance"

    def test_exports_query_surface(self) -> None:
        """Consultation et exceptions associées accessibles depuis le package racine."""
        assert GetSealedProductSnapshotService.__name__ == "GetSealedProductSnapshotService"
        assert ProductStructuralView.__name__ == "ProductStructuralView"
        assert issubclass(ProductNotFoundForQueryError, BaobabMtgProductsException)

    def test_version_fallback_when_package_metadata_missing(self) -> None:
        """Sans métadonnées distribuées, la version de repli doit s'appliquer."""
        with patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError(),
        ):
            importlib.reload(baobab_mtg_products)
            assert baobab_mtg_products.__version__ == "2.1.0"
        importlib.reload(baobab_mtg_products)
