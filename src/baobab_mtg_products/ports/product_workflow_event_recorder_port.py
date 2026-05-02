"""Port d'historisation des événements scan / enregistrement / qualification."""

from typing import Literal, Protocol

ScanChannel = Literal["commercial", "internal"]


class ProductWorkflowEventRecorderPort(Protocol):
    """Contrat pour journaliser les faits métier du workflow produit (append-only)."""

    def record_scan(self, product_id: str, channel: ScanChannel, barcode_value: str) -> None:
        """Enregistre un scan (commercial ou interne) pour une instance.

        :param product_id: Identifiant interne de l'instance concernée.
        :type product_id: str
        :param channel: Canal de scan utilisé.
        :type channel: ScanChannel
        :param barcode_value: Valeur brute ou normalisée auditée.
        :type barcode_value: str
        """
        ...

    def record_registration(self, product_id: str) -> None:
        """Enregistre la première inscription d'une nouvelle instance.

        :param product_id: Identifiant interne nouvellement créé.
        :type product_id: str
        """
        ...

    def record_product_qualified(self, product_id: str) -> None:
        """Enregistre la qualification explicite (type / set stabilisés).

        :param product_id: Identifiant interne qualifié.
        :type product_id: str
        """
        ...

    def record_product_attached_to_parent(
        self,
        child_id: str,
        parent_id: str,
        relationship_kind: str,
    ) -> None:
        """Enregistre un rattachement structurel enfant → parent.

        :param child_id: Identifiant interne de l'enfant.
        :type child_id: str
        :param parent_id: Identifiant interne du parent.
        :type parent_id: str
        :param relationship_kind: Valeur d'énumération du type de lien (chaîne stable).
        :type relationship_kind: str
        """
        ...

    def record_product_detached_from_parent(
        self,
        child_id: str,
        previous_parent_id: str,
    ) -> None:
        """Enregistre la suppression du lien vers le parent.

        :param child_id: Identifiant interne de l'ancien enfant.
        :type child_id: str
        :param previous_parent_id: Identifiant du parent au moment du détachement.
        :type previous_parent_id: str
        """
        ...

    def record_product_opened(self, product_id: str) -> None:
        """Enregistre le passage au statut « opened » pour une instance scellée.

        :param product_id: Identifiant interne du produit ouvert.
        :type product_id: str
        """
        ...

    def record_card_revealed_from_opening(
        self,
        product_id: str,
        external_card_id: str,
        sequence_in_opening: int,
    ) -> None:
        """Enregistre l'association d'une carte révélée à un produit ouvert.

        :param product_id: Produit source (déjà ouvert).
        :type product_id: str
        :param external_card_id: Identifiant carte externe sérialisé.
        :type external_card_id: str
        :param sequence_in_opening: Rang d'enregistrement dans la session.
        :type sequence_in_opening: int
        """
        ...

    def record_opening_card_scan(self, product_id: str, scan_payload: str) -> None:
        """Enregistre un scan de carte effectué pendant ou après l'ouverture.

        :param product_id: Produit ouvert concerné.
        :type product_id: str
        :param scan_payload: Valeur brute ou normalisée auditée.
        :type scan_payload: str
        """
        ...

    def record_product_instance_created(
        self,
        product_id: str,
        reference_id: str,
    ) -> None:
        """Enregistre la création explicite d'une instance physique rattachée à une référence.

        :param product_id: Identifiant interne de la nouvelle instance.
        :type product_id: str
        :param reference_id: Identifiant textuel de la référence catalogue associée.
        :type reference_id: str
        """
        ...

    def record_production_code_assigned(
        self,
        product_id: str,
        production_code: str,
    ) -> None:
        """Enregistre l'association (ou la mise à jour) d'un code de production sur l'instance.

        :param product_id: Identifiant interne de l'instance concernée.
        :type product_id: str
        :param production_code: Valeur normalisée du code de production.
        :type production_code: str
        """
        ...

    def record_container_deconditioned(
        self,
        container_id: str,
        *,
        children_processed: int,
    ) -> None:
        """Enregistre qu'un contenant physique a été déconditionné (sortie des sous-produits).

        Distinct de l'ouverture d'un booster pour révélation de cartes.

        :param container_id: Identifiant interne du contenant déconditionné.
        :type container_id: str
        :param children_processed: Nombre d'enfants créés ou rattachés lors de l'opération.
        :type children_processed: int
        """
        ...
