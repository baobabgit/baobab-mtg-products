"""Classe de base pour les cas d'usage métier."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)


class UseCase(ABC, Generic[T_co]):
    """Point d'extension pour les cas d'usage orientés métier.

    Les implémentations concrètes encapsuleront les workflows (enregistrement,
    rattachement, ouverture, etc.) plutôt qu'un accès technique générique.

    :typeparam T_co: Type de la valeur produite par le cas d'usage.
    """

    @abstractmethod
    def execute(self) -> T_co:
        """Exécute le scénario métier et retourne son résultat.

        :return: Résultat typé du cas d'usage.
        :rtype: T_co
        """
        ...
