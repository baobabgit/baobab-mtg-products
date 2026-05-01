"""Résultat minimal d'une résolution de code-barres via un référentiel métier."""

from dataclasses import dataclass
from typing import Optional

from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType


@dataclass(frozen=True, slots=True)
class ResolvedFromScan:
    """Information issue du catalogue (ou équivalent) après lookup du scan.

    Les champs peuvent être partiels : le cas d'usage combinera overrides
    opérateur et valeurs par défaut pour matérialiser une :class:`ProductReference`
    puis rattacher une :class:`ProductInstance`.

    :param product_type: Type proposé par le référentiel, si trouvé.
    :type product_type: ProductType | None
    :param set_code: Code de set proposé, si trouvé.
    :type set_code: MtgSetCode | None
    :param display_name: Nom catalogue proposé pour la référence, si disponible.
    :type display_name: str | None
    :param image_uri: URI de visuel produit proposée par le catalogue, si disponible.
    :type image_uri: str | None
    """

    product_type: Optional[ProductType]
    set_code: Optional[MtgSetCode]
    display_name: Optional[str] = None
    image_uri: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """Indique si type et set sont tous deux renseignés par la résolution.

        :return: ``True`` lorsque catalogue et résolution sont exhaustifs.
        :rtype: bool
        """
        return self.product_type is not None and self.set_code is not None
