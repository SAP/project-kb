import random, os, re, copy, time, datetime, ast, copy, sys
import numpy as np
import pandas as pd
import spacy

nlp = spacy.load('en_core_web_sm')

import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from sklearn.model_selection import ShuffleSplit, cross_val_score, cross_validate, train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

current_working_directory = os.getcwd()
os.chdir('git_explorer')
sys.path.append(os.getcwd())

os.environ['GIT_CACHE'] = current_working_directory + '/git_explorer/git_explorer_cache'
GIT_CACHE = current_working_directory + '/git_explorer/git_explorer_cache'
from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

import database
import filter

##################################
###
### MAGIC NUMBERS
###
##################################

# selection interval
days_before = 730 # two years
days_after = 100 # 100 days
seconds_per_month = 31557600 / 12 # dividing the vulnerability published timestamp by this number to "normalize" it a bit

relevant_extensions = ["java", "c", "cpp", "h", "py", "js", "xml", "go", "rb", "php", "sh", "scale", "lua", "m", "pl", "ts", "swift", "sql", "groovy", "erl", "swf", "vue", "bat", "s", "ejs", "yaml", "yml", "jar"]
fix_indicating_words = ['security', 'cve', 'patch', 'vulnerability', 'vulnerable', 'advisory', 'attack', 'exploit', 'exploitable']

# # when set to true, multiprocessing will be used to compute lexical similarity
from multiprocessing import Pool
with_multiprocessing = True
number_of_cpus = os.cpu_count()


##################################
# if with_multiprocessing:
#     from multiprocessing import Pool

#     number_of_cpus = os.cpu_count()

#     p = Pool(number_of_cpus)

def get_cosine_similarity(v1, v2):
    return cosine_similarity(v1, v2)[0][0]

##################################
###
### FILTERING TEXT
###
##################################

def camel_case_split(token):
    '''
    Splits a CamelCase token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', token)
    result = [m.group(0).lower() for m in matches]
    if len(result) == 1:
        return
    return [token] + result

def snake_case_split(token):
    '''
    Splits a snake_case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    result = token.split('_')
    if len(result) == 1:
        return 
    return [token] + result    

def dot_case_split(token):
    '''
    Splits a dot.case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in dot.case

    Returns:
        None: if the token is not in dot.case
        list: 'dot.case' --> ['dot.case', 'dot', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    result = token.split('.')
    if len(result) == 1:
        return 
    return [token] + result

def text_into_chunks(text, chunk_size=1000):
    '''
    Yield successive n-sized chunks from list.
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def filter_text(text, as_tokens=False, as_list=False, remove_duplicates=False, case_sensitive=False, lemmatize=True):
    '''
    Input:
        description (str): textual description to filter
        as_tokens (bool): whether to return as a list of relevant tokens. If True, the other modifications do not occur (i.e. removing duplicates)
        as_list (bool): to return as a bag of words
        remove_duplicates (bool): to remove duplicates
        case_sensitve (bool): whether to consider all tokens in lowercase or not (lemmatize should be False if case_sensitive is True)
        lemmatize (bool): whether to lemmatize or not

    Returns:
        list / str: a list of relevant tokens, or a string

        @TODO:
        - now the text is not split at the end of a line / sentence but after the 1000 tokens
    '''
    filtered_text = list()

    # when a list is provided concatenate it into a string
    if type(text) == list:
        text = ' '.join([str(line) for line in text])

    # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
    for chunk in text_into_chunks(text, chunk_size = 10000):
        for token in nlp(chunk):
            if token.is_punct == False and token.is_stop == False and token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and any(char for char in token.text if char.isalpha()) and len(token) > 1:
                filtered_text.append(token)

    # return output
    if as_tokens:
        return filtered_text

    # else:
    if lemmatize:
        tokens = [str(token.lemma_) for token in filtered_text]
    else:
        tokens = [str(token.text) for token in filtered_text]

    result = list()
    for token in tokens:
        if camel_case_split(token):
            if lemmatize:
                result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token)))]
            else:
                result += camel_case_split(token)
        elif snake_case_split(token):
            if lemmatize:
                result += [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token)))]
            else:
                result += snake_case_split(token)
        elif dot_case_split(token):
            if lemmatize:
                result += [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token)))]
            else:
                result += dot_case_split(token)
        else:
            result.append(token)

    if case_sensitive == False:
        result = [token.lower() for token in result]
    if remove_duplicates:
        result = list(dict.fromkeys([token for token in result]))
    
    if as_list:
        return result
    return ' '.join(result)

def filter_doc(doc):
    if type(doc) != spacy.tokens.doc.Doc:
        raise TypeError("The document should be a spacy.tokens.doc.Doc, which is created by means of nlp(")
    
    tokens = [token for token in doc if token.is_punct == False and token.is_stop == False and any(char for char in token.text if char.isalpha()) and len(token) > 1] #token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and 
    result = list()
    for token in tokens:
        if camel_case_split(token.text):
            result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
        elif snake_case_split(token.text):
            result += [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token.text)))]
        elif dot_case_split(token.text):
            result += [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token.text)))]

        else:
            result.append(str(token.lemma_).lower())

    return ' '.join(result)

def simpler_filter_text(text):
    ''' Similar to filter_text but without options:
            will be lemmatized and returned as a string
    '''

    # when a list is provided concatenate it into a string
    if type(text) == list:
        text = ' '.join([str(line) for line in text])

    # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
    return ' '.join([filter_doc(nlp(chunk)) for chunk in text_into_chunks(text, chunk_size = 10000)]).lower()

def extract_relevant_lines_from_commit_diff(git_diff, max_lines=10000):
    '''
    The commit diff returned by git-explorer contains information as the repository and file names of the changes,
        this information is already part of the ranking vector thus needs to be removed.
        Furthermore, the commit diff contains code tokens which can be removed.

    Input:
        git_diff (list): the result from git-explorer.commit.get_diff()

    Returns:
        list: only the actual line changes filtered
    '''
    if type(git_diff) != list:
        raise TypeError('The git_diff should be a list (as returned by git)')
        
    return [line for line in git_diff if line.startswith(('diff --git', 'index ', '+++ ', '--- ', '@@ ')) == False][:max_lines]

def extract_n_most_occurring_words(text, n=20):
    if type(text) == list:
        text = ' '.join(text)

    bow = text.split(' ')
    count_dict = {word : bow.count(word) for word in bow}
    
    return ' '.join(list({k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1], reverse=True)}.keys())[:n])

def find_references(text):
    '''
    Finds references in text, currently only looking for # with digits
    '''
    if type(text) == list:
        text = ' '.join(text)

    github_issue_reference = re.compile('#[0-9]+')
    url_reference = re.compile('https?://\S+')

    references = github_issue_reference.findall(text) + url_reference.findall(text)
    return [reference.rstrip('.)/,:;[]') for reference in references]

