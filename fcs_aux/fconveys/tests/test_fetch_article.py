from fconveys.actions.fetch_content.fetch_article import fetch_article_action


def test_fetch_article():
	payload = dict()
	got = fetch_article_action(payload)
	assert "url" in got
