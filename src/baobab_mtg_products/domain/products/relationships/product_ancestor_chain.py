"""Parcours de la chaîne des parents pour détecter les cycles."""

from typing import Optional, Set

from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort


class ProductAncestorChain:
    """Utilitaires sur la généalogie déjà persistée (via :attr:`ProductInstance.parent_id`)."""

    @staticmethod
    def has_broken_or_cyclic_ancestor_path(
        repository: ProductRepositoryPort,
        start: ProductInstance,
    ) -> bool:
        """Détecte un lien parent manquant dans le dépôt ou un cycle dans la remontée.

        :param repository: Source des instances.
        :type repository: ProductRepositoryPort
        :param start: Nœud à partir duquel on remonte.
        :type start: ProductInstance
        :return: ``True`` si les données d'ancêtres sont incohérentes.
        :rtype: bool
        """
        current: Optional[ProductInstance] = start
        visited: Set[str] = set()
        while current is not None and current.parent_id is not None:
            next_parent = repository.find_by_id(current.parent_id)
            if next_parent is None:
                return True
            if next_parent.internal_id.value in visited:
                return True
            visited.add(next_parent.internal_id.value)
            current = next_parent
        return False

    @staticmethod
    def child_is_ancestor_of_parent(
        repository: ProductRepositoryPort,
        parent: ProductInstance,
        child_id: InternalProductId,
    ) -> bool:
        """Indique si ``child_id`` apparaît dans la chaîne des ancêtres de ``parent``.

        Si vrai, rattacher ``child`` comme enfant direct de ``parent`` créerait un cycle.

        :param repository: Source des instances déjà enregistrées.
        :type repository: ProductRepositoryPort
        :param parent: Nœud sous lequel on souhaite accrocher l'enfant.
        :type parent: ProductInstance
        :param child_id: Identifiant du futur enfant (à comparer aux ancêtres).
        :type child_id: InternalProductId
        :return: ``True`` si un cycle serait introduit.
        :rtype: bool
        """
        current: Optional[ProductInstance] = parent
        visited: Set[str] = set()
        while current is not None and current.parent_id is not None:
            next_parent = repository.find_by_id(current.parent_id)
            if next_parent is None:
                return False
            if next_parent.internal_id.value == child_id.value:
                return True
            if next_parent.internal_id.value in visited:
                return True
            visited.add(next_parent.internal_id.value)
            current = next_parent
        return False
