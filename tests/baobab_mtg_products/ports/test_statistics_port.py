"""Tests structurels du port :class:`~baobab_mtg_products.ports.StatisticsPort`."""

from baobab_mtg_products.ports.statistics_port import StatisticsPort


class _FakeStatisticsAdapter:
    """Adaptateur minimal compatible avec :class:`StatisticsPort`."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, str]]] = []

    def record_opening_event(
        self,
        event_type: str,
        payload: dict[str, str],
    ) -> None:
        """Stocke l'événement reçu (double de test)."""
        self.events.append((event_type, payload))


class TestStatisticsPort:
    """Vérifie qu'un adaptateur peut satisfaire le contrat du port."""

    def test_adapter_records_event(self) -> None:
        """La méthode du port accepte un type et une charge utile."""
        fake = _FakeStatisticsAdapter()
        adapter: StatisticsPort = fake
        adapter.record_opening_event("product_opened", {"id": "x"})
        assert fake.events == [("product_opened", {"id": "x"})]
