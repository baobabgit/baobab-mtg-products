"""Cas d'usage : déconditionner un contenant et créer ou rattacher ses sous-produits."""

from __future__ import annotations

from typing import List

from baobab_mtg_products.domain.deconditioning.deconditionable_container_policy import (
    DeconditionableContainerPolicy,
)
from baobab_mtg_products.domain.deconditioning.decondition_child_specification import (
    DeconditionChildSpecification,
)
from baobab_mtg_products.domain.deconditioning.decondition_container_command import (
    DeconditionContainerCommand,
)
from baobab_mtg_products.domain.deconditioning.decondition_container_result import (
    DeconditionContainerResult,
)
from baobab_mtg_products.domain.products.internal_product_id import InternalProductId
from baobab_mtg_products.domain.products.product_instance import ProductInstance
from baobab_mtg_products.domain.products.product_status import ProductStatus
import baobab_mtg_products.exceptions.deconditioning.container_already_deconditioned_error as _cad
import baobab_mtg_products.exceptions.deconditioning.invalid_decondition_child_specification_error as _ice  # noqa: E501 pylint: disable=line-too-long
import baobab_mtg_products.exceptions.deconditioning.product_not_deconditionable_container_error as _pnd  # noqa: E501 pylint: disable=line-too-long
from baobab_mtg_products.exceptions.registration.product_not_found_for_workflow_error import (
    ProductNotFoundForWorkflowError,
)
from baobab_mtg_products.ports.internal_product_id_factory_port import (
    InternalProductIdFactoryPort,
)
from baobab_mtg_products.ports.product_reference_repository_port import (
    ProductReferenceRepositoryPort,
)
from baobab_mtg_products.ports.product_repository_port import ProductRepositoryPort
from baobab_mtg_products.ports.product_workflow_event_recorder_port import (
    ProductWorkflowEventRecorderPort,
)
from baobab_mtg_products.use_cases.instance.create_product_instance_use_case import (
    CreateProductInstanceUseCase,
)
from baobab_mtg_products.use_cases.parent_child.attach_child_product_to_parent_use_case import (
    AttachChildProductToParentUseCase,
)
from baobab_mtg_products.use_cases.use_case import UseCase


class DeconditionContainerUseCase(UseCase[DeconditionContainerResult]):
    """Déconditionne une instance de contenant : sortie des exemplaires enfants.

    S'appuie sur :class:`CreateProductInstanceUseCase` et
    :class:`AttachChildProductToParentUseCase` pour respecter règles de types,
    anti-cycles et journalisation de rattachement. N'émet pas d'événements d'ouverture
    ni de révélation de cartes.

    :param command: Contenant cible et spécifications d'enfants.
    :type command: DeconditionContainerCommand
    :param repository: Persistance des instances.
    :type repository: ProductRepositoryPort
    :param reference_repository: Lecture des références catalogue.
    :type reference_repository: ProductReferenceRepositoryPort
    :param product_ids: Fabrique d'identifiants pour les instances créées.
    :type product_ids: InternalProductIdFactoryPort
    :param events: Journal métier (création, rattachement, déconditionnement).
    :type events: ProductWorkflowEventRecorderPort
    :raises ProductNotFoundForWorkflowError: si le contenant est absent.
    :raises ProductNotDeconditionableContainerError: si le type n'est pas un contenant.
    :raises ContainerAlreadyDeconditionedError: si l'instance a déjà été déconditionnée.
    """

    def __init__(
        self,
        command: DeconditionContainerCommand,
        repository: ProductRepositoryPort,
        reference_repository: ProductReferenceRepositoryPort,
        product_ids: InternalProductIdFactoryPort,
        events: ProductWorkflowEventRecorderPort,
    ) -> None:
        self._command = command
        self._repository = repository
        self._reference_repository = reference_repository
        self._product_ids = product_ids
        self._events = events

    def execute(self) -> DeconditionContainerResult:
        """Traite chaque enfant, met le contenant en ``DECONDITIONED`` et journalise.

        :return: Contenant et enfants tels qu'en dépôt après l'opération.
        :rtype: DeconditionContainerResult
        """
        container = self._repository.find_by_id(self._command.container_internal_id)
        if container is None:
            raise ProductNotFoundForWorkflowError(
                "Aucun contenant ne correspond à l'identifiant fourni pour déconditionnement.",
            )
        if not DeconditionableContainerPolicy.is_deconditionable_container(
            container.product_type,
        ):
            raise _pnd.ProductNotDeconditionableContainerError(
                "Ce type de produit ne peut pas être déconditionné comme un contenant "
                "(ex. un simple booster s'ouvre, il n'est pas un contenant de déconditionnement).",
            )
        if container.status is ProductStatus.DECONDITIONED:
            raise _cad.ContainerAlreadyDeconditionedError(
                "Ce contenant a déjà été déconditionné.",
            )
        processed: List[ProductInstance] = []
        for spec in self._command.children:
            processed.append(
                self._process_child(
                    spec,
                ),
            )
        updated = container.derived_with(status=ProductStatus.DECONDITIONED)
        self._repository.save(updated)
        self._events.record_container_deconditioned(
            container.internal_id.value,
            children_processed=len(self._command.children),
        )
        return DeconditionContainerResult(
            container=updated,
            children=tuple(processed),
        )

    def _process_child(self, spec: DeconditionChildSpecification) -> ProductInstance:
        child_id: InternalProductId
        if spec.reference_id is not None:
            created = CreateProductInstanceUseCase(
                spec.reference_id,
                self._repository,
                self._reference_repository,
                self._product_ids,
                self._events,
                internal_barcode=spec.internal_barcode,
            ).execute()
            AttachChildProductToParentUseCase(
                self._command.container_internal_id,
                created.internal_id,
                spec.relationship_kind,
                self._repository,
                self._events,
            ).execute()
            child_id = created.internal_id
        else:
            existing = spec.existing_child_id
            if existing is None:
                raise _ice.InvalidDeconditionChildSpecificationError(
                    "Rattachement sans identifiant d'enfant existant.",
                )
            AttachChildProductToParentUseCase(
                self._command.container_internal_id,
                existing,
                spec.relationship_kind,
                self._repository,
                self._events,
            ).execute()
            child_id = existing
        found = self._repository.find_by_id(child_id)
        if found is None:
            raise ProductNotFoundForWorkflowError(
                "L'enfant attendu après déconditionnement est introuvable en persistance.",
            )
        return found