strings_on_every_page = ['Skip to content', 'Why GitHub?', 'Features', '→', 'Code review', 'Project management', 'Integrations', 'Actions', 'Packages', 'Security', 'Team management', 'Hosting', 'Mobile', 'Customer stories', '→', 'Security', '→', 'Team', 'Enterprise', 'Explore', 'Explore GitHub', '→', 'Learn & contribute', 'Topics', 'Collections', 'Trending', 'Learning Lab', 'Open source guides', 'Connect with others', 'Events', 'Community forum', 'GitHub Education', 'Marketplace', 'Pricing', 'Plans', '→', 'Compare plans', 'Contact Sales', 'Nonprofit', '→', 'Education', '→', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'No suggested jump to results', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'Sign\xa0in', 'Sign\xa0up', '/', 'Watch', 'Star', 'Fork', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'More', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'Dismiss', 'Join GitHub today', 'GitHub is home to over 50 million developers working together to host and review code, manage projects, and build software together.', 'Sign up', 'New issue', 'Have a question about this project?', 'Sign up for a free GitHub account to open an issue and contact its maintainers and the community.', 'Pick a username', 'Email Address', 'Password', 'Sign up for GitHub', 'By clicking “Sign up for GitHub”, you agree to our', 'terms of service', 'and', 'privacy statement', '. We’ll occasionally send you account related emails.', 'Already on GitHub?', 'Sign in', 'to your account', 'Merged', 'Merged', 'Copy link', 'Quote reply', 'commented', 'Copy link', 'Quote reply', 'commented', 'Sign up for free', 'to join this conversation on GitHub', '.\n    Already have an account?', 'Sign in to comment', 'Assignees', 'Labels', 'None yet', 'None yet', 'Milestone', 'None yet', '© 2020 GitHub, Inc.', 'Terms', 'Privacy', 'Security', 'Status', 'Help', 'Contact GitHub', 'Pricing', 'API', 'Training', 'Blog', 'About', 'You can’t perform that action at this time.', 'You signed in with another tab or window.', 'Reload', 'to refresh your session.', 'You signed out in another tab or window.', 'Reload', 'to refresh your session.']

def extract_n_most_occurring_words_from_references(references, repo_url=None, n=20, return_urls=False, driver=None):
    '''
    Parameters:
        references: list of references, or a string that is one reference
        repo_url: the reference can also be an # that refers to an issue page, therefore the repository url is needed
        n: the amount of words to return
        return_urls: if you want to collect the urls from the pages --> PageRank
        driver: a webdriver can be provided to avoid javascript required pages
    '''

    if type(references) == str:
        references = [references]

    bow, urls_found = [], []

    for reference in references:
        try:
            if 'http' not in reference:
                url = repo_url.rstrip('/') + '/issues/' + reference.lstrip('#')
                r = requests.get(url)
                soup = BeautifulSoup(r.content, "html.parser")

                # check if reference is found and whether it is an issue or pull page
                if reference.lstrip('#') in r.url and '/issues/' in r.url:
                    bow += filter_text(' '.join([string for string in soup.stripped_strings if string not in strings_on_every_page]), as_list=True)
                elif reference.lstrip('#') in r.url and '/pull/' in r.url:
                    bow += filter_text(' '.join([string for string in soup.stripped_strings if string not in strings_on_every_page]), as_list=True)
            else:
                if 'securityfocus.com' in reference.strip('/.'): #securityfocus.com requires a selection in a menu
                    reference = reference.rstrip('/.') + '/discuss' 

                r = requests.get(reference.rstrip('.')) #can be end of the sentence
                soup = BeautifulSoup(r.content, "html.parser")
                reference_content = ' '.join([string for string in soup.stripped_strings])

                # Apache pony mail requires the webdriver to see the content
                if 'requires JavaScript enabled' in reference_content and driver != None:

                    driver.get(reference.strip('.'))
                    time.sleep(0.5)
                    soup = BeautifulSoup(driver.page_source, features="lxml")
                    reference_content = ' '.join([string for string in soup.stripped_strings])

                bow += filter_text(reference_content, as_list=True)

            # add URLs
            if return_urls == True:
                urls_found += [link.get('href').rstrip('/') for link in soup.find_all('a') if link.get('href') and 'http' in link.get('href')]
        except:
            print('Failed in obtaining content for reference {}'.format(reference))

    count_dict = {word : bow.count(word) for word in bow}

    if return_urls == False:
        return ' '.join(list({k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1], reverse=True)}.keys())[:n])
    return ' '.join(list({k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1], reverse=True)}.keys())[:n]), str(urls_found)

##################################
###
### RANKING
###
##################################

def normalize_ranking_vector_component(ranking_vectors, component_indices, reversed=False):
    '''
    reversed (bool): if true, the highest value will be mapped to 1 instead of zero
    '''
    if type(ranking_vectors) != list:
        raise TypeError("ranking_vectors should be a list of ranking vectors to normalize")
    if type(component_indices) == int:
        component_indices = [component_indices]
    if type(reversed) == bool:
        reversed = [reversed] * len(component_indices)

    normalized_ranking_vectors = copy.deepcopy(ranking_vectors) #to copy, not to point to

    for i, component_index in enumerate(component_indices):
        if component_index >= len(ranking_vectors[0]):
            raise ValueError("component_index should be an integer corresponding to the index of the value in the ranking vectors to normalize, while the index is is larger than the length of the vectors")

        component_scores = [ranking_vector[component_index] for ranking_vector in ranking_vectors]
        maximum_value = max(component_scores) if max(component_scores) != 0 else 1
        minimum_value = min(component_scores) if min(component_scores) != 0 else 1

        for vector_index in range(len(ranking_vectors)):
            if reversed[i] == False:
                normalized_ranking_vectors[vector_index][component_index] = ranking_vectors[vector_index][component_index] / maximum_value
            elif ranking_vectors[vector_index][component_index] == 0:
                normalized_ranking_vectors[vector_index][component_index] = 1
            else:
                normalized_ranking_vectors[vector_index][component_index] = minimum_value / ranking_vectors[vector_index][component_index]
    return normalized_ranking_vectors

def compute_scores_from_ranking_vectors(candidate_commits_ranking_vectors, weight_vector=(1,1,1), normalize=True):
    '''
    Input:
        ranking_vector (tuple): a vector with different componens
    '''
    if len(candidate_commits_ranking_vectors[0][0]) != len(weight_vector):
        assert ValueError('Ranking vector and weight vector are not of the same length')

    commit_ids = [commit[0] for commit in candidate_commits_ranking_vectors]
    ranking_vectors = [list(commit[1]) for commit in candidate_commits_ranking_vectors]

    if normalize:
        ranking_vectors = normalize_ranking_vector_component(ranking_vectors, list(range(len(weight_vector))))

    # compute score
    result = list()

    for index, ranking_vector in enumerate(ranking_vectors):
        result.append((commit_ids[index], np.mean([component*weight for component,weight in zip(ranking_vector, weight_vector)])))
    return result

# def rank_candidates(model, ranking_vectors):
#     predictions = model.predict_proba(pd.DataFrame(ranking_vectors.values()))
#     commit_ids = list(ranking_vectors.keys())
#     commit_scores = [(candidate, predictions[index][1]) for index, candidate in enumerate(commit_ids)]
#     return [commit[0] for commit in sorted(commit_scores, key = lambda x : x[1], reverse=True)]

def ranking_vector_dict_to_df(ranking_vector_dict, ranking_vector_names):
    '''
    Previously, dictionaries were used to store the ranking vectors. These dictionaries had vulnerability IDs as keys,
        and another dict as values, with commit IDs as keys and the ranking vectors as values. This has been changed 
        to pd.DataFrame usage, this function can be used to turn one of these dictionaries to a dataframe.
    '''
    column_names = ['vulnerability_id', 'commit_id'] + ranking_vector_names

    ranking_vector_df = pd.DataFrame()
    for vulnerability_id, ranking_vectors in ranking_vector_dict.items():
        rows = [[vulnerability_id, commit_id] + ranking_vector for commit_id, ranking_vector in ranking_vectors.items()]
        ranking_vector_df = ranking_vector_df.append(pd.DataFrame(rows, columns=column_names))
    ranking_vector_df.reset_index(drop=True, inplace=True)
    return ranking_vector_df

