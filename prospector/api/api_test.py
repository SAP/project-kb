import json

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
    commit_1 = Commit(repository="xxx", commit_id="yyy").__dict__
    commit_2 = Commit(repository="aaa", commit_id="bbb").__dict__
    commits = [commit_1, commit_2]
    response = client.post("/commits/", json=commits)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_commits():
    repository = "xxx"
    commit_id = "yyy"
    response = client.get("/commits/" + repository)
    print(response.json())
    assert response.status_code == 200
    assert json.loads(response.json())[0]["id"] == commit_id
