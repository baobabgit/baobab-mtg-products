# Feature 11 — Refonte des workflows de scan commercial et interne

## Comportement public (rappel QA)

- **Code commercial connu** : résout une `ProductReference` ; chaque enregistrement crée une **nouvelle** `ProductInstance` si l’utilisateur enregistre un exemplaire (pas d’unicité d’exemplaire implicite via l’EAN).
- **Code commercial ambigu** : levée de `AmbiguousBarcodeResolutionError` par le port `BarcodeResolutionPort` (aucun succès silencieux).
- **Code interne invalide** : rejet lors de la construction du value object `InternalBarcode` (`InvalidInternalBarcodeError`). Le cas d’usage `RegisterProductByInternalScanUseCase` ne reçoit donc qu’un `InternalBarcode` déjà valide.
- **Code interne valide mais inconnu** : résultat métier `INTERNAL_BARCODE_UNKNOWN` avec `product is None` (pas de matérialisation catalogue implicite).
- **Code interne valide et connu** : issue `EXISTING_PRODUCT` et instance exacte ; `resolved_reference` renseignée lorsque la référence est trouvée en dépôt.

## Résolution référence sans instance

`ResolveProductReferenceFromCommercialBarcodeUseCase` + `CommercialReferenceResolutionResult` pour un lookup catalogue sans persister d’exemplaire.
