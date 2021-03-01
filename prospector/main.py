# The main functionality of the tool

import re, os, json, sqlite3, requests, time, datetime, ast, random, copy, sys, plac
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from joblib import load
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

current_working_directory = os.getcwd()
os.chdir('git_explorer')
sys.path.append(os.getcwd())

#  = current_working_directory + '/git_explorer/git_explorer_cache'
# current_working_directory + '/git_explorer/git_explorer_cache'

GIT_CACHE = ''
if 'GIT_CACHE' in os.environ:
    GIT_CACHE = os.environ['GIT_CACHE']
    
from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

import database
import filter
import rank

### Magic Numbers
# MODELS
min_max_scaler_path = "models/Prospector-universal_columns_scaler.joblib"
model_path = "models/Prospector-LR.joblib"

# COLUMNS
vulnerability_specific_columns = ['message_score', 'changed_files_score', 'git_diff_score', 'message_score_reference_content','changed_files_score_code_tokens']
universal_columns = ['n_hunks', 'avg_hunk_size', 'n_changed_files', 'vulnerability_timestamp']
columns_to_drop = ['path_similarity_score', 'git_diff_score_code_tokens', 'message_score_code_tokens', 'changed_files_score_reference_content', 'git_diff_score_reference_content']


@plac.annotations(
    vulnerability_id=plac.Annotation("A vulnerability ID (typically a CVE)", type=str),
    verbose=plac.Annotation("Definition of verbose: containing more words than necessary: WORDY", 'flag', 'v'),
    description=plac.Annotation("The vulnerability description", "option", type=str),
    published_timestamp=plac.Annotation("The timestamp at which the vulnerability is published (int)", "option", type=int),
    repo_url=plac.Annotation("The affected repository (typically a GitHub URL)", "option", type=str),
    project_name=plac.Annotation("The name of the affected project (typically a GitHub URL)", "option", type=str),
    references=plac.Annotation("A list of references that provide additional information on the vulnerability", "option", type=list),
    k=plac.Annotation("The number of candidates to show", "option", type=int),
    vulnerability_specific_scaling=plac.Annotation("To apply vulnerability specific scaling, or apply the pre-trained MinMaxScaler", "option", type=bool)
)
def main(vulnerability_id, verbose, description=None, published_timestamp=None, repo_url=None, project_name=None, references=None, k=10, vulnerability_specific_scaling=False):
    model = load(model_path)
    universal_columns_scaler = load(min_max_scaler_path)

    # databases are created in the notebook database_creation.ipynb 
    # the vulnerabilities database
    vulnerabilities_connection, vulnerabilities_cursor = database.connect_with_vulnerabilities_database('data/prospector-vulnerabilities.db', verbose=verbose)
    # the commits database
    prospector_connection, prospector_cursor = database.connect_with_database('data/prospector-commits.db', verbose=verbose)

    # if the vulnerability is already in the database
    if database.if_new_vulnerability(vulnerabilities_cursor, vulnerability_id) == False: 
        vulnerability = vulnerabilities_cursor.execute("SELECT * FROM vulnerabilities WHERE vulnerability_id = :vulnerability_id", {'vulnerability_id' : vulnerability_id}).fetchone()
        
        # keep the manually provided value if it has been provided, otherwise select the one in the DB
        repo_url = repo_url if repo_url != None else vulnerability['repo_url']
        published_timestamp = published_timestamp if published_timestamp != None else vulnerability['published_date']
        
        if description == None:
            description = vulnerability['description']
            preprocessed_description = vulnerability['preprocessed_description']
        else:
            preprocessed_description = rank.simpler_filter_text(description)

        if references != None:
            database.add_vulnerability_references_to_database(vulnerabilities_connection, vulnerability_id, references, driver=None, verbose=verbose)
        else:
            references = references if references != None else [nvd_reference['url'] for nvd_reference in vulnerabilities_cursor.execute("SELECT url FROM vulnerability_references WHERE vulnerability_id = :vulnerability_id", {'vulnerability_id': vulnerability_id})]

    else:
        if verbose: print("Vulnerability {} is a new vulnerability".format(vulnerability_id))

        # gather information for the new vulnerability if needed
        if description == None or published_timestamp == None or references == None:
            try:
                nvd_description, nvd_published_timestamp, nvd_references = database.extract_nvd_content(vulnerability_id)
            except: #if the vulnerability is not in the NVD
                nvd_description, nvd_published_timestamp, nvd_references = None, None, None

            if description == None:
                if nvd_description == None:
                    # raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability description manually.".format(vulnerability_id))
                    print("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability description manually.".format(vulnerability_id))
                    description = input()

                    if description == "SKIP!":
                        print('skipping this one')
                        return
                else:
                    description = nvd_description

            if published_timestamp == None:
                if nvd_published_timestamp == None:
                    # raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability timestamp manually.".format(vulnerability_id))
                    print("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability timestamp manually.".format(vulnerability_id))
                    published_timestamp = input()
                else:
                    published_timestamp = nvd_published_timestamp

            if references == None:
                if nvd_references == None:
                    # raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability description manually.".format(vulnerability_id))
                    print("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability references manually (comma seperated).".format(vulnerability_id))
                    references = input()
                    references = references.split(',')
                else:
                    references = nvd_references

        # determine the repo_url
        if repo_url == None:
            if verbose: print('Suggesting a repository URL')
            repo_url = rank.map_description_to_repository_url(vulnerabilities_connection, vulnerability_id, description)
            
            print('Does the vulnerability affect the following repository: {} [Y/n]'.format(repo_url))
            choice = input()
            if choice.lower() in ['', 'y', 'yes']: #@TODO: can be a while, where it is either yes or no, not enter
                print('Confirmed')
            else:
                print('Provide the (GitHub) URL of the affected repository:')
                repo_url = input()
                repo_url = re.sub('\.git$|/$', '', repo_url)
            print('repo_url:', repo_url)

        # add to the database
        preprocessed_description = rank.simpler_filter_text(description)
        with vulnerabilities_connection:
            vulnerabilities_cursor.execute("INSERT INTO vulnerabilities VALUES (:vulnerability_id, :repo_url, :description, :published_timestamp, :preprocessed_description)",
            {'vulnerability_id':vulnerability_id, 'repo_url':repo_url, 'description':description, 'published_timestamp':str(published_timestamp), 'preprocessed_description':preprocessed_description})

        # add the references to the database
        database.add_vulnerability_references_to_database(vulnerabilities_connection, vulnerability_id, references, driver=None, verbose=verbose)
    
    # determine the project_name
    if project_name == None:
        if verbose: print('Suggesting a project name')
        project_name = rank.extract_project_name_from_repository_url(repo_url)
        print('Does the vulnerability affect the following project: {} [Y/n]'.format(project_name))
        choice = input()
        if choice.lower() in ['', 'y', 'yes']: #@TODO: can be a while, where it is either yes or no, not enter
            print('Confirmed')
        else:
            print('Provide the name of the affected project:')
            project_name = input()

    references_content = tuple(pd.read_sql("SELECT vulnerability_id, url, preprocessed_content FROM vulnerability_references WHERE vulnerability_id = '{}' AND url IN {}".format(vulnerability_id, tuple(references)), vulnerabilities_connection).preprocessed_content)
    references_content = rank.extract_n_most_occurring_words(rank.remove_forbidden_words_from_string(string=' '.join(references_content), forbidden_words = rank.reference_stopwords + project_name.split(' ')), n=20)

    # @TODO: now adding all advisory references --> change to only using the provided references
    advisory_references = [advisory_reference['url'] for advisory_reference in vulnerabilities_cursor.execute("SELECT url FROM advisory_references WHERE vulnerability_id = :vulnerability_id", {'vulnerability_id': vulnerability_id})]

    # creating advisory record
    advisory_record = rank.Advisory_record(
        vulnerability_id,
        published_timestamp,
        repo_url,
        references, references_content, advisory_references, description, prospector_connection, preprocessed_vulnerability_description=preprocessed_description, relevant_tags=None, verbose=verbose, since=None, until=None)

    if verbose:
        print("\nThe following advisory record has been created:")
        print(" - Vulnerability ID: {}".format(advisory_record.id))
        print(" - Vulnerability description: {}".format(advisory_record.description))
        print(" - Vulnerability published timestamp: {}".format(advisory_record.published_timestamp))
        print(" - Affected project: {}".format(advisory_record.project_name))
        print(" - Affected repository: {}".format(advisory_record.repo_url))
        print(" - References content extracted: {}".format(advisory_record.references_content))

    if verbose: print("\nGathering candidate commits:")
    advisory_record.gather_candidate_commits()

    if verbose: print("\nComputing ranking vectors:")
    advisory_record.compute_ranking_vectors(vulnerability_specific_scaling)

    if vulnerability_specific_scaling == False:
        if verbose: print("\nscaling some columns using the pretrained scaler, and some vulnerability specific")
        advisory_record.ranking_vectors[vulnerability_specific_columns] = MinMaxScaler().fit_transform(advisory_record.ranking_vectors[vulnerability_specific_columns])
        advisory_record.ranking_vectors[universal_columns] = universal_columns_scaler.transform(advisory_record.ranking_vectors[universal_columns])
    advisory_record.ranking_vectors.drop(columns=columns_to_drop, inplace=True)

    if verbose: print("\nRanking the candidate commits:")
    advisory_record.ranked_candidate_commits = rank.rank_candidates(model, advisory_record.ranking_vectors)

    if verbose: print('\nResults:')
    advisory_record.ranking_vectors.set_index('commit_id', inplace=True)
    output = advisory_record_to_output(advisory_record, model, prospector_cursor, k=k)
    print(output)

    # # succeeded
    vulnerabilities_connection.close()
    prospector_connection.close()
    return advisory_record

