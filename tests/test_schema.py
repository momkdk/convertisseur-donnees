import unittest

from convertisseur_donnees.schema import convertir_valeur, valider


class TestSchema(unittest.TestCase):
    def test_tout_valide(self):
        lignes = [{"nom": "Alice", "age": "30", "actif": "oui", "inscrit_le": "2026-01-15"}]
        schema = {"nom": "texte", "age": "entier", "actif": "booleen", "inscrit_le": "date"}
        r = valider(lignes, schema)
        self.assertTrue(r.valide)
        self.assertEqual(r.erreurs, [])

    def test_entier_invalide(self):
        lignes = [{"nom": "Alice", "age": "trente"}]
        schema = {"nom": "texte", "age": "entier"}
        r = valider(lignes, schema)
        self.assertFalse(r.valide)
        self.assertEqual(r.erreurs[0].colonne, "age")

    def test_decimal_avec_virgule(self):
        lignes = [{"prix": "12,50"}]
        schema = {"prix": "decimal"}
        r = valider(lignes, schema)
        self.assertTrue(r.valide)

    def test_date_invalide(self):
        lignes = [{"date": "15/01/2026"}]
        schema = {"date": "date"}
        r = valider(lignes, schema)
        self.assertFalse(r.valide)

    def test_colonne_manquante_obligatoire(self):
        lignes = [{"nom": "Alice"}]
        schema = {"nom": "texte", "age": "entier"}
        r = valider(lignes, schema)
        self.assertFalse(r.valide)
        self.assertTrue(any(e.colonne == "age" and "manquante" in e.message for e in r.erreurs))

    def test_colonnes_obligatoires_restreintes(self):
        lignes = [{"nom": "Alice"}]  # age absent mais pas obligatoire ici
        schema = {"nom": "texte", "age": "entier"}
        r = valider(lignes, schema, colonnes_obligatoires=["nom"])
        self.assertTrue(r.valide)

    def test_type_schema_inconnu_leve_erreur(self):
        with self.assertRaises(ValueError):
            valider([{"x": "1"}], {"x": "nombre_romain"})

    def test_booleens_reconnus(self):
        for valeur in ["1", "0", "true", "false", "vrai", "faux", "oui", "non"]:
            r = valider([{"actif": valeur}], {"actif": "booleen"})
            self.assertTrue(r.valide, msg=f"'{valeur}' devrait être reconnu comme booléen")

    def test_convertir_valeur(self):
        self.assertEqual(convertir_valeur("30", "entier"), 30)
        self.assertEqual(convertir_valeur("12,5", "decimal"), 12.5)
        self.assertIs(convertir_valeur("oui", "booleen"), True)
        self.assertIs(convertir_valeur("non", "booleen"), False)
        self.assertEqual(convertir_valeur("Alice", "texte"), "Alice")


if __name__ == "__main__":
    unittest.main()