def rank_candidates(model, ranking_vectors):
    '''
    @TODO: add test case that the column ID is not dropped from original
    '''

    commit_ids = tuple(ranking_vectors.commit_id)
    ranking_vectors = ranking_vectors.drop(columns=['commit_id'])

    # predict the probability of a ranking vector in being the fix, or not
    predictions = model.predict_proba(ranking_vectors)
    commit_scores = [(candidate, predictions[index][1]) for index, candidate in enumerate(commit_ids)]
    return tuple([commit[0] for commit in sorted(commit_scores, key = lambda x : x[1], reverse=True)])

def rank_ranking_vectors(ranking_vector_df, vulnerability_ids, model):
    '''
    @TODO: verhaaltje

    Returns:
        dict: A dictionary with the vulnerability IDs as key, and a list of commit IDs as values.
            The commit IDs are sorted on the probability of being the fix (ranked)
    '''

    ranked_vulnerability_candidates = dict()

    for vulnerability in vulnerability_ids:

        # extract the ranking vectors for this vulnerability
        ranking_vectors = ranking_vector_df[ranking_vector_df.vulnerability_id == vulnerability].reset_index(drop=True).drop(columns=['vulnerability_id'])

        ranked_vulnerability_candidates[vulnerability] = rank_candidates(model, ranking_vectors)

    return ranked_vulnerability_candidates

def evaluate_ranking(ranked_vulnerability_candidates, vulnerabilities, fix_commits_df, fix_commit_group_mapping_dict, validation_method='all', k=[5, 10], verbose=True):
    no_fixes_count = 0
    no_fixes_found_count = 0

    if type(k) == int:
        k = [k]

    df = pd.DataFrame()

    for vulnerability, ranked_candidates in ranked_vulnerability_candidates.items():
        if vulnerability in vulnerabilities:
            if vulnerability not in list(fix_commits_df.vulnerability_id):
                no_fixes_count += 1
            elif validation_method == 'group':
                if vulnerability in fix_commit_group_mapping_dict:
                    fix_commit_groups = [fix_commits for fix_commits in fix_commit_group_mapping_dict[vulnerability].values()]
                    fix_commit_group_positions = [[ranked_candidates.index(fix_commit) if fix_commit in ranked_candidates else -1 for fix_commit in fix_commit_group] for fix_commit_group in fix_commit_groups]
                    valid_fix_commit_group_positions = [(positions, np.mean(positions) / len(positions)) for positions in fix_commit_group_positions if all([True if position != -1 else False for position in positions])]

                    #select best group based on average position
                    if len(valid_fix_commit_group_positions) > 0:
                        fix_commit_positions = sorted(valid_fix_commit_group_positions, key=lambda x: x[1])[0][0]
                    else:
                        fix_commit_positions = []
                else:
                    fix_commits = list(fix_commits_df[fix_commits_df.vulnerability_id == vulnerability].commit_id)
                    fix_commit_positions = [ranked_candidates.index(fix_commit) for fix_commit in fix_commits if fix_commit in ranked_candidates]

            elif validation_method == 'all':            
                fix_commits = list(fix_commits_df[fix_commits_df.vulnerability_id == vulnerability].commit_id)
                fix_commit_positions = [ranked_candidates.index(fix_commit) for fix_commit in fix_commits if fix_commit in ranked_candidates]

            else: # validate only on the best fix
                fix_commits = list(fix_commits_df[fix_commits_df.vulnerability_id == vulnerability].commit_id)
                try:
                    fix_commit_positions = [sorted([ranked_candidates.index(fix_commit) for fix_commit in fix_commits if fix_commit in ranked_candidates])[0]]
                except:
                    fix_commit_positions = []

            if len(fix_commit_positions) > 0:
                df.at[vulnerability, 'n candidate commits'] = len(ranked_candidates)
                df.at[vulnerability, 'n_fix_commits'] = len(fix_commit_positions)
                df.at[vulnerability, 'fix_commit_positions'] = str(fix_commit_positions)
                df.at[vulnerability, 'min_ranking_position'] = min(fix_commit_positions)
                df.at[vulnerability, 'mean_ranking_position'] = np.mean(fix_commit_positions)
                df.at[vulnerability, 'max_ranking_position'] = max(fix_commit_positions)
                df.at[vulnerability, 'precision'] = len(fix_commit_positions) / (1 + max(fix_commit_positions))

                for position in k:
                    if len(fix_commit_positions) <= position:
                        df.at[vulnerability, 'recall_at_{}'.format(position)] = len([ranked_position for ranked_position in fix_commit_positions if ranked_position < position]) / len(fix_commit_positions)
                    else:
                        df.at[vulnerability, 'recall_at_{}'.format(position)] = len([ranked_position for ranked_position in fix_commit_positions if ranked_position < position]) / position
            else:
                no_fixes_found_count += 1
    if verbose: print("{} / {} do not have a known fix among the candidates (and {} do not have a fix in the data).".format(no_fixes_found_count, len(vulnerabilities), len(no_fixes_count)))
    return df

def create_train_and_test_datasets(ranking_vector_df, vulnerability_ids, fix_commits_df, negative_samples_multiplier=1, test_size=0.2, random_state=4):
    '''
    Parameters:
        ranking_vector_df (pd.DataFrame): the dataframe with all ranking vectors, as returned by @TODO: name
        vulnerability_ids (list): a list of vulnerability IDs to use for create the train and test data sets
        fix_commits_df (pd.DataFrame): the vulnerabilities table as a DataFrame (fix_commits_df = pd.read_sql_query("SELECT * FROM fix_commits", vulnerabilities_connection))
        negative_samples_multiplier (int): how many negative (not security fixes) samples should be drawn for each positive sample. Does not yield the exact multiplied number of instances as not all candidate commits are present among the candidate commits, as only one entire group needs to be present.

    Returns:
        pd.DataFrame: x_train, the training set
        pd.DataFrame: x_test, the test set
        np.array: y_train, the labels of x_train
        np.array: y_test, the labels of x_test
    '''
    random.seed(21)

    subset, labels = pd.DataFrame(), list()

    for vulnerability in vulnerability_ids:
        vulnerability_ranking_vectors = ranking_vector_df[ranking_vector_df.vulnerability_id == vulnerability].set_index('commit_id').drop(columns=['vulnerability_id'])
        fix_commits = [commit_id for commit_id in list(fix_commits_df[fix_commits_df.vulnerability_id == vulnerability].commit_id) if commit_id in list(vulnerability_ranking_vectors.index)]

        non_fix_commits = [commit_id for commit_id in list(vulnerability_ranking_vectors.index) if commit_id not in fix_commits]

        # add non fix commits
        n_fix_commits = len(fix_commits)
        random.shuffle(non_fix_commits) 
        commits_to_select = non_fix_commits[:negative_samples_multiplier*n_fix_commits]
        labels += [0] * len(commits_to_select)

        # add the fix commits
        commits_to_select += fix_commits
        labels += [1] * n_fix_commits
        subset = subset.append(vulnerability_ranking_vectors.loc[commits_to_select])

    # create train and test set
    subset.fillna(value=0.0, inplace=True)

    x_train, x_test, y_train, y_test = train_test_split(subset, labels, test_size=test_size, random_state=random_state)

    x_train.reset_index(inplace=True, drop=True)
    x_test.reset_index(inplace=True, drop=True)

    y_train = np.array(y_train, dtype=np.float)
    y_test = np.array(y_test, dtype=np.float)
    return x_train, x_test, y_train, y_test

