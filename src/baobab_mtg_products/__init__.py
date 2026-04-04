"""baobab-mtg-products — gestion métier des produits scellés Magic: The Gathering.

Cette librairie modélise le cycle de vie des produits scellés (enregistrement,
relations parent/enfant, ouverture, traçabilité) sans couplage HTTP, UI,
moteur de règles ni deckbuilding.
"""

from importlib.metadata import PackageNotFoundError, version

from baobab_mtg_products.exceptions import BaobabMtgProductsException

try:
    __version__: str = version("baobab-mtg-products")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["BaobabMtgProductsException", "__version__"]
