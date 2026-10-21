"""Validation de données contre un schéma simple : colonnes obligatoires et types.

Le schéma est un dict {nom_colonne: type}, type parmi :
"texte", "entier", "decimal", "booleen", "date" (AAAA-MM-JJ).

Conçu pour valider un CSV ou un JSON déjà chargé en liste de dicts, avant de
les utiliser dans un programme : repère les lignes qui ne respectent pas le
format attendu plutôt que de planter plus loin avec une erreur confuse.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

TYPES_VALIDES = {"texte", "entier", "decimal", "booleen", "date"}
_RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VRAI = {"1", "true", "vrai", "oui", "yes"}
_FAUX = {"0", "false", "faux", "non", "no"}


@dataclass(frozen=True)
class ErreurLigne:
    index: int
    colonne: str
    message: str


@dataclass(frozen=True)
class ResultatValidation:
    nb_lignes: int
    erreurs: list[ErreurLigne] = field(default_factory=list)

    @property
    def valide(self) -> bool:
        return not self.erreurs


def _verifier_type(valeur: str, type_attendu: str) -> str | None:
    """Renvoie un message d'erreur si la valeur ne correspond pas au type, sinon None."""
    if type_attendu == "texte":
        return None
    if type_attendu == "entier":
        try:
            int(valeur)
        except ValueError:
            return f"'{valeur}' n'est pas un entier"
        return None
    if type_attendu == "decimal":
        try:
            float(valeur.replace(",", "."))
        except ValueError:
            return f"'{valeur}' n'est pas un nombre décimal"
        return None
    if type_attendu == "booleen":
        if valeur.strip().lower() not in _VRAI | _FAUX:
            return f"'{valeur}' n'est pas un booléen reconnu (vrai/faux, oui/non, 1/0)"
        return None
    if type_attendu == "date":
        if not _RE_DATE.match(valeur.strip()):
            return f"'{valeur}' n'est pas une date au format AAAA-MM-JJ"
        return None
    raise ValueError(f"type de schéma inconnu : {type_attendu}")


def valider(lignes: list[dict], schema: dict[str, str], colonnes_obligatoires: list[str] | None = None) -> ResultatValidation:
    """Valide une liste de dicts contre un schéma {colonne: type}.

    `colonnes_obligatoires` (sous-ensemble des clés du schéma) doit être non vide
    sur chaque ligne ; si omis, toutes les colonnes du schéma sont obligatoires.
    """
    inconnus = set(schema.values()) - TYPES_VALIDES
    if inconnus:
        raise ValueError(f"type(s) de schéma inconnu(s) : {', '.join(sorted(inconnus))}")

    obligatoires = colonnes_obligatoires if colonnes_obligatoires is not None else list(schema.keys())
    erreurs: list[ErreurLigne] = []

    for i, ligne in enumerate(lignes):
        for colonne in obligatoires:
            if colonne not in ligne or str(ligne[colonne]).strip() == "":
                erreurs.append(ErreurLigne(i, colonne, "valeur manquante"))

        for colonne, type_attendu in schema.items():
            valeur = ligne.get(colonne)
            if valeur is None or str(valeur).strip() == "":
                continue  # déjà signalé ci-dessus si obligatoire
            message = _verifier_type(str(valeur), type_attendu)
            if message:
                erreurs.append(ErreurLigne(i, colonne, message))

    return ResultatValidation(len(lignes), erreurs)


def convertir_valeur(valeur: str, type_cible: str) -> object:
    """Convertit une valeur texte vers le type Python correspondant (après validation)."""
    if type_cible == "texte":
        return valeur
    if type_cible == "entier":
        return int(valeur)
    if type_cible == "decimal":
        return float(valeur.replace(",", "."))
    if type_cible == "booleen":
        return valeur.strip().lower() in _VRAI
    if type_cible == "date":
        return valeur.strip()
    raise ValueError(f"type de schéma inconnu : {type_cible}")
