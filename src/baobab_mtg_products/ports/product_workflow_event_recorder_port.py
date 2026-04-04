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
