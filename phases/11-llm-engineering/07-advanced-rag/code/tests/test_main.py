import unittest

import main


class AdvancedRAGExerciseTests(unittest.TestCase):
    def setUp(self):
        self.index = main.build_sample_index(chunk_size=50, overlap=10)

    def test_hybrid_wins_on_at_least_three_test_queries(self):
        rows = main.compare_retrievers_on_test_queries(self.index)
        wins = main.count_top1_wins(rows)
        self.assertGreaterEqual(wins["hybrid"], 3)
        self.assertEqual(len(rows), 5)

    def test_metadata_filter_only_returns_security_chunks(self):
        results = main.metadata_filtered_vector_search(
            "What encryption is used?",
            self.index["embeddings"],
            self.index["vocab"],
            self.index["idf"],
            self.index["metadata"],
            filters={"category": "security"},
            top_k=3,
        )
        self.assertTrue(results)
        categories = {self.index["metadata"][idx]["category"] for idx, _ in results}
        self.assertEqual(categories, {"security"})

    def test_hyde_comparison_reports_direct_and_hyde_hits(self):
        rows = main.compare_direct_vs_hyde(self.index, top_k=3)
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertIn("direct_hit", row)
            self.assertIn("hyde_hit", row)
            self.assertIn("hypothesis", row)
            self.assertGreater(len(row["hypothesis"]), len(row["query"]))

    def test_parent_child_search_returns_parent_context(self):
        contexts = main.parent_child_search_context(
            " ".join(main.SAMPLE_DOCUMENTS),
            "enterprise refund 60 days",
            parent_size=100,
            child_size=30,
            top_k=3,
        )
        self.assertTrue(contexts)
        first = contexts[0]
        self.assertLessEqual(len(first["child"].split()), 30)
        self.assertGreater(len(first["parent"].split()), len(first["child"].split()))

    def test_recall_metrics_include_all_methods_and_cutoffs(self):
        metrics = main.evaluate_advanced_retrievers(self.index)
        self.assertEqual(set(metrics), {"vector", "bm25", "hybrid", "hybrid_rerank"})
        for by_k in metrics.values():
            self.assertEqual(set(by_k), {3, 5, 10})
            for value in by_k.values():
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_recall_bar_renderer_outputs_text_plot(self):
        metrics = {"vector": {3: 0.5}, "hybrid": {3: 1.0}}
        rendered = main.render_recall_bars(metrics)
        self.assertIn("vector", rendered)
        self.assertIn("Recall@3", rendered)
        self.assertIn("hybrid", rendered)


if __name__ == "__main__":
    unittest.main()
