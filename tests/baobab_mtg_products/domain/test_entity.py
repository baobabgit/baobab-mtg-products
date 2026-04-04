"""Tests pour :class:`~baobab_mtg_products.domain.entity.DomainEntity`."""

import pytest

from baobab_mtg_products.domain.entity import DomainEntity


class _SampleEntity(DomainEntity):
    """Implémentation minimale pour valider la classe abstraite."""

    def __init__(self, identity: str) -> None:
        self._identity = identity

    def domain_identity(self) -> str:
        return self._identity


class TestDomainEntity:
    """Cas nominaux et erreurs pour l'entité de domaine de base."""

    def test_concrete_subclass_returns_identity(self) -> None:
        """Une sous-classe concrète expose son identité métier."""
        entity = _SampleEntity("prod-123")
        assert entity.domain_identity() == "prod-123"

    def test_cannot_instantiate_abstract_base(self) -> None:
        """La classe abstraite ne doit pas être instanciable directement."""
        with pytest.raises(TypeError):
            # pylint: disable=abstract-class-instantiated
            DomainEntity()  # type: ignore[abstract,misc]
