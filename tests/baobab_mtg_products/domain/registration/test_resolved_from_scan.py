"""Tests pour :class:`ResolvedFromScan`."""

from baobab_mtg_products.domain.products.mtg_set_code import MtgSetCode
from baobab_mtg_products.domain.products.product_type import ProductType
from baobab_mtg_products.domain.registration.resolved_from_scan import ResolvedFromScan


class TestResolvedFromScan:
    """Résolution catalogue partielle ou complète."""

    def test_is_complete_when_both_set(self) -> None:
        """Complet lorsque type et set sont présents."""
        r = ResolvedFromScan(
            ProductType.PLAY_BOOSTER,
            MtgSetCode("MH3"),
        )
        assert r.is_complete is True

    def test_is_incomplete_when_partial(self) -> None:
        """Incomplet si l'un des deux manque."""
        assert ResolvedFromScan(ProductType.BUNDLE, None).is_complete is False
        assert ResolvedFromScan(None, MtgSetCode("FDN")).is_complete is False
        assert ResolvedFromScan(None, None).is_complete is False

    def test_is_incomplete_when_type_missing(self) -> None:
        """Plan 11 — set connu sans type : résolution incomplète (qualification pending)."""
        assert ResolvedFromScan(None, MtgSetCode("FDN")).is_complete is False

    def test_is_incomplete_when_set_missing(self) -> None:
        """Plan 11 — type connu sans set : résolution incomplète."""
        assert ResolvedFromScan(ProductType.BUNDLE, None).is_complete is False
