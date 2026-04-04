"""Exception racine du domaine baobab-mtg-products."""


class BaobabMtgProductsException(Exception):
    """Erreur de base pour toutes les exceptions métier de la librairie.

    Les exceptions spécifiques (validation, invariants, ports, etc.) doivent
    hériter de cette classe afin de permettre un filtrage homogène côté
    consommateur.

    :param message: Description lisible de l'erreur.
    :type message: str
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message: str = message
