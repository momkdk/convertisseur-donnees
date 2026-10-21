import json
import tempfile
import unittest
from pathlib import Path

from convertisseur_donnees.conversion import csv_vers_json, ecrire_csv, json_vers_csv, lire_csv


class TestConversion(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_lire_csv_virgule(self):
        chemin = self.racine / "a.csv"
        chemin.write_text("nom,age\nAlice,30\nBob,25\n", encoding="utf-8")
        lignes = lire_csv(chemin)
        self.assertEqual(lignes, [{"nom": "Alice", "age": "30"}, {"nom": "Bob", "age": "25"}])

    def test_lire_csv_point_virgule(self):
        chemin = self.racine / "b.csv"
        chemin.write_text("nom;age\nAlice;30\n", encoding="utf-8")
        lignes = lire_csv(chemin)
        self.assertEqual(lignes, [{"nom": "Alice", "age": "30"}])

    def test_csv_vers_json_aller_retour(self):
        csv_path = self.racine / "a.csv"
        csv_path.write_text("nom,age\nAlice,30\n", encoding="utf-8")
        json_path = self.racine / "a.json"
        n = csv_vers_json(csv_path, json_path)
        self.assertEqual(n, 1)
        donnees = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(donnees, [{"nom": "Alice", "age": "30"}])

    def test_json_vers_csv(self):
        json_path = self.racine / "a.json"
        json_path.write_text(json.dumps([{"nom": "Alice", "age": "30"}]), encoding="utf-8")
        csv_path = self.racine / "a.csv"
        n = json_vers_csv(json_path, csv_path)
        self.assertEqual(n, 1)
        self.assertEqual(lire_csv(csv_path), [{"nom": "Alice", "age": "30"}])

    def test_json_vers_csv_cles_variables(self):
        json_path = self.racine / "a.json"
        json_path.write_text(json.dumps([{"nom": "Alice"}, {"nom": "Bob", "age": "25"}]), encoding="utf-8")
        csv_path = self.racine / "a.csv"
        json_vers_csv(json_path, csv_path)
        lignes = lire_csv(csv_path)
        self.assertEqual(lignes, [{"nom": "Alice", "age": ""}, {"nom": "Bob", "age": "25"}])

    def test_json_vers_csv_vide_leve_erreur(self):
        json_path = self.racine / "vide.json"
        json_path.write_text("[]", encoding="utf-8")
        with self.assertRaises(ValueError):
            json_vers_csv(json_path, self.racine / "out.csv")

    def test_json_vers_csv_format_invalide(self):
        json_path = self.racine / "mauvais.json"
        json_path.write_text('{"pas": "une liste"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            json_vers_csv(json_path, self.racine / "out.csv")

    def test_ecrire_csv_sans_lignes_leve_erreur(self):
        with self.assertRaises(ValueError):
            ecrire_csv([], self.racine / "vide.csv")

    def test_csv_vide_leve_erreur(self):
        chemin = self.racine / "vide.csv"
        chemin.write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            lire_csv(chemin)


if __name__ == "__main__":
    unittest.main()
