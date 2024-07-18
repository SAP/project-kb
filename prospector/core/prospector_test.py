import subprocess

import pytest

from llm.llm_service import LLMService

from .prospector import prospector

OPENCAST_CVE = "CVE-2021-21318"
OPENCAST_REPO = "https://github.com/opencast/opencast"


# Mock the llm_service configuration object
class Config:
    type: str = None
    model_name: str = None
    temperature: str = None
    ai_core_sk: str = None

    def __init__(self, type, model_name, temperature, ai_core_sk):
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        self.ai_core_sk = ai_core_sk


config = Config("sap", "gpt-4", 0.0, "sk.json")


def test_prospector_client():
    results, _ = prospector(
        vulnerability_id=OPENCAST_CVE,
        repository_url=OPENCAST_REPO,
        version_interval="9.1:9.2",
        git_cache="/tmp/gitcache",
        limit_candidates=5000,
    )
    assert results[0].commit_id == "b18c6a7f81f08ed14884592a6c14c9ab611ad450"


def test_prospector_llm_repo_url():
    LLMService(config)

    results, _ = prospector(
        vulnerability_id=OPENCAST_CVE,
        version_interval="9.1:9.2",
        git_cache="/tmp/gitcache",
        limit_candidates=5000,
        use_llm_repository_url=True,
    )
    assert results[0].commit_id == "b18c6a7f81f08ed14884592a6c14c9ab611ad450"
