import pytest, re, os, json, sqlite3, requests, time, datetime, ast, random, copy, sys
import numpy as np
import pandas as pd

current_working_directory = os.getcwd()

os.chdir('../git_explorer')
sys.path.append(os.getcwd())

os.environ['GIT_CACHE'] = os.getcwd() + '/git_explorer_cache'
GIT_CACHE = os.environ['GIT_CACHE']

from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir('..')
sys.path.append(os.getcwd())

import database
import filter
import rank
import main

os.chdir(current_working_directory)
sys.path.insert(1, '../experiment/tests')

############
@pytest.fixture()
def example_vulnerability():
    example_vulnerability = {
        'vulnerability_id' : 'CVE-2018-16166',
        'description' : 'LogonTracer 1.2.0 and earlier allows remote attackers to conduct XML External Entity (XXE) attacks via unspecified vectors.',
        'repo_url' : 'https://github.com/JPCERTCC/LogonTracer',
        'nvd_published_timestamp' : 1546988400,
        'nvd_references' : ['https://github.com/JPCERTCC/LogonTracer/releases/tag/v1.2.1', 'https://jvn.jp/en/vu/JVNVU98026636/index.html'],
        'fix_commits' : ['2bb79861dbaf7e8a9646fcd70359523fdb464d9c'],
        'project_name' : 'github JPCERTCC LogonTracer',
        'nvd_reference_content' : 'git GitHub hub cve-2018 logon tracer vulnerability jpcert base score cookie cvss av ac sign code use learn product release',
        'preprocessed_description' : 'LogonTracer logon tracer early allow remote attacker conduct xml external entity xxe attack unspecified vector'
    }
    return example_vulnerability

# databases are created in the notebook database_creation.ipynb
vulnerabilities_connection, vulnerabilities_cursor = database.connect_with_vulnerabilities_database('test-vulnerabilities.db')
prospector_connection, prospector_cursor = database.connect_with_database('test-commits.db')

@pytest.mark.database
def test_database_coverage(example_vulnerability):
    database.add_vulnerabiliy_to_database(vulnerabilities_connection, example_vulnerability['vulnerability_id'], example_vulnerability['repo_url'], example_vulnerability['description'], str(example_vulnerability['nvd_published_timestamp']))
    assert vulnerabilities_cursor.execute("SELECT COUNT(vulnerability_id) FROM vulnerabilities WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']}).fetchone()['COUNT(vulnerability_id)'] == 1

    database.add_vulnerability_references_to_database(vulnerabilities_connection, example_vulnerability['vulnerability_id'], example_vulnerability['nvd_references'])
    assert vulnerabilities_cursor.execute("SELECT COUNT(url) FROM vulnerability_references WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']}).fetchone()['COUNT(url)'] == 2
    assert vulnerabilities_cursor.execute("SELECT COUNT(url) FROM advisory_references WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']}).fetchone()['COUNT(url)'] == 35

    database.add_vulnerability_fixes_to_database(vulnerabilities_connection, example_vulnerability['vulnerability_id'], example_vulnerability['fix_commits'], example_vulnerability['repo_url'])
    assert vulnerabilities_cursor.execute("SELECT COUNT(commit_id) FROM fix_commits WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']}).fetchone()['COUNT(commit_id)'] == 1

@pytest.mark.database
def test_extracting_reference_content(example_vulnerability):
    vulnerabilities_cursor.execute("SELECT url, preprocessed_content FROM vulnerability_references WHERE vulnerability_id = :vulnerability_id", {'vulnerability_id': example_vulnerability['vulnerability_id']})
    nvd_references = {nvd_reference['url'] : nvd_reference['preprocessed_content'] for nvd_reference in vulnerabilities_cursor}
    nvd_references_content = rank.extract_n_most_occurring_words(rank.remove_project_name_from_string(example_vulnerability['project_name'], ' '.join(nvd_references.values())), n=20)
    assert len(nvd_references_content.split(' ')) == 20

@pytest.mark.database
def test_commit_coverage(example_vulnerability):
    vulnerabilities_cursor.execute("SELECT url FROM advisory_references WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']})
    advisory_references = [reference['url'] for reference in vulnerabilities_cursor]

    advisory_record = rank.Advisory_record(
        vulnerability_id = example_vulnerability['vulnerability_id'],
        published_timestamp = example_vulnerability['nvd_published_timestamp'],
        repo_url = example_vulnerability['repo_url'],
        nvd_references = example_vulnerability['nvd_references'],
        advisory_references = advisory_references,
        vulnerability_description = example_vulnerability['description'],
        connection =  prospector_connection,
        preprocessed_vulnerability_description = example_vulnerability['preprocessed_description'] + example_vulnerability['nvd_reference_content']
    )
    advisory_record.gather_candidate_commits()
    assert len(advisory_record.candidate_commits) == 54

@pytest.mark.ranking
def test_ranking(example_vulnerability):
    vulnerabilities_cursor.execute("SELECT url FROM advisory_references WHERE vulnerability_id = :vulnerability_id;", {'vulnerability_id':example_vulnerability['vulnerability_id']})
    advisory_references = [reference['url'] for reference in vulnerabilities_cursor]

    advisory_record = rank.Advisory_record(
        vulnerability_id = example_vulnerability['vulnerability_id'],
        published_timestamp = example_vulnerability['nvd_published_timestamp'],
        repo_url = example_vulnerability['repo_url'],
        nvd_references = example_vulnerability['nvd_references'],
        advisory_references = advisory_references,
        vulnerability_description = example_vulnerability['description'],
        connection =  prospector_connection,
        preprocessed_vulnerability_description = example_vulnerability['preprocessed_description'] + example_vulnerability['nvd_reference_content']
    )

    advisory_record.gather_candidate_commits()
    advisory_record.ranking_vectors = rank.compute_ranking_vectors_for_advisory_records_with_db(advisory_record, advisory_record.connection)
    assert len(advisory_record.ranking_vectors) == 54

def test_close_database():
    vulnerabilities_connection.close()
    prospector_connection.close()