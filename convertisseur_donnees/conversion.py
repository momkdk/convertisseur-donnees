"""Conversion CSV <-> JSON, sans dépendance externe.

CSV est toujours traité comme une liste de lignes (dict colonne -> valeur en
texte). JSON est une liste d'objets. La conversion ne devine jamais les types
(nombre, booléen) : c'est le rôle du module `schema` de les vérifier et de
les convertir explicitement si besoin.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


def lire_csv(chemin: str | Path) -> list[dict[str, str]]:
    """Lit un CSV (séparateur , ou ; détecté automatiquement) en liste de dicts."""
    chemin = Path(chemin)
    with chemin.open(newline="", encoding="utf-8-sig") as f:
        extrait = f.read(4096)
        f.seek(0)
        delimiteur = ";" if extrait.count(";") > extrait.count(",") else ","
        lecteur = csv.DictReader(f, delimiter=delimiteur)
        if lecteur.fieldnames is None:
            raise ValueError(f"fichier CSV vide ou sans en-tête : {chemin}")
        return [dict(ligne) for ligne in lecteur]


def ecrire_csv(lignes: list[dict], chemin: str | Path, colonnes: list[str] | None = None) -> None:
    """Écrit une liste de dicts en CSV. Les colonnes sont déduites de la 1ʳᵉ ligne si non précisées."""
    if not lignes:
        raise ValueError("aucune ligne à écrire")
    colonnes = colonnes or list(lignes[0].keys())
    chemin = Path(chemin)
    with chemin.open("w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def csv_vers_json(chemin_csv: str | Path, chemin_json: str | Path, indentation: int = 2) -> int:
    """Convertit un CSV en JSON (liste d'objets). Renvoie le nombre de lignes converties."""
    lignes = lire_csv(chemin_csv)
    Path(chemin_json).write_text(json.dumps(lignes, ensure_ascii=False, indent=indentation), encoding="utf-8")
    return len(lignes)


def json_vers_csv(chemin_json: str | Path, chemin_csv: str | Path) -> int:
    """Convertit un JSON (liste d'objets plats) en CSV. Renvoie le nombre de lignes converties."""
    donnees = json.loads(Path(chemin_json).read_text(encoding="utf-8"))
    if not isinstance(donnees, list) or not all(isinstance(d, dict) for d in donnees):
        raise ValueError("le JSON doit être une liste d'objets (tableau de dictionnaires)")
    if not donnees:
        raise ValueError("le JSON ne contient aucun objet")

    # Toutes les clés rencontrées, dans l'ordre d'apparition, pour ne perdre aucune colonne
    # même si certains objets ont des clés absentes ailleurs.
    colonnes: list[str] = []
    for d in donnees:
        for cle in d:
            if cle not in colonnes:
                colonnes.append(cle)

    lignes = [{c: d.get(c, "") for c in colonnes} for d in donnees]
    ecrire_csv(lignes, chemin_csv, colonnes)
    return len(donnees)