def create_training_set(data, negative_samples_multiplier=1, label_column='cls', random_state=4):
    '''
    Parameters:
        negative_samples_multiplier (int): how many negative (not security fixes) samples should be drawn for each positive sample. Does not yield the exact multiplied number of instances as not all candidate commits are present among the candidate commits, as only one entire group needs to be present.

    Returns:
        pd.DataFrame(): 
    '''
    random.seed(random_state)
    indices = list(data[data[label_column] == 1].index)

    # for every fix commit; keys can occur more than once
    for key in list(data[data[label_column] == 1].key):

        ### adding negative samples
        commits = list(data[data['key'] == key].index) 
        random.shuffle(commits) 

        added, i = 0, 0
        while added != negative_samples_multiplier and i != len(commits):

            # fix commits are already in the indices
            if commits[i] not in indices:
                indices.append(commits[i])
                added += 1
            i += 1

    # sample the instances
    training_data = data.iloc[sorted(indices)]
    labels = training_data[label_column].to_numpy(dtype=np.float)
    training_data = training_data.drop([label_column, 'key', 'commit_id'], axis=1)
    training_data.reset_index(inplace=True, drop=True)
    return training_data, labels

# def test_models_on_ranking(model, keys, original_data, classification_data, ranked_candidate_commit_column='ranked_candidate_commits', ranking_vector_column='candidate_commits_ranking_vectors', verbose=True):

#     for key in list(keys):
#         subset = classification_data[classification_data.key == key]
#         commit_ids = list(subset.commit_id)
#         subset = subset.drop(['cls', 'key', 'commit_id'], axis=1)
#         subset.reset_index(drop=True, inplace=True) 
#         predictions = model.predict_proba(subset)
#         commit_scores = [(candidate, predictions[index][1]) for index, candidate in enumerate(commit_ids)]
#         original_data[key][ranked_candidate_commit_column] = [commit[0] for commit in sorted(commit_scores, key = lambda x : x[1], reverse=True)]

#     return original_data, evaluate_ranking(original_data, keys, k=[5,10], ranked_commits_column=ranked_candidate_commit_column, ranking_vector_column=ranking_vector_column, verbose=verbose)

