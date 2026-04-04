"""Tests pour :class:`~baobab_mtg_products.use_cases.use_case.UseCase`."""

import pytest

from baobab_mtg_products.use_cases.use_case import UseCase


class _NoOpUseCase(UseCase[int]):
    """Cas d'usage factice retournant une constante."""

    def execute(self) -> int:
        return 42


class TestUseCase:
    """Comportement de la base abstraite des cas d'usage."""

    def test_concrete_use_case_returns_result(self) -> None:
        """Une implémentation concrète exécute et retourne un résultat typé."""
        use_case = _NoOpUseCase()
        assert use_case.execute() == 42

    def test_cannot_instantiate_abstract_use_case(self) -> None:
        """La classe abstraite ne doit pas être instanciable directement."""
        with pytest.raises(TypeError):
            # pylint: disable=abstract-class-instantiated
            UseCase()  # type: ignore[abstract,misc]
