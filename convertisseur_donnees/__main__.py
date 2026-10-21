"""CLI : python -m convertisseur_donnees <convertir|valider> ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .conversion import csv_vers_json, json_vers_csv, lire_csv
from .schema import valider


def _deduire_sens(entree: str, sortie: str) -> str:
    e, s = Path(entree).suffix.lower(), Path(sortie).suffix.lower()
    if e == ".csv" and s == ".json":
        return "csv->json"
    if e == ".json" and s == ".csv":
        return "json->csv"
    raise ValueError("extensions non reconnues : utilisez .csv et .json (dans un sens ou l'autre)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="convertisseur_donnees", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sous = p.add_subparsers(dest="commande", required=True)

    c = sous.add_parser("convertir", help="convertit un CSV en JSON ou un JSON en CSV")
    c.add_argument("entree")
    c.add_argument("sortie")

    v = sous.add_parser("valider", help="valide un CSV contre un schéma JSON {colonne: type}")
    v.add_argument("fichier_csv")
    v.add_argument("--schema", required=True, help="fichier JSON décrivant {colonne: type}")
    v.add_argument(
        "--obligatoires",
        help="liste de colonnes obligatoires séparées par des virgules (défaut : toutes les colonnes du schéma)",
    )

    args = p.parse_args(argv)

    try:
        if args.commande == "convertir":
            sens = _deduire_sens(args.entree, args.sortie)
            if sens == "csv->json":
                n = csv_vers_json(args.entree, args.sortie)
            else:
                n = json_vers_csv(args.entree, args.sortie)
            print(f"{n} ligne(s) converties -> {args.sortie}")
        else:
            schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
            obligatoires = args.obligatoires.split(",") if args.obligatoires else None
            lignes = lire_csv(args.fichier_csv)
            resultat = valider(lignes, schema, obligatoires)
            print(f"{resultat.nb_lignes} ligne(s) analysée(s), {len(resultat.erreurs)} erreur(s)")
            for e in resultat.erreurs:
                print(f"  ligne {e.index + 1}  colonne '{e.colonne}'  -> {e.message}")
            if not resultat.valide:
                return 1
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
