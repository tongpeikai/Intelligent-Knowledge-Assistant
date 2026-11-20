from scripts.evaluate_rag import evaluate


def test_metrics_use_only_labeled_relevance(monkeypatch):
    cases = [
        {"id": "a", "category": "x", "query": "q", "relevant_sources": ["a.md"]},
        {"id": "n", "category": "no", "query": "none", "relevant_sources": []},
    ]
    def fake_search(query, top_k, max_distance, expand_bilingual=True):
        if query == "none" and max_distance == 0.5:
            return []
        return [{"source": "a.md", "distance": 0.1}, {"source": "b.md", "distance": 0.2}]
    monkeypatch.setattr("scripts.evaluate_rag.search_documents", fake_search)
    result = evaluate(cases, top_k=2)
    assert result["recall_at_k"] == 1
    assert result["precision_at_k"] == 0.5
    assert result["mrr"] == 1
    assert result["no_answer_rejection"] == 1
