"""Tests structurels du port :class:`~baobab_mtg_products.ports.CollectionPort`."""

from baobab_mtg_products.ports.collection_port import CollectionPort


class _FakeCollectionAdapter:
    """Adaptateur minimal compatible avec :class:`CollectionPort`."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def notify_product_registered(self, product_id: str) -> None:
        """Enregistre l'identifiant notifié (double de test)."""
        self.seen.append(product_id)


class TestCollectionPort:
    """Vérifie qu'un adaptateur peut satisfaire le contrat du port."""

    def test_adapter_can_notify_registration(self) -> None:
        """La méthode du port est appelable sur un adaptateur typé."""
        fake = _FakeCollectionAdapter()
        adapter: CollectionPort = fake
        adapter.notify_product_registered("p-1")
        assert fake.seen == ["p-1"]
