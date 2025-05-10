from main import search_reddit  # adjust import as needed

def test_search_reddit_success():
    results = search_reddit("AI", limit=2)
    assert isinstance(results, list), "Expected list of results"
    assert len(results) <= 2, "Limit exceeded"
    for post in results:
        assert "title" in post
        assert "url" in post
        assert "comments" in post

def test_search_reddit_no_results():
    results = search_reddit("nonsensequerythatshouldfail12345", limit=2)
    assert isinstance(results, list), "Expected a list"
    assert len(results) == 0, "Expected empty result list for invalid query"