def plot_learning_curves(model_results, title, y_label, x=None, x_label='training test size'):
    '''Plots the individual results in a plot'''
    if x == None:
        x=[(i+1)/100 for i in range(len(model_results['mean_test_score']))]
    xi=list(range(len(x)))
    plt.title(title)
    plt.plot(xi, model_results['mean_test_score'], color='green', label = 'mean test score')
    plt.plot(xi, model_results['mean_train_score'], color='blue', label = 'mean train score')
    plt.xticks(xi, x, rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    return

def extract_project_name_from_repository_url(repo_url):
    project_name = re.sub('^https?://|[^\w]', ' ', repo_url)
    return ' '.join([token for token in project_name.split(' ') if token not in ['github', 'com', 'git', 'org']])

def map_description_to_repository_url(vulnerabilities_connection, vulnerability_id, description):
    vulnerabilities_df = pd.read_sql("SELECT vulnerability_id, repo_url FROM vulnerabilities", vulnerabilities_connection).set_index("vulnerability_id")

    if vulnerability_id in tuple(vulnerabilities_df.index):
        return vulnerabilities_df.at[vulnerability_id, 'repo_url']

    vulnerabilities_df['project_name'] = vulnerabilities_df['repo_url'].apply(extract_project_name_from_repository_url)
    vulnerabilities_df['project_name'] = vulnerabilities_df['project_name'].apply(simpler_filter_text)

    # else return url with highest lexical similarity
    repo_urls = tuple(vulnerabilities_df['repo_url'])
    project_names = list(vulnerabilities_df['project_name'])

    preprocessed_description = simpler_filter_text([re.sub('[^\w]', ' ', token.text) for token in nlp(description)]).lower()
    tfidf_vectorized_strings = TfidfVectorizer().fit_transform([preprocessed_description] + project_names)

    scores = {repo_url : cosine_similarity(tfidf_vectorized_strings[0], tfidf_vectorized_strings[i+1])[0][0] for i, repo_url in enumerate(repo_urls) }
    return list({k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}.keys())[0]

class Advisory_record:
    def __init__(self, vulnerability_id, published_timestamp, repo_url, nvd_references, advisory_references, vulnerability_description, connection, preprocessed_vulnerability_description=None, relevant_tags=None, verbose=True, since=None, until=None):
        self.id = vulnerability_id
        self.published_timestamp = published_timestamp
        self.repo_url = re.sub('\.git$|/$', '', repo_url)
        self.is_github_url = 'https://github.com' in repo_url
        self.project_name = extract_project_name_from_repository_url(self.repo_url)
        self.description = vulnerability_description
        self.relevant_tags = relevant_tags

        if preprocessed_vulnerability_description == None:
            self.preprocessed_description = simpler_filter_text(vulnerability_description)
        else:
            self.preprocessed_description = preprocessed_vulnerability_description

        self.git_repo = Git(repo_url, cache_path=GIT_CACHE)
        self.git_repo.clone(skip_existing=False) #@TODO: true or false..?
        self.connection = connection
        self.nvd_references = nvd_references
        self.advisory_references = advisory_references

        #whether to print or not to print
        self.verbose = verbose
        
        self.since = since
        self.until = until

    class Reference:
        def __init__(self, url, repo_url):
            self.url = url
            self.repo_url = re.sub('\.git$|/$', '', repo_url) 

        def is_pull_page(self):
            return self.repo_url+'/pull/' in self.url

        def is_issue_page(self):
            return self.repo_url+'/issues/' in self.url

        def is_tag_page(self):
            return self.repo_url+'/releases/tag/' in self.url

        def is_commit_page(self):
            return self.repo_url+'/commit/' in self.url

    def analyse_references(self):
        '''
        Scan the first and second level references for github pull, issue, tag or commit references
        '''
        self.pull_references_nvd = list()
        self.pull_references_adv = list()

        self.issue_references_nvd = list()
        self.issue_references_adv = list()

        self.tag_references_nvd = list()
        self.tag_references_adv = list()

        self.commits_found_nvd = list()
        self.commits_found_adv = list()

        for reference in [self.Reference(reference, self.repo_url) for reference in self.nvd_references]:

            if reference.is_pull_page():
                if reference.url.split('/,.') not in self.pull_references_nvd:
                    self.pull_references_nvd.append(reference.url.split('/,.'))

            if reference.is_issue_page():
                if reference.url.split('/,.') not in self.issue_references_nvd:
                    self.issue_references_nvd.append(reference.url.split('/,.'))

            if reference.is_tag_page():
                if reference.url.split('/,.') not in self.tag_references_nvd:
                    self.tag_references_nvd.append(reference.url.split('/,.'))

            if reference.is_commit_page():
                commit_id = reference.url.split('/commit/')[1][:8] #only first 8 characters
                if commit_id not in self.commits_found_nvd:
                    self.commits_found_nvd.append(commit_id)

        for reference in [self.Reference(reference, self.repo_url) for reference in self.advisory_references]:
            if reference.is_pull_page():
                if reference.url.split('/,.') not in self.pull_references_adv:
                    self.pull_references_adv.append(reference.url.split('/,.'))

            if reference.is_issue_page():
                if reference.url.split('/,.') not in self.issue_references_adv:
                    self.issue_references_adv.append(reference.url.split('/,.'))

            if reference.is_tag_page():
                if reference.url.split('/,.') not in self.tag_references_adv:
                    self.tag_references_adv.append(reference.url.split('/,.'))

            if reference.is_commit_page():
                commit_id = reference.url.split('/commit/')[1][:8]
                if commit_id not in self.commits_found_adv:
                    self.commits_found_adv.append(commit_id)

    def reference_analysis_to_dataframe(self):
        return pd.DataFrame({
            'vulnerability_id' : [self.id],
            'repo_url' : [self.repo_url],
            'is_github_url' : [self.is_github_url],

            'n_nvd_references' : [len(self.nvd_references)],
            'n_nvd_pull_references' : [len(self.pull_references_nvd)],
            'n_nvd_issue_references' : [len(self.issue_references_nvd)],
            'n_nvd_tag_references' : [len(self.tag_references_nvd)],
            'n_nvd_commit_references' : [len(self.commits_found_nvd)],

            'n_advisory_references' : [len(self.advisory_references)],
            'n_advisory_pull_references' : [len(self.pull_references_adv)],
            'n_advisory_issue_references' : [len(self.issue_references_adv)],
            'n_advisory_tag_references' :[len(self.tag_references_adv)],
            'n_advisory_commit_references' : [len(self.commits_found_adv)],

            'total_n_commits_found' : [len(list(dict.fromkeys(self.commits_found_nvd + self.commits_found_adv)))]
        })

    def validate_database_coverage(self):
        database.add_commits_to_database(self.connection, self.candidate_commits, git_repo=self.git_repo, verbose=self.verbose)
        database.add_repository_to_database(self.connection, self.repo_url, self.project_name, verbose=self.verbose)
        database.add_tags_to_database(self.connection, tags=None, git_repo=self.git_repo, verbose=self.verbose)

        #remove candidates that are not in the databases
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM commits WHERE id IN {} and repository_url = :repo_url".format(tuple(self.candidate_commits+[self.candidate_commits[0]])), {'repo_url':self.repo_url}) # +[self.candidate_commits[0]] as SQL requires at least 2 items
        commits_in_the_db = [row['id'] for row in cursor]

        if self.verbose:
            print('    Had to discard {} candidates as they were not in the DB.'.format(len([commit_id for commit_id in self.candidate_commits if commit_id not in commits_in_the_db])))
        cursor.close()
        self.candidate_commits = commits_in_the_db

    def gather_candidate_commits(self):
        if self.since == None and self.until == None:
            self.since, self.until = database.timestamp_to_timestamp_interval(self.published_timestamp, days_before=days_before, days_after=days_after)

        ### Add commits before NVD release with maximum to add
        commit_ids_to_add_before = database.get_commit_ids_between_timestamp(str(self.since), str(self.published_timestamp), git_repo=self.git_repo, repository_url=self.repo_url)
        if len(commit_ids_to_add_before) > 5215:
            commit_ids_to_add_before = commit_ids_to_add_before[:5215] #add the 5215 closest before the NVD release date

        ### Add commits after NVD release with a maximum to add
        commit_ids_to_add_after = database.get_commit_ids_between_timestamp(str(self.published_timestamp), str(self.until), git_repo=self.git_repo, repository_url=self.repo_url)
        if len(commit_ids_to_add_after) > 100:
            commit_ids_to_add_after = commit_ids_to_add_after[-100:] #add the 100 closest before the NVD release date

        # gather candidate commits
        self.candidate_commits = commit_ids_to_add_before + commit_ids_to_add_after
        if len(self.candidate_commits) > 0:
            self.validate_database_coverage()
            self.candidate_commits = filter.filter_commits_on_files_changed_extensions(self.candidate_commits, self.connection, verbose=self.verbose)
        else:
            print("No candidates found.")

    def compute_ranking_vectors(self, vulnerability_specific_scaling=False):
        self.ranking_vectors = compute_ranking_vectors_for_advisory_records_with_db(self, vulnerability_specific_scaling)

def create_classification_data(data, keys, cve_data_dict, ranking_vector_column='candidate_commits_ranking_vectors', irrelevant_commits_based_on_extension=None, connection=None):
    '''
    Returns:
        pd.DataFrame(): 
    '''
    if irrelevant_commits_based_on_extension == None:
        commits_in_data = tuple(dict.fromkeys([commit_id for key in keys for commit_id in [ranking_vector[0] for ranking_vector in data[key][ranking_vector_column]]]))
        relevant_commits_based_on_extension = filter.filter_commits_on_files_changed_extensions(commits_in_data, connection)
        irrelevant_commits_based_on_extension = [commit_id for commit_id in commits_in_data if commit_id not in relevant_commits_based_on_extension]

    classification_df = pd.DataFrame(columns=['cls', 'key', 'commit_id'])

    for key in keys:
        fix_commits = [fix_commit_id for fix_commit_group in data[key]['fix_commit'] for fix_commit_id in fix_commit_group]

        # make it scaleable on the number of ranking vector components
        ranking_vector_length = len(data[key][ranking_vector_column][0][1])
        ranking_vector_components = [list() for i in range(ranking_vector_length)]
        for candidate in data[key][ranking_vector_column]:
            for i in range(ranking_vector_length):
                ranking_vector_components[i].append(candidate[1][i] if len(candidate[1]) >= i+1 else 0.0) 

        # store values in a dict to append to the dataframe
        df_from_dict = {
            component_index : ranking_vector_components[component_index] for component_index in range(ranking_vector_length)
        }
        df_from_dict['cls'] = [1 if candidate[0] in fix_commits else 0 for candidate in data[key][ranking_vector_column]]
        df_from_dict['key'] = [key for i in range(len(data[key][ranking_vector_column]))]
        df_from_dict['commit_id'] = [candidate[0] for candidate in data[key][ranking_vector_column]]
        
        classification_df = classification_df.append(pd.DataFrame.from_dict(df_from_dict))

    # removing irrelevant commits based on extensions
    classification_df = classification_df[~classification_df.commit_id.isin(irrelevant_commits_based_on_extension)]
    classification_df.reset_index(inplace=True, drop=True)
    return classification_df

def remove_project_name_from_string(string, project_name):
    try:
        return ' '.join([token for token in string.split(' ') if token not in project_name.split(' ')])
    except:
        return ''

def check_preprocessing(advisory_record, candidate_commit_df):
    # extract commit content
    project_name = simpler_filter_text(advisory_record.project_name)

    #check whether values have been preprocessed
    for index in candidate_commit_df[(candidate_commit_df.preprocessed_message == None) | (candidate_commit_df.preprocessed_message == '')].index:
        preprocessed_message = simpler_filter_text(ast.literal_eval(candidate_commit_df.at[index, 'message']))
        candidate_commit_df.at[index, 'preprocessed_message'] = preprocessed_message

    for index in candidate_commit_df[(candidate_commit_df.preprocessed_changed_files == None) | (candidate_commit_df.preprocessed_changed_files == '')].index:
        preprocessed_message = simpler_filter_text(ast.literal_eval(candidate_commit_df.at[index, 'changed_files']))
        candidate_commit_df.at[index, 'preprocessed_changed_files'] = preprocessed_message

    for index in candidate_commit_df[(candidate_commit_df.preprocessed_diff == None) | (candidate_commit_df.preprocessed_diff == '')].index:
        preprocessed_message = simpler_filter_text(ast.literal_eval(candidate_commit_df.at[index, 'diff']))
        candidate_commit_df.at[index, 'preprocessed_diff'] = preprocessed_message

    candidate_commit_df['preprocessed_message'] = candidate_commit_df['preprocessed_message'].apply(remove_project_name_from_string, project_name=project_name)
    candidate_commit_df['preprocessed_changed_files'] = candidate_commit_df['preprocessed_changed_files'].apply(remove_project_name_from_string, project_name=project_name)
    candidate_commit_df['preprocessed_diff'] = candidate_commit_df['preprocessed_diff'].apply(remove_project_name_from_string, project_name=project_name)

    return candidate_commit_df

def compute_lexical_similarity_components(advisory_record, candidate_commit_df):

    # Preprocess
    project_name = simpler_filter_text(advisory_record.project_name)
    description = advisory_record.preprocessed_description
    if 'nvd_references_content' in advisory_record.__dict__:
        description += advisory_record.nvd_references_content
    description = remove_project_name_from_string(string=description, project_name=project_name)

    # create additional bags of words
    description_with_fix_indicating_words = description + ' '.join(fix_indicating_words) # for the commit message
    
    # define the different aspects and compute vector components
    tfidf_vectorizer_messages, tfidf_vectorizer_files, tfidf_vectorizer_diff = TfidfVectorizer(), TfidfVectorizer(), TfidfVectorizer()

    tfidf_messages = tfidf_vectorizer_messages.fit_transform([description_with_fix_indicating_words] + list(candidate_commit_df['preprocessed_message']))
    tfidf_files = tfidf_vectorizer_files.fit_transform([description] + list(candidate_commit_df['preprocessed_changed_files']))
    tfidf_diffs = tfidf_vectorizer_diff.fit_transform([description] + list(candidate_commit_df['preprocessed_diff']))

    # compute scores
    # can be done with multiprocessing
    if with_multiprocessing:
        with Pool(number_of_cpus) as p:
            candidate_commit_df['message_score'] = p.starmap(get_cosine_similarity, [(tfidf_messages[0], tfidf_messages[index+1]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['changed_files_score'] = p.starmap(get_cosine_similarity, [(tfidf_files[0], tfidf_files[index+1]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['git_diff_score'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[0], tfidf_diffs[index+1]) for index in range(len(candidate_commit_df))])
            # candidate_commit_df['message_score'] = p.map(get_cosine_similarity, [(tfidf_messages[0], tfidf_messages[index+1]) for index in range(len(candidate_commit_df))])
            # candidate_commit_df['changed_files_score'] = p.map(get_cosine_similarity, [(tfidf_files[0], tfidf_files[index+1]) for index in range(len(candidate_commit_df))])
            # candidate_commit_df['git_diff_score'] = p.map(get_cosine_similarity, [(tfidf_diffs[0], tfidf_diffs[index+1]) for index in range(len(candidate_commit_df))])
    else:
        candidate_commit_df['message_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[0], tfidf_messages[x.name+1])[0][0], axis=1) #x.name is index
        candidate_commit_df['changed_files_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[0], tfidf_files[x.name+1])[0][0], axis=1) 
        candidate_commit_df['git_diff_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[0], tfidf_diffs[x.name+1])[0][0], axis=1) 

    return candidate_commit_df

# reference_stopwords = ['redhat', 'red', 'hat', 'github', 'GitHub', 'git', 'hub', 'january', 'februari', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'com', 'org', 'version', 'release'] + ['fix', 'security', 'cve', 'patch', 'prevent', 'vulnerability']

# def remove_forbidden_words_from_string(string, forbidden_words):
#     if type(forbidden_words) == 'str':
#         forbidden_words = forbidden_words.split(' ') 
#     try:
#         return ' '.join([token for token in string.split(' ') if token not in forbidden_words])
#     except:
#         return ''

# def compute_lexical_similarity_components_with_references(advisory_record, candidate_commit_df):
#     #@TODO: now using the nvd references cursor

#     nvd_references_cursor.execute("SELECT url, preprocessed_content FROM vulnerability_references WHERE vulnerability_id = :vulnerability_id", {'vulnerability_id': advisory_record.id})
#     nvd_references = {nvd_reference['url'] : nvd_reference['preprocessed_content'] for nvd_reference in nvd_references_cursor}
#     nvd_references_content = extract_n_most_occurring_words(remove_forbidden_words_from_string(string=' '.join(nvd_references.values()), forbidden_words = reference_stopwords + project_name.split(' ')), n=20)

#     # define the different aspects and compute vector components
#     tfidf_vectorizer_messages, tfidf_vectorizer_files, tfidf_vectorizer_diff = TfidfVectorizer(), TfidfVectorizer(), TfidfVectorizer()

#     tfidf_messages = tfidf_vectorizer_messages.fit_transform([nvd_references_content] + list(candidate_commit_df['preprocessed_message']))
#     tfidf_files = tfidf_vectorizer_files.fit_transform([nvd_references_content] + list(candidate_commit_df['preprocessed_changed_files']))
#     tfidf_diffs = tfidf_vectorizer_diff.fit_transform([nvd_references_content] + list(candidate_commit_df['preprocessed_diff']))

#     # compute scores
#     # candidate_commit_df['nvd_references_message_similarity'] = p.starmap(get_cosine_similarity, [(tfidf_messages[0], tfidf_messages[index+1]) for index in range(len(candidate_commit_df))])
#     # candidate_commit_df['nvd_references_changed_files_similarity'] = p.starmap(get_cosine_similarity, [(tfidf_files[0], tfidf_files[index+1]) for index in range(len(candidate_commit_df))])
#     # candidate_commit_df['nvd_references_git_diff_similarity'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[0], tfidf_diffs[index+1]) for index in range(len(candidate_commit_df))])

#     candidate_commit_df['nvd_references_message_similarity'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[0], tfidf_messages[x.name+1])[0][0], axis=1) #x.name is index
#     candidate_commit_df['nvd_references_changed_files_similarity'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[0], tfidf_files[x.name+1])[0][0], axis=1) 
#     candidate_commit_df['nvd_references_git_diff_similarity'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[0], tfidf_diffs[x.name+1])[0][0], axis=1) 

#     return candidate_commit_df

def is_path(token):
    return '/' in token.rstrip('.,;:?!"\'') or ('.' in token.rstrip('.,;:?!"\'') and token.rstrip('.,;:?!"\'').split('.')[-1] in relevant_extensions)

def extract_code_tokens(description):
    tokens = [token.rstrip('.,;:?!"\'') for token in description.split(' ')] #remove punctuation etc.
    relevant_tokens = [token for token in tokens if not is_path(token) and (dot_case_split(token) or snake_case_split(token) or camel_case_split(token))]
    return relevant_tokens

def compute_lexical_similarity_components_code_tokens(advisory_record, candidate_commit_df):

    # Preprocess
    project_name = simpler_filter_text(advisory_record.project_name)
    description = advisory_record.description
    code_tokens = simpler_filter_text(extract_code_tokens(description))
    code_tokens = remove_project_name_from_string(string=code_tokens, project_name=project_name)

    # define the different aspects and compute vector components
    # tfidf_vectorizer_messages = TfidfVectorizer()
    tfidf_vectorizer_files = TfidfVectorizer()
    # tfidf_vectorizer_diff = TfidfVectorizer()

    # tfidf_messages = tfidf_vectorizer_messages.fit_transform([code_tokens] + list(candidate_commit_df['preprocessed_message']))
    tfidf_files = tfidf_vectorizer_files.fit_transform([code_tokens] + list(candidate_commit_df['preprocessed_changed_files']))
    # tfidf_diffs = tfidf_vectorizer_diff.fit_transform([code_tokens] + list(candidate_commit_df['preprocessed_diff']))

    # compute scores
    # with multiprocessing
    if with_multiprocessing:
        with Pool(number_of_cpus) as p:
            # candidate_commit_df['message_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_messages[0], tfidf_messages[index+1]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['changed_files_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_files[0], tfidf_files[index+1]) for index in range(len(candidate_commit_df))])
            # candidate_commit_df['git_diff_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[0], tfidf_diffs[index+1]) for index in range(len(candidate_commit_df))])
    else:
        # without multiprocessing
        # candidate_commit_df['message_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[0], tfidf_messages[x.name+1])[0][0], axis=1) #x.name is index
        candidate_commit_df['changed_files_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[0], tfidf_files[x.name+1])[0][0], axis=1) 
        # candidate_commit_df['git_diff_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[0], tfidf_diffs[x.name+1])[0][0], axis=1) 

    return candidate_commit_df

def extract_path_tokens_from_text(text):
    return [re.split('\.|,|/', token.rstrip('.,;:?!"\'')) for token in text.split(' ') if ('/' in token.rstrip('.,;:?!"\'') and not token.startswith('</')) or ('.' in token.rstrip('.,;:?!"\'') and token.rstrip('.,;:?!"\'').split('.')[-1] in relevant_extensions)]

def compute_path_similarity_score(changed_files, path_tokens_list):
    '''
    Provides a score for the found path and the changed files.
    - a description can mention multiple paths, therefore a sum is returned
    - a path can match multiple files, therefore the scores are first stored 
    in an intermediate score list and only the highest score is kept.
    '''
    if type(changed_files) == str:
        changed_files = ast.literal_eval(changed_files)

    path_similarity_scores = [0] # to return 0 if there are no path tokens

    for path_tokens in path_tokens_list:
        intermediate_scores = list()

        reversed_path_tokens = list(reversed([token.lower() for token in path_tokens]))
        with_extension = True if reversed_path_tokens[0] in relevant_extensions else False

        for changed_file in changed_files:       

            changed_file_tokens = list(reversed([token.lower() for token in re.split('\.|,|/', changed_file)]))
            if with_extension == False and changed_file_tokens[0] in relevant_extensions:
                changed_file_tokens.pop(0) #remove the extension

            same_token_count, same_tokens = 0, True
            while same_tokens == True and same_token_count < len(reversed_path_tokens) and same_token_count < len(changed_file_tokens):
                if reversed_path_tokens[same_token_count] == changed_file_tokens[same_token_count]:
                    same_token_count += 1
                else:
                    same_tokens = False

            # adjust for only changing the right extension
            if with_extension and same_token_count > 0:
                same_token_count -= 1 
            intermediate_scores.append(same_token_count)
        path_similarity_scores.append(max(intermediate_scores))
    return sum(path_similarity_scores)

def calculate_time_distance_before(commit_timestamp, published_timestamp, first_candidate_timestamp):
    return 0.5 + ((commit_timestamp - first_candidate_timestamp) / (published_timestamp - first_candidate_timestamp)) / 2 if commit_timestamp < published_timestamp else 0.0

def calculate_time_distance_after(commit_timestamp, published_timestamp, last_candidate_timestamp):
    return 1 - ((commit_timestamp - published_timestamp) / (last_candidate_timestamp - published_timestamp)) / 2 if commit_timestamp > published_timestamp else 0.0

def compute_commit_distance_components(advisory_record, candidate_commit_df, days_before=100, days_after=0):
    cursor = advisory_record.connection.cursor()

    # gather the tags in the description
    if advisory_record.relevant_tags == None:
        cursor.execute("SELECT tag FROM tags WHERE repo_url = :repo_url", {'repo_url' : advisory_record.repo_url}) 
        tags = [row['tag'] for row in cursor]
        if len(tags) == 0:
            advisory_record.relevant_tags = []
        else:
            versions_in_description = filter.retreive_all_versions_from_description(advisory_record.description)
            tags_in_description = [tag for version in versions_in_description for tag in filter.get_tag_for_version(tags, version)]
            advisory_record.relevant_tags = list(dict.fromkeys(tags_in_description))

    # add time components
    # add absolute distance components
    candidate_commit_df = candidate_commit_df.astype({'timestamp': 'int64'})

    first_candidate_timestamp = min(candidate_commit_df.timestamp)
    candidate_commit_df['time_distance_before'] = candidate_commit_df['timestamp'].apply(calculate_time_distance_before, published_timestamp=int(advisory_record.published_timestamp), first_candidate_timestamp=first_candidate_timestamp)

    last_candidate_timestamp = max(candidate_commit_df.timestamp)
    candidate_commit_df['time_distance_after'] = candidate_commit_df['timestamp'].apply(calculate_time_distance_after, published_timestamp=int(advisory_record.published_timestamp), last_candidate_timestamp=last_candidate_timestamp)

    # add reachability components
    if len(advisory_record.relevant_tags) == 0:
        # add an empty component (otherwise the length will not match what is expected)
        candidate_commit_df['reachability_score'] =  [0.0 for i in range(len(candidate_commit_df))]
        return candidate_commit_df

    elif len(advisory_record.relevant_tags) == 1:
        advisory_record.relevant_tags.append(advisory_record.relevant_tags[0])

    timestamps_for_tags_in_description = pd.read_sql("SELECT tag, tag_timestamp FROM tags WHERE tag IN {} AND repo_url = '{}'".format(tuple(advisory_record.relevant_tags), advisory_record.repo_url), advisory_record.connection).set_index('tag')
    timestamps_for_tags_in_description.drop_duplicates(inplace=True)

    reachable_commits = dict()
    for tag in [tag for tag in advisory_record.relevant_tags if tag in list(timestamps_for_tags_in_description.index) and tag not in reachable_commits]:
        since, until = database.timestamp_to_timestamp_interval(timestamp=timestamps_for_tags_in_description.at[tag, 'tag_timestamp'], days_before=days_before, days_after=0)
        reachable_commits[tag] = advisory_record.git_repo.get_commits(ancestors_of=tag, exclude_ancestors_of=None, since=since, until=until)

    # calculate scores
    candidate_commit_df['reachability_score'] = candidate_commit_df.apply(calculate_reachability_score, timestamps_for_tags_in_description=timestamps_for_tags_in_description, reachable_commits=reachable_commits, relevant_tags=advisory_record.relevant_tags, days_before=days_before, axis=1)
    
    return candidate_commit_df

def calculate_reachability_score(row, timestamps_for_tags_in_description, reachable_commits, relevant_tags, days_before):
    relevant_tags = [tag for tag in relevant_tags if tag in list(timestamps_for_tags_in_description.index)]
    return 1.0 - (min([int((int(timestamps_for_tags_in_description.at[tag, 'tag_timestamp']) - int(row['timestamp']))/86400) if row['id'] in reachable_commits[tag] else days_before for tag in relevant_tags]) / days_before) if len(relevant_tags) > 0 else 0.0

def if_commit_id_in_list(commit_id, commits_found_list):
    return 1 if commit_id[:8] in commits_found_list else 0

def compute_referred_to_components(advisory_record, candidate_commit_df):
    if 'commits_found_nvd' not in advisory_record.__dict__ and 'commits_found_adv' not in advisory_record.__dict__:
        advisory_record.analyse_references()

    candidate_commit_df['referred_to_by_nvd'] = candidate_commit_df['id'].apply(if_commit_id_in_list, commits_found_list=advisory_record.commits_found_nvd)
    candidate_commit_df['referred_to_by_advisories'] = candidate_commit_df['id'].apply(if_commit_id_in_list, commits_found_list=advisory_record.commits_found_adv)

    return candidate_commit_df

def if_vulnerability_id_in_list(string, vulnerability_id):
    return 1 if vulnerability_id in string else 0

def if_other_vulnerability_id_in_list(string, vulnerability_id):
    if vulnerability_id not in string and 'CVE-' in string: 
        return 1
    return 0

def hunks_to_n_hunks(hunks):
    return len(ast.literal_eval(hunks))

def hunks_to_avg_hunk_size(hunks):
    hunks = ast.literal_eval(hunks)
    return sum([h[1] - h[0] for h in hunks]) / len(hunks) if len(hunks) != 0 else 0

def contains_issue_reference(message_column):
    return 1 if len([result.group(0) for result in re.finditer('#\d+:?', ' '.join(ast.literal_eval(message_column)))]) > 0 else 0

def contains_jira_reference(message_column):
    return 1 if len([result.group(0) for result in re.finditer('\w+-\d+:?', ' '.join(ast.literal_eval(message_column)))]) > 0 else 0

def changed_files_to_n_changed_files(changed_files):
    return len(ast.literal_eval(changed_files))

def compute_ranking_vectors_for_advisory_records_with_db(advisory_record, vulnerability_specific_scaling=False):
    '''
    Input:
        advisory_record:
        vulnerability_specific_scaling: variables can be scaled vulnerability specific, or on the entire training set
            --> if True, the largest number of the candidates will be scaled to one, otherwise the largest number of all candidates for all vulnerabilities

    Core functionality:
     - extracts content for the candidates
     - ranks the candidates based on their lexical similarity with the vulnerability description
    '''
    if 'candidate_commits' not in advisory_record.__dict__:
        raise ValueError('Advisory record does not contain candidate commits to rank')

    # candidate commit DF
    candidate_commit_df = pd.read_sql("SELECT * FROM commits WHERE id IN {} AND repository_url = '{}'".format(tuple(advisory_record.candidate_commits + [advisory_record.candidate_commits[0]]), advisory_record.repo_url), advisory_record.connection) # +[adisory_record.candidate_commits[0]] as SQL requires at least 2 items
    candidate_commit_df = check_preprocessing(advisory_record, candidate_commit_df)

    # creating the ranking vectors
    candidate_commit_df['vulnerability_id_in_message'] = candidate_commit_df['message'].apply(if_vulnerability_id_in_list, vulnerability_id=advisory_record.id)
    candidate_commit_df['other_CVE_in_message'] = candidate_commit_df['message'].apply(if_other_vulnerability_id_in_list, vulnerability_id=advisory_record.id)

    # commit statistics
    candidate_commit_df['n_hunks'] = candidate_commit_df['hunks'].apply(hunks_to_n_hunks)
    candidate_commit_df['avg_hunk_size'] = candidate_commit_df['hunks'].apply(hunks_to_avg_hunk_size)
    candidate_commit_df['n_changed_files'] = candidate_commit_df['changed_files'].apply(changed_files_to_n_changed_files)

    #commit message references
    candidate_commit_df['git_issue_reference'] = candidate_commit_df['message'].apply(contains_issue_reference)
    candidate_commit_df['contains_jira_reference'] = candidate_commit_df['message'].apply(contains_jira_reference)
    
    # add path score
    path_tokens_list = extract_path_tokens_from_text(advisory_record.description)
    candidate_commit_df['path_similarity_score'] = candidate_commit_df['changed_files'].apply(compute_path_similarity_score, path_tokens_list=path_tokens_list)
    
    # drop columns that are no longer needed
    candidate_commit_df.drop(columns=['repository_url', 'hunks', 'message', 'changed_files', 'diff', 'commit_message_reference_content', 'preprocessed_commit_message_reference_content'], inplace=True)

    # adding lexical similarity components
    candidate_commit_df = compute_lexical_similarity_components(advisory_record, candidate_commit_df)
    candidate_commit_df = compute_lexical_similarity_components_code_tokens(advisory_record, candidate_commit_df)
    candidate_commit_df = compute_commit_distance_components(advisory_record, candidate_commit_df, days_before=100, days_after=0)
    candidate_commit_df = compute_referred_to_components(advisory_record, candidate_commit_df)
    
    # normalize the values
    candidate_commit_df.drop(columns=['timestamp', 'preprocessed_diff', 'preprocessed_message', 'preprocessed_changed_files'], inplace=True)

    # variables can be scaled vulnerability specific, or on the entire training set
    if vulnerability_specific_scaling:
        candidate_commit_df.iloc[:,1:] = MinMaxScaler().fit_transform(candidate_commit_df.iloc[:,1:])
    
    # @TODO: add the vulnerability timestamp as a somewhat normalized component to allow for learning
    candidate_commit_df['vulnerability_timestamp'] = [int(advisory_record.published_timestamp) / seconds_per_month for i in range(len(candidate_commit_df))]
    candidate_commit_df = candidate_commit_df.rename(columns={'id' : 'commit_id'})
    # return {row[0] : row[1:].tolist() for row in candidate_commit_df.values} # to list to be able to write to JSON
    return candidate_commit_df

def analyse_ranking_results(ranking_results_df, method, train_or_test, k=[5, 10, 20]):
    df = pd.DataFrame()
    
    df.at[0, 'method'] = method
    df.at[0, 'train_or_test'] = train_or_test
    df.at[0, 'avg_precision'] = round(np.mean(ranking_results_df.precision) * 100, 2)
    df.at[0, 'avg_max_ranking_pos'] = np.mean(ranking_results_df.max_ranking_position)
    df.at[0, 'med_max_ranking_pos'] = np.median(ranking_results_df.max_ranking_position)
    df.at[0, 'n'] = len(ranking_results_df)

    for position in k:
        fixes_in_top_k = len(ranking_results_df[(ranking_results_df.max_ranking_position < position) & (ranking_results_df.n_fix_commits <= position)]) + len(ranking_results_df[(ranking_results_df.max_ranking_position < ranking_results_df.n_fix_commits) & (ranking_results_df.n_fix_commits > position)])
        df.at[0, 'recall_at_{}'.format(position)] = round(fixes_in_top_k / len(ranking_results_df) * 100, 2)

    return df