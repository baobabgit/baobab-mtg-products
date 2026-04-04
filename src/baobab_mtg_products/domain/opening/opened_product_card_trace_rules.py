"""Règles pour enregistrer une trace de carte à partir d'un produit ouvert."""

from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
from baobab_mtg_products.exceptions.opening.product_not_opened_for_card_trace_error import (
    ProductNotOpenedForCardTraceError,
)


class OpenedProductCardTraceRules:
    """Contrôle que la provenance produit est bien un scellé déjà ouvert."""

    @staticmethod
    def assert_product_is_opened_for_card_tracing(instance: ProductInstance) -> None:
        """Lève une erreur si le produit n'est pas au statut ``opened``.

        :param instance: Produit censé être la source des cartes révélées.
        :type instance: ProductInstance
        :raises ProductNotOpenedForCardTraceError: si le statut n'est pas ``opened``.
        """
        if instance.status is not ProductStatus.OPENED:
            raise ProductNotOpenedForCardTraceError(
                "Les cartes révélées ou leurs scans ne peuvent être tracés qu'après ouverture.",
            )
