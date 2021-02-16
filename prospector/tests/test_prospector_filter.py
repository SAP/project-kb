# Test cases for Prospectors mapping functions in July 2020
#   created by Daan Hommersom and Antonino Sabetta at SAP
#
# For every function in prospector/map.py two test cases are created:
#  - The first one tests cases that should succeed
#  - The second one tests the cases for which an exception should be raised

import pytest, os, sys, json, random

current_working_directory = os.getcwd()

os.chdir('../../prospector')
sys.path.insert(1, '../prospector')

import filter
import database_creation

os.chdir(current_working_directory)

os.chdir('../../database_creation')
sys.path.insert(1, '../database_creation')

GIT_CACHE = '/mnt/c/Users/I537960/Documents/git_explorer_cache'
os.environ['GIT_CACHE'] = '/mnt/c/Users/I537960/Documents/git_explorer_cache'

from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

##################################
###
### FIXTURES
###
##################################

@pytest.fixture()
def example_advisory_record():
    example_advisory_record = {
        'vulas_id': 1038,
        'cve': 'CVE-2019-10342',
        'description': "A missing permission check in Jenkins Docker Plugin 1.1.6 and earlier in various 'fillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins.",
        'fix_commit': '6ad27199f6fad230be72fd45da78ddac85c075db',
        'repo_url': 'https://github.com/jenkinsci/docker-plugin/',
        'n_tags' : 54,
        'fix_commit_tag': 'docker-plugin-1.1.7',
        'n_candidate_commits' : 21,
    }
    return example_advisory_record

@pytest.fixture()
def git_repo(example_advisory_record):
    git_repo = Git(example_advisory_record['repo_url'], cache_path=GIT_CACHE)
    git_repo.clone(skip_existing=True)
    return git_repo
   
@pytest.fixture()
def tags(git_repo):
    tags = git_repo.get_tags()
    return tags

def test_initialization(example_advisory_record, git_repo, tags):
    assert type(example_advisory_record) == dict
    assert type(git_repo) == Git
    assert len(tags) >= 54

##################################
###
### EXTRACT
###
##################################

# @pytest.mark.API
# def test_class_Advisory():
#     global test_CVE

#     test_CVE = prospector.Advisory('https://nvd.nist.gov/vuln/detail/CVE-2020-1928')
#     assert type(test_CVE) == prospector.Advisory

# @pytest.mark.API
# @pytest.mark.parametrize('url, error', [
#     (['https://nvd.nist.gov/vuln/detail/CVE-2020-1928'], ValueError),
#     ('https://nvd.nist.gov/vuln/detail/CVE-2020-19282605', RuntimeError)
# ])
# def test_create_advisory_record_errors(url, error):
#     with pytest.raises(error):
#         extract.create_advisory_record_from_url(url)

# @pytest.mark.API
# def test_create_advisory_record():
#     test_CVE.advisory_record = extract.create_advisory_record_from_url(test_CVE.advisory_url)
#     assert test_CVE.advisory_record['cve']['CVE_data_meta']['ID'] == 'CVE-2020-1928'

##################################
###
### RETREIVE TAGS
###
##################################


#
# filter description
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('n_relevant_sentences, description', [
    (0, 'A string without a version should not be a problem!'),
    (1, "A missing permission check in Jenkins Docker Plugin 1.1.6 and earlier in various 'fillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins."),
    (1, 'This is an example. From this description the following should be returned: v1.2, 4.7.RC2, and version-3.2-RC1. Version-1.x and v-2.1.X not.'),
])
def test_filter_description(n_relevant_sentences, description):
    assert n_relevant_sentences == len(filter.filter_description(description))

@pytest.mark.exception_handling
@pytest.mark.parametrize('description, error', [
    (['This is an example.', 'From this description the following should be returned: v1.2, 4.7.RC2, and version-3.2-RC1.', 'Version-1.x and v-2.1.X not.'], TypeError)
])
def test_filter_description_errors(description, error):
    with pytest.raises(error):
        filter.filter_description(description)


#
# retreive_all_versions_from_description
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('versions, description', [
    ([], 'A string without a version should not be a problem!'),
    (['1.1.6'], "A missing permission check in Jenkins Docker Plugin 1.1.6 and earlier in various 'fillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins."),
    (['v1.2', '4.7.RC2', 'version-3.2-RC1'], 'This is an example. From this description the following should be returned: v1.2, 4.7.RC2, and version-3.2-RC1. Version-1.x and v-2.1.X not.'),
])
def test_retreive_all_versions_from_description(versions, description):
    assert versions == filter.retreive_all_versions_from_description(description)

@pytest.mark.exception_handling
@pytest.mark.parametrize('description, error', [
    (['This', 'is', 'wrong'], TypeError)
])
def test_retreive_all_versions_from_description_errors(description, error):
    with pytest.raises(error):
        filter.recursively_split_version_string(description)


#
# recursively_split_version_string
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('input_version, result', [
    ('v2.10.0.Final', ['v', 2, '.', 10, '.', 0, '.Final']),
    ('4.1.M1', [4, '.', 1, '.M', 1]),
    ('1.1.6', [1, '.', 1, '.', 6])
])
def test_recursively_split_version_string(input_version, result):
    assert filter.recursively_split_version_string(input_version) == result

