"""Journal métier en mémoire : cohérence minimale et port workflow complet."""

from __future__ import annotations

from typing import Dict, List, Set

from baobab_mtg_products.domain.history.product_business_event_kind import (
    ProductBusinessEventKind,
)
from baobab_mtg_products.domain.history.product_business_event_payload import (
    ProductBusinessEventPayload,
)
from baobab_mtg_products.domain.history.product_business_event_record import (
    ProductBusinessEventRecord,
)
from baobab_mtg_products.exceptions.history.product_history_coherence_error import (
    ProductHistoryCoherenceError,
)
from baobab_mtg_products.ports.product_workflow_event_recorder_port import ScanChannel


class InMemoryProductBusinessEventLedger:
    """Append-only : enregistre les faits métier et expose la consultation par produit.

    Implémente le contrat :class:`ProductWorkflowEventRecorderPort` et la lecture
    homonyme attendue par :class:`ProductBusinessHistoryQueryPort`.

    Contrôles minimaux : pas de double enregistrement / qualification / ouverture ;
    rattachement cohérent ; traces carte après ouverture ; détachement aligné sur
    le parent courant du journal.
    """

    def __init__(self) -> None:
        self._records: List[ProductBusinessEventRecord] = []
        self._next_seq: int = 0
        self._known_product_ids: Set[str] = set()
        self._registered_ids: Set[str] = set()
        self._qualified_ids: Set[str] = set()
        self._opened_ids: Set[str] = set()
        self._child_current_parent: Dict[str, str] = {}

    def list_events_for_product(self, product_id: str) -> tuple[ProductBusinessEventRecord, ...]:
        """Retourne les événements concernant l'identifiant (vue produit ou parent).

        Inclut les rattachements / détachements où ce produit apparaît comme parent.

        :param product_id: Identifiant interne à inspecter.
        :type product_id: str
        :return: Séquence chronologique (ordre d'insertion global).
        :rtype: tuple[ProductBusinessEventRecord, ...]
        """
        result: List[ProductBusinessEventRecord] = []
        for record in self._records:
            if record.principal_product_id == product_id:
                result.append(record)
            elif (
                record.kind is ProductBusinessEventKind.ATTACHED_TO_PARENT
                and record.payload.parent_id == product_id
            ):
                result.append(record)
            elif (
                record.kind is ProductBusinessEventKind.DETACHED_FROM_PARENT
                and record.payload.previous_parent_id == product_id
            ):
                result.append(record)
        return tuple(result)

    def record_scan(self, product_id: str, channel: ScanChannel, barcode_value: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.SCAN,
            payload=ProductBusinessEventPayload(
                scan_channel=channel,
                barcode_value=barcode_value,
            ),
        )
        self._known_product_ids.add(product_id)

    def record_registration(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id in self._registered_ids:
            raise ProductHistoryCoherenceError(
                "Enregistrement déjà journalisé pour cet identifiant.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.REGISTRATION,
            payload=ProductBusinessEventPayload(),
        )
        self._registered_ids.add(product_id)
        self._known_product_ids.add(product_id)

    def record_product_qualified(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id not in self._registered_ids:
            raise ProductHistoryCoherenceError(
                "La qualification exige un enregistrement préalable dans le journal.",
            )
        if product_id in self._qualified_ids:
            raise ProductHistoryCoherenceError(
                "Qualification déjà journalisée pour cet identifiant.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.QUALIFIED,
            payload=ProductBusinessEventPayload(),
        )
        self._qualified_ids.add(product_id)

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if child_id == parent_id:
            raise ProductHistoryCoherenceError(
                "Rattachement refusé : enfant et parent identiques.",
            )
        if child_id not in self._known_product_ids or parent_id not in self._known_product_ids:
            raise ProductHistoryCoherenceError(
                "Rattachement refusé : le parent et l'enfant doivent être connus du journal.",
            )
        if child_id in self._child_current_parent:
            raise ProductHistoryCoherenceError(
                "Rattachement refusé : l'enfant est déjà lié à un parent dans le journal.",
            )
        self._append(
            principal_product_id=child_id,
            kind=ProductBusinessEventKind.ATTACHED_TO_PARENT,
            payload=ProductBusinessEventPayload(
                parent_id=parent_id,
                relationship_kind=relationship_kind,
            ),
        )
        self._child_current_parent[child_id] = parent_id

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        current = self._child_current_parent.get(child_id)
        if current != previous_parent_id:
            raise ProductHistoryCoherenceError(
                "Détachement refusé : le parent courant ne correspond pas au journal.",
            )
        self._append(
            principal_product_id=child_id,
            kind=ProductBusinessEventKind.DETACHED_FROM_PARENT,
            payload=ProductBusinessEventPayload(previous_parent_id=previous_parent_id),
        )
        del self._child_current_parent[child_id]

    def record_product_opened(self, product_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id not in self._known_product_ids:
            raise ProductHistoryCoherenceError(
                "Ouverture refusée : aucun scan ni enregistrement préalable dans le journal.",
            )
        if product_id in self._opened_ids:
            raise ProductHistoryCoherenceError(
                "Ouverture déjà journalisée pour cet identifiant.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.OPENED,
            payload=ProductBusinessEventPayload(),
        )
        self._opened_ids.add(product_id)

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id not in self._opened_ids:
            raise ProductHistoryCoherenceError(
                "Révélation carte refusée : ouverture non journalisée pour ce produit.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.CARD_REVEALED_FROM_OPENING,
            payload=ProductBusinessEventPayload(
                external_card_id=external_card_id,
                sequence_in_opening=str(sequence_in_opening),
            ),
        )

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id not in self._opened_ids:
            raise ProductHistoryCoherenceError(
                "Scan carte refusé : ouverture non journalisée pour ce produit.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.OPENING_CARD_SCAN,
            payload=ProductBusinessEventPayload(scan_payload=scan_payload),
        )

    def record_product_instance_created(self, product_id: str, reference_id: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id in self._registered_ids:
            raise ProductHistoryCoherenceError(
                "Création d'instance déjà journalisée pour cet identifiant.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.INSTANCE_CREATED,
            payload=ProductBusinessEventPayload(reference_id=reference_id),
        )
        self._registered_ids.add(product_id)
        self._known_product_ids.add(product_id)

    def record_production_code_assigned(self, product_id: str, production_code: str) -> None:
        """Voir :class:`ProductWorkflowEventRecorderPort`."""
        if product_id not in self._known_product_ids:
            raise ProductHistoryCoherenceError(
                "Association de code de production refusée : instance inconnue du journal.",
            )
        self._append(
            principal_product_id=product_id,
            kind=ProductBusinessEventKind.PRODUCTION_CODE_ASSIGNED,
            payload=ProductBusinessEventPayload(production_code_value=production_code),
        )

    def _append(
        self,
        *,
        principal_product_id: str,
        kind: ProductBusinessEventKind,
        payload: ProductBusinessEventPayload,
    ) -> None:
        record = ProductBusinessEventRecord(
            global_sequence=self._next_seq,
            principal_product_id=principal_product_id,
            kind=kind,
            payload=payload,
        )
        self._records.append(record)
        self._next_seq += 1
