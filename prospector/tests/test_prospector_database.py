# Test cases for Prospectors database functions in August 2020
#   created by Daan Hommersom and Antonino Sabetta at SAP
#
# For every function in database.py two test cases are created:
#  - The first one tests cases that should succeed
#  - The second one tests the cases for which an exception should be raised

import pytest, os, sys, ast, json, time, datetime, requests, sqlite3

current_working_directory = os.getcwd()

os.chdir('../git_explorer')
sys.path.append(os.getcwd())

os.environ['GIT_CACHE'] = os.getcwd() + '/git_explorer_cache'
GIT_CACHE = os.environ['GIT_CACHE']

from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir('..')
sys.path.append(os.getcwd())

import database

os.chdir(current_working_directory)

##################################
###
### FIXTURES
###
##################################

@pytest.fixture()
def example_vulnerability():
    example_vulnerability = {
        'vulnerability_id' : 'CVE-2018-1000114',
        'description' : 'An improper authorization vulnerability exists in Jenkins Promoted Builds Plugin 2.31.1 and earlier in Status.java and ManualCondition.java that allow an attacker with read access to jobs to perform promotions.',
        'repo_url': 'https://github.com/jenkinsci/promoted-builds-plugin',
        'nvd_published_timestamp': 1520895600,
        'references' : ['https://jenkins.io/security/advisory/2018-02-26/#SECURITY-746']
    }
    return example_vulnerability

@pytest.fixture()
def example_vulnerability_git_repo(example_vulnerability):
    example_vulnerability_git_repo = Git(example_vulnerability['repo_url'], cache_path=GIT_CACHE)
    example_vulnerability_git_repo.clone(skip_existing=True)
    return example_vulnerability_git_repo

##################################
###
### EXTRACTING AND PROCESSING CONTENT
###
##################################

#
# timestamp_to_timestamp_interval
#

@pytest.mark.database
def test_timestamp_to_timestamp_interval(example_vulnerability):
    assert database.timestamp_to_timestamp_interval(example_vulnerability['nvd_published_timestamp'], days_before=730, days_after=100) == ('1457823600', '1529532000')
    assert database.timestamp_to_timestamp_interval(str(example_vulnerability['nvd_published_timestamp']), days_before=730, days_after=100) == ('1457823600', '1529532000')
    assert database.timestamp_to_timestamp_interval(str(example_vulnerability['nvd_published_timestamp']), days_before='730', days_after='100') == ('1457823600', '1529532000')
    assert database.timestamp_to_timestamp_interval(str(example_vulnerability['nvd_published_timestamp']), days_before=0, days_after=0) == ('1520895600', '1520895600')

#
# get_commit_ids_between_timestamp_interval
#

@pytest.mark.database
def test_get_commit_ids_between_timestamp_interval(example_vulnerability, example_vulnerability_git_repo):
    #with a git_repo provided
    commit_ids_to_add = database.get_commit_ids_between_timestamp_interval(since=1457823600, until=1529532000, git_repo=example_vulnerability_git_repo, repository_url=None)
    assert len(commit_ids_to_add) == 100
    assert commit_ids_to_add[0], commit_ids_to_add[-1] == ('e4c9304553f2868f67556644f5831eba60cf2c34', 'be96e51aa2ba68e0f230ff954a3d47f1c15c7a95')
    
    #without a git_repo provided
    commit_ids_to_add = database.get_commit_ids_between_timestamp_interval(since=1457823600, until=1529532000, git_repo=None, repository_url=example_vulnerability['repo_url'])
    assert len(commit_ids_to_add) == 100
    assert commit_ids_to_add[0], commit_ids_to_add[-1] == ('e4c9304553f2868f67556644f5831eba60cf2c34', 'be96e51aa2ba68e0f230ff954a3d47f1c15c7a95')
    
    #with timestamp as strings
    commit_ids_to_add = database.get_commit_ids_between_timestamp_interval(since='1457823600', until='1529532000', git_repo=example_vulnerability_git_repo, repository_url=None)
    assert len(commit_ids_to_add) == 100
    assert commit_ids_to_add[0], commit_ids_to_add[-1] == ('e4c9304553f2868f67556644f5831eba60cf2c34', 'be96e51aa2ba68e0f230ff954a3d47f1c15c7a95')

@pytest.mark.exception_handling
def test_get_commit_ids_between_timestamp_interval_errors(example_vulnerability, example_vulnerability_git_repo):
    with pytest.raises(ValueError):
        database.get_commit_ids_between_timestamp_interval(since='1457823600', until='1529532000', git_repo=None, repository_url=None)
    with pytest.raises(ValueError):
        database.get_commit_ids_between_timestamp_interval(since='1529532000', until='1457823600', git_repo=None, repository_url=None)

#
# get_hunks_from_diff
#

@pytest.mark.database
def test_get_hunks_from_diff(example_vulnerability_git_repo):
    commit_id = 'e4c9304553f2868f67556644f5831eba60cf2c34'
    diff = Commit(example_vulnerability_git_repo, commit_id)._exec.run(['git', 'diff', '--unified=1', commit_id + "^.." + commit_id])
    assert database.get_hunks_from_diff(diff) == [(6, 8), (11, 13)]
    assert database.get_hunks_from_diff(str(diff)) == [(6, 8), (11, 13)]

@pytest.mark.exception_handling
def test_get_hunks_from_diff_errors(example_vulnerability_git_repo):
    with pytest.raises(TypeError):
        database.get_hunks_from_diff('diff')