@pytest.mark.exception_handling
@pytest.mark.parametrize('input_version, error', [
    ([1, '.', 1, '.', 6], TypeError)
])
def test_recursively_split_version_string_errors(input_version, error):
    with pytest.raises(error):
        filter.recursively_split_version_string(input_version)


#
# get tag for version
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('version, tag', [
    ('0.1', 'docker-plugin-0.1'),
    # ('1.2', 'docker-plugin-1.2.0'),
    ('1.8', 'libvirt-slave-1.8')
])
def test_get_tag_for_version(version, tag, tags):
    # returns a list of tags that could be corresponding to the version
    assert tag in filter.get_tag_for_version(tags, version)

@pytest.mark.exception_handling
@pytest.mark.parametrize('version, error', [
    (['version-1.8'], TypeError),
])
def test_get_tag_for_version_errors(version, error, tags):
    with pytest.raises(error):
        filter.get_tag_for_version(tags, version)

# no feature to parametrize a fixture, thus testing an empty 'tags' this way
@pytest.mark.exception_handling
def test_get_tag_for_version_errors_2(tags=[]):
    with pytest.raises(ValueError):
        filter.get_tag_for_version(tags, 'version-1.8')


# 
# get_timestamp_for_tag
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('tag, timestamp', [
    ('0.9-beta1', 1426785331),
])
def test_get_timestamp_for_tag(tag, timestamp, git_repo):
    assert filter.get_timestamp_for_tag(tag, git_repo) == timestamp

@pytest.mark.exception_handling
@pytest.mark.parametrize('tag, error', [
    (1, TypeError),
    ('invalid-tag', ValueError)
])
def test_get_timestamp_for_tag_errors(tag, error, git_repo):
    with pytest.raises(error):
        filter.get_timestamp_for_tag(tag, git_repo)

# no feature to parametrize a fixture, thus testing an invalid 'git_repo' this way
def test_get_timestamp_for_tag_errors_2(git_repo='no-git-repo'):
    with pytest.raises(TypeError):
        filter.get_timestamp_for_tag('0.9-beta1', git_repo)


#
# find next tags
#

@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('tag, next_tag', [
    # ('docker-plugin-0.1', 'docker-plugin-0.3.1'), # should probably be 'docker-plugin-0.3.1', but 0.4 is also fine
    # ('docker-plugin-1.1', 'docker-plugin-1.1.1'), # or 'docker-plugin-1.2.0'
    ('docker-plugin-0.10.2', 'docker-plugin-0.11.0'),
    ('docker-plugin-1.1.1', 'docker-plugin-1.1.2'), # or 'docker-plugin-1.2.0'
    # ('libvirt-slave-1.8', 'libvirt-slave-1.8.1'),
    ('docker-plugin-0.9.0-beta2', 'docker-plugin-0.9.1')
])
def test_find_next_tag(tag, next_tag, tags, git_repo):
    assert filter.find_next_tag(tag, tags, None, git_repo) == next_tag

@pytest.mark.exception_handling
@pytest.mark.parametrize('tag, error', [
    (1, TypeError),
    ('invalid-tag', ValueError)
])
def test_find_next_tag_errors(tag, error, tags, git_repo):
    with pytest.raises(error):
        filter.find_next_tag(tag, tags, None, git_repo)

# no feature to parametrize a fixture, thus testing an invalid 'git_repo' this way
@pytest.mark.exception_handling
def test_find_next_tag_errors_2(tags, git_repo='no-git-repo'):
    with pytest.raises(TypeError):
        filter.find_next_tag('docker-plugin-1.1.1', tags, None, git_repo)

# no feature to parametrize a fixture, thus testing an empty 'tags' this way
@pytest.mark.exception_handling
def test_find_next_tag_errors_3(git_repo, tags=[]):
    with pytest.raises(ValueError):
        filter.find_next_tag('docker-plugin-1.1.1', tags, None, git_repo)


#
# find previous tags
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('previous_tag, tag', [
    # ('docker-plugin-0.1', 'docker-plugin-0.3.1'), # should probably be 'docker-plugin-0.3.1', but 0.4 is also fine
    # ('docker-plugin-1.1', 'docker-plugin-1.1.1'), # or 'docker-plugin-1.2.0'
    ('docker-plugin-0.10.2', 'docker-plugin-0.11.0'),
    ('docker-plugin-1.1.1', 'docker-plugin-1.1.2'), # or 'docker-plugin-1.2.0'
    # ('libvirt-slave-1.8', 'libvirt-slave-1.8.1'),
    ('docker-plugin-0.6.2', 'docker-plugin-0.9.1'), #should be 'docker-plugin-0.9.0-beta2', or 0.8
])
def test_find_previous_tag(previous_tag, tag, tags, git_repo):
    assert filter.find_previous_tag(tag, tags, None, git_repo) == previous_tag

