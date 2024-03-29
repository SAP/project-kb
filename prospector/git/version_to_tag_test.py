import pytest

from git.version_to_tag import get_possible_tags


@pytest.fixture
def tags():
    return [
        "0.9-beta1",
        "docker-plugin-0.1",
        "docker-plugin-0.10.0",
        "docker-plugin-0.10.1",
        "docker-plugin-0.10.2",
        "docker-plugin-0.11.0",
        "docker-plugin-0.12.0",
        "docker-plugin-0.12.1",
        "docker-plugin-0.13.0",
        "docker-plugin-0.14.0",
        "docker-plugin-0.15.0",
        "docker-plugin-0.3.1",
        "docker-plugin-0.3.2",
        "docker-plugin-0.3.3",
        "docker-plugin-0.3.4",
        "docker-plugin-0.3.5",
        "docker-plugin-0.4",
        "docker-plugin-0.5",
        "docker-plugin-0.6",
        "docker-plugin-0.6.1",
        "docker-plugin-0.6.2",
        "docker-plugin-0.7",
        "docker-plugin-0.8",
        "docker-plugin-0.9.0-beta2",
        "docker-plugin-0.9.0-rc1",
        "docker-plugin-0.9.1",
        "docker-plugin-0.9.2",
        "docker-plugin-0.9.3",
        "docker-plugin-0.9.4",
        "docker-plugin-1.1",
        "docker-plugin-1.1.1",
        "docker-plugin-1.1.2",
        "docker-plugin-1.1.3",
        "docker-plugin-1.1.4",
        "docker-plugin-1.1.5",
        "docker-plugin-1.1.6",
        "docker-plugin-1.1.7",
        "docker-plugin-1.1.8",
        "docker-plugin-1.1.9",
        "docker-plugin-1.2.0",
        "docker-plugin-1.2.1",
        "docker-plugin-1.2.2",
        "docker-plugin-parent-0.16.0",
        "docker-plugin-parent-0.16.1",
        "docker-plugin-parent-0.16.2",
        "docker-plugin-parent-0.17",
        "docker-plugin-parent-0.18",
        "docker-plugin-parent-0.9.0",
        "docker-plugin-parent-1.0.0",
        "docker-plugin-parent-1.0.1",
        "docker-plugin-parent-1.0.2",
        "docker-plugin-parent-1.0.3",
        "docker-plugin-parent-1.0.4",
        "libvirt-slave-1.7",
        "libvirt-slave-1.8",
        "libvirt-slave-1.8.1",
    ]


def test_get_possible_tags(tags):
    prev, next = get_possible_tags(tags, "1.1.4:1.1.6")
    assert prev == "docker-plugin-1.1.4" and next == "docker-plugin-1.1.6"
