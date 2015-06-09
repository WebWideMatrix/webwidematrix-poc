from fconveys.actions.fetch_content.fetch_article import fetch_article_action


def test_fetch_article():
    payload = {
        "urls": [
            {
                "expanded_url": "https://medium.com/@intercom/the-dribbblisation-of-design-406422ccb026",
                "display_url": "medium.com/@intercom/dribbalization...",
                "url": "https://t.co/d3bdjb"
            }
        ]
    }
    got = fetch_article_action(payload)
    assert len(got) == 1
    got = got[0]
    assert "content_type" in got
    assert got["content_type"] == "article-text"
    assert "payload" in got
    assert "text" in got["payload"]
    assert "Things that use real data." in got["payload"]["text"]
    print got
