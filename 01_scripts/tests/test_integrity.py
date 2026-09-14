"""Contrôles utiles contre les fuites et les erreurs de résultats exportés."""
import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from src.common import ROOT, FEATURES, TARGETS, DX, DELAYS, NUM, LOG, load_data, get_x


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.raw, self.clean = load_data()
        self.split = pd.read_csv(ROOT / "02_data/processed/split.csv", dtype={"group": str})

    def test_source_and_feature_boundary(self):
        self.assertEqual(self.raw.shape, (858, 36))
        self.assertTrue(self.raw.Biopsy.isin([0, 1]).all())
        self.assertFalse(set(FEATURES) & set(TARGETS + DX + DELAYS))
        self.assertFalse(set(LOG) & set(TARGETS))
        self.assertEqual(int((self.raw["First sexual intercourse"] > self.raw.Age).sum()), 2)
        self.assertFalse((self.clean["First sexual intercourse"] > self.clean.Age).any())

    def test_no_profile_crosses_split_or_validation(self):
        self.assertEqual(set(self.split.source_row), set(range(2, 860)))
        self.assertEqual(self.split.groupby("group").subset.nunique().max(), 1)
        dev = self.split.loc[self.split.subset == "development"]
        self.assertEqual(dev.groupby("group").validation_fold.nunique().max(), 1)
        self.assertEqual(set(dev.validation_fold), {1, 2, 3, 4, 5})
        self.assertTrue(dev.groupby("validation_fold").Biopsy.sum().gt(0).all())

    def test_imputation_uses_development_only(self):
        dev = self.split.loc[self.split.subset == "development", "source_row"].to_numpy() - 2
        x = get_x(self.clean).iloc[dev]
        selection = json.loads((ROOT / "04_results/tables/02_selection.json").read_text())
        for model, settings in selection["parameters"].items():
            stats = pd.read_csv(ROOT / f"04_results/tables/02_imputation_{model}.csv").set_index("feature")
            expected = x[NUM].agg(settings["pre__num__impute__strategy"])
            np.testing.assert_allclose(stats.loc[NUM, "imputed_value_model_space"], expected)

    def test_predictions_and_confusion_counts(self):
        predictions = pd.read_csv(ROOT / "04_results/tables/02_predictions_test.csv")
        metrics = pd.read_csv(ROOT / "04_results/tables/02_metriques_test.csv")
        actual = self.clean.Biopsy.iloc[predictions.source_row.to_numpy() - 2].to_numpy()
        np.testing.assert_array_equal(predictions.Biopsy, actual)
        for _, row in metrics.iterrows():
            p = predictions[f"score_{row.model}"].to_numpy()
            self.assertTrue(np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all())
            predicted = p >= row.threshold
            tp = int(((actual == 1) & predicted).sum())
            fp = int(((actual == 0) & predicted).sum())
            self.assertEqual(tp, row.TP)
            self.assertEqual(fp, row.FP)
            self.assertEqual(row.TN + row.FP + row.FN + row.TP, len(actual))

    def test_cluster_outputs_cover_exactly_the_same_rows(self):
        a = pd.read_csv(ROOT / "04_results/tables/03_affectations.csv")
        self.assertEqual(a.source_row.nunique(), 858)
        joined = a.merge(self.split, on="source_row", suffixes=("_cluster", "_split"))
        self.assertTrue(joined.subset_cluster.eq(joined.subset_split).all())
        self.assertTrue(joined.Biopsy_cluster.eq(joined.Biopsy_split).all())


if __name__ == "__main__":
    unittest.main()
