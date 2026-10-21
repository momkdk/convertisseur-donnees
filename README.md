# convertisseur-donnees

🔗 **Essayer en ligne, gratuitement : [momkdk.github.io/convertisseur-donnees](https://momkdk.github.io/convertisseur-donnees/)**

Conversion **CSV ↔ JSON** et validation de données contre un schéma simple (colonnes
obligatoires, types). Python pur, aucune dépendance, licence MIT. Outil généraliste :
utile à n'importe quel métier qui manipule des tableurs et des fichiers de données.

## Ce qu'il fait

- **Convertir** un CSV en JSON (liste d'objets) ou l'inverse.
- **Valider** un CSV contre un schéma `{colonne: type}` : `texte`, `entier`, `decimal`,
  `booleen`, `date` (AAAA-MM-JJ). Signale les valeurs manquantes et les types incorrects,
  ligne par ligne.

## Utilisation

```
python -m convertisseur_donnees convertir exemples/contacts.csv contacts.json
python -m convertisseur_donnees convertir contacts.json contacts.csv

python -m convertisseur_donnees valider exemples/contacts.csv --schema exemples/schema-contacts.json
```

Exemple de sortie de validation :

```
3 ligne(s) analysée(s), 1 erreur(s)
  ligne 3  colonne 'age'  -> 'trente' n'est pas un entier
```

Dans le code :

```python
from convertisseur_donnees import conversion, schema

lignes = conversion.lire_csv("contacts.csv")
resultat = schema.valider(lignes, {"nom": "texte", "age": "entier"})
if not resultat.valide:
    for e in resultat.erreurs:
        print(e.index, e.colonne, e.message)
```

## Limites à connaître

- La conversion ne devine jamais les types : un CSV lu reste en texte tant qu'il n'est
  pas passé par `schema.valider` / `convertir_valeur`. C'est volontaire, pour éviter les
  surprises silencieuses (ex. un code postal transformé en nombre).
- `json_vers_csv` suppose une liste d'objets **plats** (pas de listes ni d'objets
  imbriqués dans les valeurs).
- Le détecteur de séparateur CSV (`,` ou `;`) est une heuristique simple : un fichier
  inhabituel peut le tromper.

## Tests

```
python -m unittest discover -s tests -v
```

## Auteur

Mohamed Ali El Amri, développeur freelance Python et IA, Cluses (Haute-Savoie).

Licence MIT.
