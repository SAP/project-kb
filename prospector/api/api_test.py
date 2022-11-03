from fastapi.testclient import TestClient

from api.main import app
from datamodel.commit import Commit

client = TestClient(app)


# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert "<title>Prospector</title>" in response.text


def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_preprocessed_commits():
    commit_1 = Commit(
        repository="https://github.com/apache/dubbo", commit_id="yyy"
    ).as_dict()
    commit_2 = Commit(
        repository="https://github.com/apache/dubbo", commit_id="zzz"
    ).as_dict()
    commit_3 = Commit(
        repository="https://github.com/apache/struts", commit_id="bbb"
    ).as_dict()
    commits = [commit_1, commit_2, commit_3]
    response = client.post("/commits/", json=commits)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_specific_commit():
    repository = "https://github.com/apache/dubbo"
    commit_id = "yyy"
    response = client.get("/commits/" + repository + "?commit_id=" + commit_id)
    assert response.status_code == 200
    assert response.json()[0]["commit_id"] == commit_id


# @pytest.mark.skip(reason="will raise exception")
def test_get_commits_by_repository():
    repository = "https://github.com/apache/dubbo"
    response = client.get("/commits/" + repository)
    assert response.status_code == 200
    assert response.json()[0]["commit_id"] == "yyy"
    assert response.json()[1]["commit_id"] == "zzz"
