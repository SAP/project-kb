from fastapi.testclient import TestClient
from datamodel.commit import Commit


from api.main import app

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