@pytest.mark.exception_handling
@pytest.mark.parametrize('tag, error', [
    (1, TypeError),
    ('invalid-tag', ValueError)
])
def test_find_find_previous_tag_errors(tag, error, tags, git_repo):
    with pytest.raises(error):
        filter.find_previous_tag(tag, tags, None, git_repo)

# no feature to parametrize a fixture, thus testing an invalid 'git_repo' this way
@pytest.mark.exception_handling
def test_find_previous_tag_errors_2(tags, git_repo='no-git-repo'):
    with pytest.raises(TypeError):
        filter.find_previous_tag('docker-plugin-1.1.1', tags, None, git_repo)

# no feature to parametrize a fixture, thus testing an empty 'tags' this way
@pytest.mark.exception_handling
def test_find_previous_tag_errors_3(git_repo, tags=[]):
    with pytest.raises(ValueError):
        filter.find_previous_tag('docker-plugin-1.1.1', tags, None, git_repo)


#
# version_to_wide_interval_tags
#


@pytest.mark.mapping_onto_tags
@pytest.mark.parametrize('version, interval_tag_1, interval_tag_2', [
    ('1.1.6', ('docker-plugin-1.1.5', 'docker-plugin-1.1.6'), ('docker-plugin-1.1.6', 'docker-plugin-1.1.7'))
])
def test_version_to_wide_interval_tags(version, interval_tag_1, interval_tag_2, tags, git_repo):
    wide_interval_tags = filter.version_to_wide_interval_tags(tags, version, git_repo)
    assert interval_tag_1 in wide_interval_tags and interval_tag_2 in wide_interval_tags

# no feature to parametrize a fixture, thus testing an invalid 'git_repo' this way
@pytest.mark.exception_handling
def test_version_to_wide_interval_tags_errors(tags, git_repo='no-git-repo'):
    with pytest.raises(TypeError):
        filter.version_to_wide_interval_tags(tags, '1.1.6', git_repo)

# no feature to parametrize a fixture, thus testing an empty 'tags' this way
@pytest.mark.exception_handling
def test_version_to_wide_interval_tags_errors_2(git_repo, tags=[]):
    with pytest.raises(ValueError):
        filter.version_to_wide_interval_tags(tags, '1.1.6', git_repo)

##################################
###
### MAP ONTO CANDIDATE COMMITS
###
##################################


#
# get_commits_between_interval_tags
#


@pytest.mark.integration_test
def test_get_commits_between_interval_tags(example_advisory_record, git_repo):
    intervals_tags = [('docker-plugin-1.1.5', 'docker-plugin-1.1.6'), ('docker-plugin-1.1.6', 'docker-plugin-1.1.7')]
    candidate_commits = filter.get_commits_between_interval_tags(intervals_tags, git_repo=None, repo_url=example_advisory_record['repo_url'])
    assert example_advisory_record['fix_commit'] in candidate_commits
    assert example_advisory_record['n_candidate_commits'] == len(candidate_commits)

#without git_repo provided
@pytest.mark.integration_test
def test_get_commits_between_interval_tags_2(example_advisory_record):
    intervals_tags = [('docker-plugin-1.1.5', 'docker-plugin-1.1.6'), ('docker-plugin-1.1.6', 'docker-plugin-1.1.7')]
    candidate_commits = filter.get_commits_between_interval_tags(intervals_tags, git_repo=None, repo_url=example_advisory_record['repo_url'])
    assert example_advisory_record['fix_commit'] in candidate_commits
    assert example_advisory_record['n_candidate_commits'] == len(candidate_commits)

@pytest.mark.exception_handling
def test_get_commits_between_interval_tags_errors(repo_url='no-git-repo-url'):
    intervals_tags = [('docker-plugin-1.1.5', 'docker-plugin-1.1.6'), ('docker-plugin-1.1.6', 'docker-plugin-1.1.7')]
    with pytest.raises(TypeError):
        filter.get_commits_between_interval_tags(intervals_tags, git_repo=None, repo_url=repo_url)


#
# map_advisory_record_onto_candidate_commits
#


@pytest.mark.integration_test
def test_map_advisory_record_onto_candidate_commits(example_advisory_record):
    candidate_commits = filter.map_advisory_record_onto_candidate_commits(example_advisory_record)
    assert example_advisory_record['fix_commit'] in candidate_commits
    assert example_advisory_record['n_candidate_commits'] == len(candidate_commits)

@pytest.mark.exception_handling
def test_map_advisory_record_onto_candidate_commits_errors(advisory_record=dict()):
    with pytest.raises(ValueError):
        filter.map_advisory_record_onto_candidate_commits(advisory_record)


#
# filter_commits_on_files_changed_extensions
#


@pytest.mark.filter
def test_filter_commits_on_files_changed_extensions(example_advisory_record):
    prospector_connection, prospector_cursor = database_creation.connect_with_database('../data/prospector-commits.db')
    candidate_commits = filter.map_advisory_record_onto_candidate_commits(example_advisory_record)
    assert len(filter.filter_commits_on_files_changed_extensions(candidate_commits, prospector_connection, prospector_cursor)) == 11
