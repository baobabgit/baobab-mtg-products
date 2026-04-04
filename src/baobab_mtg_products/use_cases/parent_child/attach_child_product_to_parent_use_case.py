"""Cas d'usage : rattacher une instance sans parent à un parent conforme au kind."""

from typing import Optional

from baobab_mtg_products.domain.integration.product_parent_link_for_collection_event import (
    ProductParentLinkForCollectionEvent,
)
from baobab_mtg_products.domain.integration.product_provenance_for_collection import (
    ProductProvenanceForCollection,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.relationships.parent_child_relationship_rules import (
    ParentChildRelationshipRules,
)
from baobab_mtg_products.domain.products.relationships.product_ancestor_chain import (
    ProductAncestorChain,
)
from baobab_mtg_products.domain.products.relationships.product_relationship import (
    ProductRelationship,
)
from baobab_mtg_products.domain.products.relationships.product_relationship_kind import (
    ProductRelationshipKind,
)
from baobab_mtg_products.exceptions.relationship.circular_product_parentage_error import (
    CircularProductParentageError,
)
from baobab_mtg_products.exceptions.relationship.incomplete_product_hierarchy_error import (
    IncompleteProductHierarchyError,
)
from baobab_mtg_products.exceptions.relationship.invalid_product_relationship_link_error import (
    InvalidProductRelationshipLinkError,
)
from baobab_mtg_products.exceptions.relationship.product_already_has_parent_error import (
    ProductAlreadyHasParentError,
)
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.collection_port import CollectionPort
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class AttachChildProductToParentUseCase(UseCase[ProductRelationship]):
    """Rattache un produit « orphelin » (sans ``parent_id``) sous un parent valide.

    :param parent_id: Identifiant du futur parent.
    :type parent_id: InternalProductId
    :param child_id: Identifiant du futur enfant.
    :type child_id: InternalProductId
    :param kind: Règle métier de compatibilité des types.
    :type kind: ProductRelationshipKind
    :param repository: Persistance des instances.
    :type repository: ProductRepositoryPort
    :param events: Journal des rattachements.
    :type events: ProductWorkflowEventRecorderPort
    :param collection: Synchronisation collection (provenance enfant + lien), si fourni.
    :type collection: CollectionPort | None
    :raises InvalidProductRelationshipLinkError: si parent et enfant sont identiques.
    :raises ProductNotFoundForWorkflowError: si l'un des identifiants est inconnu.
    :raises ProductAlreadyHasParentError: si l'enfant a déjà un parent.
    :raises IncompatibleParentChildTypesError: si les types ne correspondent pas au kind.
    :raises CircularProductParentageError: si le rattachement créerait un cycle.
    :raises IncompleteProductHierarchyError: si la chaîne des ancêtres du parent est corrompue.
    """

    def __init__(
        self,
        parent_id: InternalProductId,
        child_id: InternalProductId,
        kind: ProductRelationshipKind,
        repository: ProductRepositoryPort,
        events: ProductWorkflowEventRecorderPort,
        collection: Optional[CollectionPort] = None,
    ) -> None:
        self._parent_id = parent_id
        self._child_id = child_id
        self._kind = kind
        self._repository = repository
        self._events = events
        self._collection = collection

    def execute(self) -> ProductRelationship:
        """Persiste ``parent_id`` sur l'enfant et journalise l'événement.

        :return: Valeur objet représentant le lien créé.
        :rtype: ProductRelationship
        """
        if self._parent_id.value == self._child_id.value:
            raise InvalidProductRelationshipLinkError(
                "Le parent et l'enfant doivent être deux instances distinctes.",
            )
        parent = self._repository.find_by_id(self._parent_id)
        child = self._repository.find_by_id(self._child_id)
        if parent is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit parent ne correspond à l'identifiant fourni.",
            )
        if child is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun produit enfant ne correspond à l'identifiant fourni.",
            )
        if child.parent_id is not None:
            raise ProductAlreadyHasParentError(
                "Ce produit est déjà rattaché à un parent ; détachez-le d'abord.",
            )
        ParentChildRelationshipRules.validate(parent, child, self._kind)
        if ProductAncestorChain.has_broken_or_cyclic_ancestor_path(self._repository, parent):
            raise IncompleteProductHierarchyError(
                "La chaîne des parents du produit parent est incohérente dans le dépôt.",
            )
        if ProductAncestorChain.child_is_ancestor_of_parent(
            self._repository,
            parent,
            child.internal_id,
        ):
            raise CircularProductParentageError(
                "Ce rattachement ferait du futur enfant un ancêtre du parent (cycle).",
            )
        updated_child = child.derived_with(parent_id=parent.internal_id)
        self._repository.save(updated_child)
        link = ProductRelationship(
            parent_id=parent.internal_id,
            child_id=child.internal_id,
            kind=self._kind,
        )
        self._events.record_product_attached_to_parent(
            child.internal_id.value,
            parent.internal_id.value,
            self._kind.value,
        )
        if self._collection is not None:
            self._collection.publish_product_provenance(
                ProductProvenanceForCollection.from_product_instance(updated_child),
            )
            self._collection.publish_parent_child_link(
                ProductParentLinkForCollectionEvent(
                    child_product_id=child.internal_id.value,
                    parent_product_id=parent.internal_id.value,
                    relationship_kind_value=self._kind.value,
                    attached=True,
                ),
            )
        return link
