"""Entité de domaine de base pour les futurs agrégats métier."""

from abc import ABC, abstractmethod


class DomainEntity(ABC):
    """Marqueur abstrait pour les entités du domaine produits scellés.

    Les types métier concrets (instances de produit, relations, événements)
    pourront hériter de cette classe pour signaler leur appartenance au
    domaine et exposer une identité stable.
    """

    @abstractmethod
    def domain_identity(self) -> str:
        """Retourne l'identifiant métier stable de l'entité.

        :return: Identifiant unique au sens du domaine.
        :rtype: str
        """
        ...
