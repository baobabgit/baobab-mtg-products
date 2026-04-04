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
