"""Valeurs par défaut pour les produits issus d'un scan encore incomplet."""

from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType


class RegistrationDefaults:
    """Constantes métier pour l'enregistrement en attente de qualification.

    Le code de set ``QQ`` est réservé côté domaine pour signaler un set non
    encore identifié après un scan seul ; il doit être remplacé par une
    qualification explicite.
    """

    _PLACEHOLDER_SET = "QQ"

    @classmethod
    def placeholder_set_code(cls) -> MtgSetCode:
        """Code de set réservé lorsque le scan n'a pas permis d'identifier l'extension.

        :return: Code placeholder stable pour l'attente de qualification.
        :rtype: MtgSetCode
        """
        return MtgSetCode(cls._PLACEHOLDER_SET)

    @classmethod
    def unknown_product_type(cls) -> ProductType:
        """Type générique lorsque le catalogue ne propose pas de catégorie.

        :return: Type « autre scellé ».
        :rtype: ProductType
        """
        return ProductType.OTHER_SEALED

    @classmethod
    def is_placeholder_set(cls, set_code: MtgSetCode) -> bool:
        """Indique si le set est encore le marqueur d'attente.

        :param set_code: Code à comparer au placeholder.
        :type set_code: MtgSetCode
        :return: ``True`` si le code correspond au placeholder réservé.
        :rtype: bool
        """
        return set_code.value == cls._PLACEHOLDER_SET
