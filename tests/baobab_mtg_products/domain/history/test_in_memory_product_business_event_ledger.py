"""Tests pour :class:`InMemoryProductBusinessEventLedger`."""

import pytest

from baobab_mtg_products.domain.history.in_memory_product_business_event_ledger import (
    InMemoryProductBusinessEventLedger,
)
from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.exceptions.history.product_history_coherence_error import (
    ProductHistoryCoherenceError,
)


class TestInMemoryProductBusinessEventLedger:
    """Cohérence, ordre et vues par produit."""

    def test_registration_then_scan_sequence(self) -> None:
        """Ordre global monotone."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("a")
        ledger.record_scan("a", "commercial", "b1")
        events = ledger.list_events_for_product("a")
        assert [e.kind for e in events] == [
            ProductBusinessEventKind.REGISTRATION,
            ProductBusinessEventKind.SCAN,
        ]
        assert events[0].global_sequence < events[1].global_sequence

    def test_scan_only_then_open(self) -> None:
        """Produit connu uniquement par scan (pas d'enregistrement)."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_scan("legacy", "internal", "x")
        ledger.record_product_opened("legacy")
        kinds = [e.kind for e in ledger.list_events_for_product("legacy")]
        assert kinds[-1] is ProductBusinessEventKind.OPENED

    def test_rejects_duplicate_registration(self) -> None:
        """Double enregistrement."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_registration("p")

    def test_rejects_qualify_without_registration(self) -> None:
        """Qualification sans enregistrement."""
        ledger = InMemoryProductBusinessEventLedger()
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_qualified("p")

    def test_rejects_second_qualification(self) -> None:
        """Une seule qualification journalisée."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p")
        ledger.record_product_qualified("p")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_qualified("p")

    def test_rejects_open_without_known_product(self) -> None:
        """Ouverture sans activité préalable."""
        ledger = InMemoryProductBusinessEventLedger()
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_opened("ghost")

    def test_rejects_second_open(self) -> None:
        """Double ouverture."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p")
        ledger.record_product_opened("p")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_opened("p")

    def test_rejects_card_without_open(self) -> None:
        """Carte sans ouverture."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_card_revealed_from_opening("p", "c1", 0)

    def test_rejects_opening_scan_without_open(self) -> None:
        """Scan carte sans ouverture."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_opening_card_scan("p", "payload")

    def test_parent_sees_attach_and_detach(self) -> None:
        """Vue parent : rattachement puis détachement."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("parent")
        ledger.record_registration("child")
        ledger.record_product_attached_to_parent(
            "child",
            "parent",
            "generic_structural_attachment",
        )
        ledger.record_product_detached_from_parent("child", "parent")
        parent_view = ledger.list_events_for_product("parent")
        assert [e.kind for e in parent_view] == [
            ProductBusinessEventKind.REGISTRATION,
            ProductBusinessEventKind.ATTACHED_TO_PARENT,
            ProductBusinessEventKind.DETACHED_FROM_PARENT,
        ]

    def test_rejects_attach_unknown_child(self) -> None:
        """Enfant inconnu du journal."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("parent")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_attached_to_parent(
                "nope",
                "parent",
                "generic_structural_attachment",
            )

    def test_rejects_double_attach(self) -> None:
        """Enfant déjà rattaché dans le journal."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p1")
        ledger.record_registration("c1")
        ledger.record_product_attached_to_parent(
            "c1",
            "p1",
            "bundle_contains_subproduct",
        )
        ledger.record_registration("p2")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_attached_to_parent(
                "c1",
                "p2",
                "generic_structural_attachment",
            )

    def test_rejects_detach_wrong_parent(self) -> None:
        """Détachement incohérent."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("p1")
        ledger.record_registration("c1")
        ledger.record_product_attached_to_parent(
            "c1",
            "p1",
            "generic_structural_attachment",
        )
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_detached_from_parent("c1", "other")

    def test_rejects_self_parent_attach(self) -> None:
        """Enfant et parent identiques."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("solo")
        with pytest.raises(ProductHistoryCoherenceError):
            ledger.record_product_attached_to_parent(
                "solo",
                "solo",
                "generic_structural_attachment",
            )

    def test_card_reveal_and_scan_after_open(self) -> None:
        """Traces carte une fois ouvert."""
        ledger = InMemoryProductBusinessEventLedger()
        ledger.record_registration("b")
        ledger.record_product_opened("b")
        ledger.record_card_revealed_from_opening("b", "c1", 0)
        ledger.record_opening_card_scan("b", "raw-scan")
        kinds = [e.kind for e in ledger.list_events_for_product("b")]
        assert kinds[-2] is ProductBusinessEventKind.CARD_REVEALED_FROM_OPENING
        assert kinds[-1] is ProductBusinessEventKind.OPENING_CARD_SCAN