#
# get_changed_files_from_diff
#

@pytest.mark.database
def test_get_changed_files_from_diff(example_vulnerability_git_repo):
    commit_id = 'e4c9304553f2868f67556644f5831eba60cf2c34'
    diff = Commit(example_vulnerability_git_repo, commit_id)._exec.run(['git', 'diff', '--unified=1', commit_id + "^.." + commit_id])
    assert database.get_changed_files_from_diff(diff) == ['pom.xml']
    assert database.get_changed_files_from_diff(str(diff)) == ['pom.xml']

@pytest.mark.exception_handling
def test_get_hunks_from_diff_errors(example_vulnerability_git_repo):
    with pytest.raises(TypeError):
        database.get_changed_files_from_diff('diff')

#
# extract_commit_message_reference_content
#

def test_extract_commit_message_reference_content(example_vulnerability):
    # message with a reference
    message = ['Merge pull request #118 from dwnusbaum/add-comments', 'Add comments to clarify the HtmlUnit-based tests in ManualConditionTest']
    reference_content = database.extract_commit_message_reference_content(message, repo_url=example_vulnerability['repo_url'])
    assert len(reference_content) == 1
    assert type(reference_content[0]) == str
    assert len(reference_content[0]) > 0

    # message without a reference
    assert len(database.extract_commit_message_reference_content('message', repo_url=example_vulnerability['repo_url'])) == 0

#
# extract_nvd_content
#

def test_extract_nvd_content(example_vulnerability):
    nvd_content = database.extract_nvd_content(example_vulnerability['vulnerability_id'])
    assert nvd_content[0] == example_vulnerability['description']
    assert nvd_content[1] == example_vulnerability['nvd_published_timestamp']
    assert nvd_content[2] == example_vulnerability['references']

@pytest.mark.exception_handling
def test_extract_nvd_content_errors():
    with pytest.raises(AssertionError):
        database.extract_nvd_content('BLA-BLA-BLA')

##################################
###
### DATABASE
###
##################################

def test_database_creation(example_vulnerability, example_vulnerability_git_repo):
    connection, cursor = database.connect_with_database(':memory:')
    assert type(connection) == sqlite3.Connection
    assert type(cursor) == sqlite3.Cursor
    connection.close()

def test_add_commits_to_database(example_vulnerability, example_vulnerability_git_repo):
    connection, cursor = database.connect_with_database(':memory:')
    commit_ids_to_add = database.get_commit_ids_between_timestamp(since=1457823600, until=1529532000, git_repo=None, repository_url=example_vulnerability['repo_url'])
    database.add_commits_to_database(connection, commit_ids_to_add[:10], git_repo=example_vulnerability_git_repo, repository_url=example_vulnerability['repo_url'], with_message_references=False)
    cursor.execute('SELECT COUNT(id) FROM commits')
    assert cursor.fetchone()['COUNT(id)'] == 10
    
    # verify entries are correct
    cursor.execute('SELECT * FROM commits')
    row = cursor.fetchone()
    
    assert row['repository_url'] == 'https://github.com/jenkinsci/promoted-builds-plugin'
    assert row['id'] == 'e4c9304553f2868f67556644f5831eba60cf2c34'
    assert row['timestamp'] == '1528139978'
    assert row['message'] == "['[maven-release-plugin] prepare for next development iteration']"
    assert row['changed_files'] == "['pom.xml']"
    assert row['diff'] == "['diff --git a/pom.xml b/pom.xml', 'index 3afe9c3..51b568a 100644', '--- a/pom.xml', '+++ b/pom.xml', '@@ -10,3 +10,3 @@', '   <artifactId>promoted-builds</artifactId>', '-  <version>3.2</version>', '+  <version>3.3-SNAPSHOT</version>', '   <packaging>hpi</packaging>', '@@ -41,3 +41,3 @@', '     <url>https://github.com/jenkinsci/${project.artifactId}-plugin</url>', '-    <tag>promoted-builds-3.2</tag>', '+    <tag>HEAD</tag>', '   </scm>']"
    assert row['hunks'] == "[(6, 8), (11, 13)]"
    assert row['commit_message_reference_content'] == None
    assert row['preprocessed_message'] == "maven release plugin prepare development iteration"
    # assert row['preprocessed_diff'] == "artifactid artifact id promote build artifactid artifact id version version version snapshot version packaging hpi packaging url https github com jenkinsci project artifactid artifact id plugin url tag promote build tag tag head tag scm"
    assert row['preprocessed_changed_files'] == "pom.xml pom xml"
    assert row['preprocessed_commit_message_reference_content'] == None

    # test adding without reference content: to speed up the time
    database.add_commits_to_database(connection, commit_ids_to_add[10:20], git_repo=example_vulnerability_git_repo, repository_url=example_vulnerability['repo_url'], with_message_references=False)
    cursor.execute('SELECT COUNT(id) FROM commits')
    assert cursor.fetchone()['COUNT(id)'] == 20

    connection.close()





## create a test database
# CVE-2018-16166
# with open('../scripts/data/vulas_cves.json', 'r') as data_json:
#     vulas_cves = json.load(data_json)
    
# cve = 'CVE-2018-16166'
# repo_url = vulas_cves[cve]['vulas_content']['constructChanges'][0]['repo'].rstrip('.git, /') 
# nvd_published_timestamp = int(time.mktime(datetime.datetime.strptime(vulas_cves[cve]['nvd_content']['publishedDate'].split('T')[0], "%Y-%m-%d").timetuple()))
# nvd_published_timestamp