def advisory_record_to_output(advisory_record, model, prospector_cursor, k=20):
    if k > len(advisory_record.candidate_commits):
        k = len(advisory_record.candidate_commits)

    # write as txt output as well
    string = 'PROSPECTOR\nA search engine for fix-commits for security vulnerabilities in Open-Source Software\nBy SAP - Antonino SABETTA & Daan HOMMERSOM\n\n'

    string += 'This file shows the result for the search for fix-commits for vulnerability {}\n'.format(advisory_record.id)
    string += 'Firstly, an advisory record is created containing information on the vulnerability.\n'
    string += 'This advisory record is used to select candidate commits. For these candidate commits,\n'
    string += 'ranking vectors are computed. These ranking vectors consist of several components that\n'
    string += 'can be used to predict whether a candidate commit is the fix commit we are looking for.\n'
    string += 'These candidates are then ranked on this probability score, and the first {} are shown\n'.format(k)
    string += 'in this file. In 77.68% of the cases, the fix is in the top 5. In 84.03% in the top 10, \n'
    string += 'and in 88.59% in the top 20.'

    string += '\n\nFEATURES:\n'
    string += 'The message_score, git_diff_score, changed_files_score reflect the lexical similarity with \n'
    string += 'the vulnerability description. The time_distance_before and time_distance_after reflect how \n'
    string += 'much time was between the vulnerability release date and the commit timestamp. The \n'
    string += 'reachability_score reflects whether a commit is reachable from one of the tags mentioned\n'
    string += 'in the vulnerability_description.'
    
    string += '\n\nWEIGHTS (Logistic Regression Coefficients):\n{}'.format(pd.DataFrame({'feature' : advisory_record.ranking_vectors.columns, 'importance' : model.coef_[0]}).set_index('feature').sort_values('importance', ascending=False).transpose().loc['importance'])
    
    string += '\n\nADVISORY RECORD - {}'.format(advisory_record.id)
    
    string += '\n - Vulnerability description: {}'.format(advisory_record.description)
    string += '\n - Published timestamp: {}'.format(advisory_record.published_timestamp)
    string += '\n - Repository: {}'.format(advisory_record.repo_url)
    string += '\n - Relevant tags: {}'.format(advisory_record.relevant_tags)

    string += '\n\nPROSPECTOR RESULTS - {}'.format(advisory_record.id)

    for i in range(k):
        string += '\n\nCandidate {}: {}/commit/{}'.format(i, advisory_record.repo_url, advisory_record.ranked_candidate_commits[i])
        string += '\n - Tag(s): {}'.format(Commit(advisory_record.git_repo, advisory_record.ranked_candidate_commits[i]).get_tags())
        ranking_vector = advisory_record.ranking_vectors.loc[advisory_record.ranked_candidate_commits[i]]
        commit = prospector_cursor.execute("SELECT message, changed_files, preprocessed_message FROM commits WHERE id = :commit_id AND repository_url = :repo_url", {'commit_id' : advisory_record.ranked_candidate_commits[i], 'repo_url': advisory_record.repo_url}).fetchone()
        commit_message = str(' '.join(ast.literal_eval(str(commit['message'])))) #commit['preprocessed_message']#
        string += "\n - Commit message: {}".format(repr(commit_message)) #
        string += "\n - Changed files: {}".format(commit['changed_files'])
        string += "\n - Ranking vector: \n{}".format(ranking_vector)
    return string

if __name__ == "__main__":
    plac.call(main)

## TEST CASE
# main('CVE-2018-16166', verbose=True, description=None, published_timestamp=None, repo_url=None, references=None, k=10, vulnerability_specific_scaling=False, model='logistic_regression')
