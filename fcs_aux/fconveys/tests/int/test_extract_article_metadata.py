from fconveys.actions.extract_metadata.extract_article_metadata import extract_article_metadata_action


def test_extract_article_metadata():
    payload = {
        "url": "https://medium.com/@intercom/the-dribbblisation-of-design-406422ccb026",
    }
    got = extract_article_metadata_action(payload)
    assert len(got) == 1
    got = got[0]
    assert "payload" in got
    assert "title" in got["payload"]
    assert "The Dribbblisation of Design" == got["payload"]["title"]
    assert "site" in got["payload"]
    assert "Medium" == got["payload"]["site"]
    assert "image_url" in got["payload"]
    assert len(got["payload"]["image_url"]) > 0
