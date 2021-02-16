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
reference_stopwords = ['redhat', 'red', 'hat', 'github', 'GitHub', 'git', 'hub', 'january', 'februari', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'com', 'org', 'version', 'release'] + fix_indicating_words # words to avoid sampling

# # when set to true, multiprocessing will be used to compute lexical similarity
from multiprocessing import Pool
with_multiprocessing = True
number_of_cpus = os.cpu_count()

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
        None: if the token is not in snake_case
        list: 'snake_case' --> ['snake_case', 'snake', 'case']
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

def text_into_chunks(text, chunk_size=10000):
    '''
    Yield successive n-sized chunks from list.
    @TODO: now the text is not split at the end of a line / sentence but after the 1000 tokens,
        might be better to split on line endings or tokens

    Input:
        text (str/list): the test to split in chunks
        chunk_size (int): the number characters per chunk
    
    Returns:
        list: a list of the chunks
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def filter_text(text, as_tokens=False, as_list=False, remove_duplicates=False, case_sensitive=False, lemmatize=True):
    '''
    This is the 'complex' filter text function and can be used for all kinds of preprocessing

    Input:
        text (list/str): The text to filter i.e. a vulnerability description
        as_tokens (bool): whether to return as a list of relevant tokens. If True, the other modifications do not occur (i.e. removing duplicates)
        as_list (bool): to return as a bag of words
        remove_duplicates (bool): to remove duplicates
        case_sensitve (bool): whether to consider all tokens in lowercase or not (lemmatize should be False if case_sensitive is True)
        lemmatize (bool): whether to lemmatize or not

    Returns:
        list / str: a list of relevant tokens, or a string
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
    '''
    Function used for the simpler_filter_text; filters the textual document (chunk)

    Input: 
        doc (spacy.tokens.doc.Doc): the input document
    
    Returns:
        str: the preprocessed doc as a string
    '''
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
    ''' 
    Similar to filter_text but without options:
            will be lemmatized and returned as a string

    Input:
        text (list/str): the text to preprocess i.e. a vulnerability description

    Returns:
        str: the preprocessed text
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
    '''
    Extracts the most occurring words from the text

    Input:
        text (str/list)
        n (int): the number of words to return

    Returns:
        str: the n most occurring words
    '''
    if type(text) == list:
        text = ' '.join(text)

    bow = text.split(' ')
    count_dict = {word : bow.count(word) for word in bow}
    
    return ' '.join(list({k: v for k, v in sorted(count_dict.items(), key=lambda item: item[1], reverse=True)}.keys())[:n])

def find_references(text):
    '''
    Finds references in text, currently only looking for Git issues through # with digits and URLs

    Input:
        text (str/list)
    
    Returns:
        list: a list of the found references
    '''
    if type(text) == list:
        text = ' '.join(text)

    github_issue_reference = re.compile('#[0-9]+')
    url_reference = re.compile('https?://\S+')

    references = github_issue_reference.findall(text) + url_reference.findall(text)
    return [reference.rstrip('.)/,:;[]') for reference in references]

# to avoid being the most occurring words, as they are on every GitHub page
strings_on_every_page = ['Skip to content', 'Why GitHub?', 'Features', '→', 'Code review', 'Project management', 'Integrations', 'Actions', 'Packages', 'Security', 'Team management', 'Hosting', 'Mobile', 'Customer stories', '→', 'Security', '→', 'Team', 'Enterprise', 'Explore', 'Explore GitHub', '→', 'Learn & contribute', 'Topics', 'Collections', 'Trending', 'Learning Lab', 'Open source guides', 'Connect with others', 'Events', 'Community forum', 'GitHub Education', 'Marketplace', 'Pricing', 'Plans', '→', 'Compare plans', 'Contact Sales', 'Nonprofit', '→', 'Education', '→', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'No suggested jump to results', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'Sign\xa0in', 'Sign\xa0up', '/', 'Watch', 'Star', 'Fork', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'More', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'Dismiss', 'Join GitHub today', 'GitHub is home to over 50 million developers working together to host and review code, manage projects, and build software together.', 'Sign up', 'New issue', 'Have a question about this project?', 'Sign up for a free GitHub account to open an issue and contact its maintainers and the community.', 'Pick a username', 'Email Address', 'Password', 'Sign up for GitHub', 'By clicking “Sign up for GitHub”, you agree to our', 'terms of service', 'and', 'privacy statement', '. We’ll occasionally send you account related emails.', 'Already on GitHub?', 'Sign in', 'to your account', 'Merged', 'Merged', 'Copy link', 'Quote reply', 'commented', 'Copy link', 'Quote reply', 'commented', 'Sign up for free', 'to join this conversation on GitHub', '.\n    Already have an account?', 'Sign in to comment', 'Assignees', 'Labels', 'None yet', 'None yet', 'Milestone', 'None yet', '© 2020 GitHub, Inc.', 'Terms', 'Privacy', 'Security', 'Status', 'Help', 'Contact GitHub', 'Pricing', 'API', 'Training', 'Blog', 'About', 'You can’t perform that action at this time.', 'You signed in with another tab or window.', 'Reload', 'to refresh your session.', 'You signed out in another tab or window.', 'Reload', 'to refresh your session.']

def extract_n_most_occurring_words_from_references(references, repo_url=None, n=20, return_urls=False, driver=None):
    '''
    Scrape the references and return the n most occurring words from a corpus containing all content of all references

    Input:
        references (list/str): list of references, or a string that is one reference
        repo_url (str): the reference can also be an # that refers to an issue page, therefore the repository url is needed
        n (int): the amount of words to return
        return_urls (bool): if you want to collect the urls from the pages --> PageRank
        driver: a webdriver can be provided to avoid javascript required pages
    
    Returns:
        str: the n most occurring words from a corpus containing all content of all references
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

def extract_project_name_from_repository_url(repo_url):
    '''
    Extract the project name from a repository URL through splitting the URL;
        @TODO: might be better to visit the URL and extract the project name via scraping

    Input:
        repo_url (str): The repository URL
    
    Returns:
        str: The project name
    '''
    project_name = re.sub('^https?://|[^\w]', ' ', repo_url)
    return ' '.join([token for token in project_name.split(' ') if token not in ['github', 'com', 'git', 'org']])

def map_description_to_repository_url(vulnerabilities_connection, vulnerability_id, description):
    '''
    Use the vulnerability database to predict a repository URL
        @TODO: the repository URL is now predicted based on the database, hence for a vulnerability affecting a repository
            which is not in the database, the prediction will not be correct

    Input:
        vulnerabilities_connection (sqlite3.connection): the connection with the vulnerabilities database
        vulnerability_id (str): if the vulnerability is already in the DB, the repository URL is already known
        description (list/str): the vulnerability description to use for the prediction

    Returns:
        str: the predicted repository URL
    '''
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
    '''
    The advisory record is the object containing all information on the vulnerability, 
        and will be used for finding the fix commit(s)
    '''
    def __init__(self, vulnerability_id, published_timestamp, repo_url, nvd_references, references_content, advisory_references, vulnerability_description, connection, preprocessed_vulnerability_description=None, relevant_tags=None, verbose=True, since=None, until=None):
        '''
        Information to provide when initializing an advisory record

        Input:
            vulnerability_id (str): the vulnerability ID, typically a CVE 
            published_timestamp (str/int): the timestamp at which the vulnerability was published, or patched if that is known 
            repo_url (str): the URL of the affected (GitHub) repository URL 
            nvd_references (list): references to which the NVD refers (1st level references)
            references_content (str): the content that was extracted from these references, and will be used to compare lexical similarity with
            advisory_references (list): the references that were extracted from the NVD references (2nd level references)
            vulnerability_description (str): the vulnerability description 
            connection (sqlite3.connection): the connection with the (commits) database

            Optional:
                preprocessed_vulnerability_description (str): if there is already a preprocess vulnerability description
                relevant_tags (list): a list of tags that are regarded as relevant tags (affected versions of the software)
                verbose (bool): to print intermediate output 
                since (timestamp): lower bound for selecting the candidate commits 
                until (timestamp): upper bound for selecting the candidate commits
        '''
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
        self.git_repo.clone(skip_existing=True) #@TODO: true or false..?
        self.connection = connection
        self.nvd_references = nvd_references
        self.references_content = references_content
        self.advisory_references = advisory_references

        #whether to print or not to print
        self.verbose = verbose
        
        self.since = since
        self.until = until

    class Reference:
        '''
        Used for analyzing the references
        '''
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
            @TODO: now only checking for /commit/ but it can also be /commits/
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
        '''
        To print the reference analysis as a pd.DataFrame()
        '''
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
        '''
        Check whether the candidate commits are already in the database, and add them otherwise
        '''
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
        '''
        Select commits to consider as candidate commits
        '''
        if self.since == None and self.until == None:
            self.since, self.until = database.timestamp_to_timestamp_interval(self.published_timestamp, days_before=days_before, days_after=days_after)

        ### Add commits before NVD release with maximum to add
        commit_ids_to_add_before = database.get_commit_ids_between_timestamp_interval(str(self.since), str(self.published_timestamp), git_repo=self.git_repo, repository_url=self.repo_url)
        if len(commit_ids_to_add_before) > 5215:
            commit_ids_to_add_before = commit_ids_to_add_before[:5215] #add the 5215 closest before the NVD release date

        ### Add commits after NVD release with a maximum to add
        commit_ids_to_add_after = database.get_commit_ids_between_timestamp_interval(str(self.published_timestamp), str(self.until), git_repo=self.git_repo, repository_url=self.repo_url)
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

def remove_project_name_from_string(string, project_name):
    '''
    Remove the project name from a string

    Input:
        string (str)
        project_name (str)

    Input:
        advisory_record: containing all information
        candidate_commit_df (pd.DataFrame): The dataframe containing the commit content
    '''
    try:
        return ' '.join([token for token in string.split(' ') if token not in project_name.split(' ')])
    except:
        return string

def check_preprocessing(advisory_record, candidate_commit_df):
    '''
    Checks whether the candidate commits are preprocessed, and does so when this is not the case
    '''
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

def remove_forbidden_words_from_string(string, forbidden_words):
    '''
    Removes forbidden words from string

    Input:
        string (str): the string to remove words from
        forbidden_words (list/str): the words to remove
    
    Returns:
        str: the string without the forbidden words
    '''
    if type(forbidden_words) == 'str':
        forbidden_words = forbidden_words.split(' ') 
    try:
        return ' '.join([token for token in string.split(' ') if token not in forbidden_words])
    except:
        return string

def compute_lexical_similarity_components(advisory_record, candidate_commit_df):
    '''
    This function computes the lexical similarity features:
        First, the descriptions are preprocessed and fix indicating words are added to the 
        description which is compared with the commit messages. The lexical similarity is
        computed for three vulnerability aspects:
         - the commit message + fix indicating words
         - the reference content
         - the code tokens extracted from the vulnerability description
        @TODO: the reference content and code tokens lexical similarity features are not of
        high predictive value, and it might be more efficient to discard these features
    
    Input:
        advisory_record: containing all information
        candidate_commit_df (pd.DataFrame): The dataframe containing the commit content

    Returns:
        pd.DataFrame: the candidate_commit_df with the lexical similarity features
    '''
    # DESCRIPTION
    project_name = simpler_filter_text(advisory_record.project_name)
    description = advisory_record.preprocessed_description
    description = remove_project_name_from_string(string=description, project_name=project_name)
    description_with_fix_indicating_words = description + ' '.join(fix_indicating_words) # for the commit message
    
    # CODE TOKENS
    code_tokens = simpler_filter_text(extract_code_tokens(advisory_record.description))
    code_tokens = remove_project_name_from_string(string=code_tokens, project_name=project_name)

    # define the different aspects and compute vector components
    tfidf_vectorizer_messages, tfidf_vectorizer_files, tfidf_vectorizer_diff = TfidfVectorizer(), TfidfVectorizer(), TfidfVectorizer()

    tfidf_messages = tfidf_vectorizer_messages.fit_transform([description_with_fix_indicating_words, advisory_record.references_content, code_tokens] + list(candidate_commit_df['preprocessed_message']))
    tfidf_files = tfidf_vectorizer_files.fit_transform([description, advisory_record.references_content, code_tokens] + list(candidate_commit_df['preprocessed_changed_files']))
    tfidf_diffs = tfidf_vectorizer_diff.fit_transform([description, advisory_record.references_content, code_tokens] + list(candidate_commit_df['preprocessed_diff']))

    # compute scores
    # can be done with multiprocessing
    if with_multiprocessing:
        with Pool(number_of_cpus) as p:
            # vulnerability description with fix indicating words
            candidate_commit_df['message_score'] = p.starmap(get_cosine_similarity, [(tfidf_messages[0], tfidf_messages[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['changed_files_score'] = p.starmap(get_cosine_similarity, [(tfidf_files[0], tfidf_files[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['git_diff_score'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[0], tfidf_diffs[index+3]) for index in range(len(candidate_commit_df))])

            # with nvd reference content
            candidate_commit_df['message_score_reference_content'] = p.starmap(get_cosine_similarity, [(tfidf_messages[1], tfidf_messages[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['changed_files_score_reference_content'] = p.starmap(get_cosine_similarity, [(tfidf_files[1], tfidf_files[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['git_diff_score_reference_content'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[1], tfidf_diffs[index+3]) for index in range(len(candidate_commit_df))])

            # with code tokens
            candidate_commit_df['message_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_messages[2], tfidf_messages[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['changed_files_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_files[2], tfidf_files[index+3]) for index in range(len(candidate_commit_df))])
            candidate_commit_df['git_diff_score_code_tokens'] = p.starmap(get_cosine_similarity, [(tfidf_diffs[2], tfidf_diffs[index+3]) for index in range(len(candidate_commit_df))])
    else:
        # vulnerability description
        candidate_commit_df['message_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[0], tfidf_messages[x.name+3])[0][0], axis=1) #x.name is index
        candidate_commit_df['changed_files_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[0], tfidf_files[x.name+3])[0][0], axis=1) 
        candidate_commit_df['git_diff_score'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[0], tfidf_diffs[x.name+3])[0][0], axis=1) 

        # with nvd reference content
        candidate_commit_df['message_score_reference_content'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[1], tfidf_messages[x.name+3])[0][0], axis=1) #x.name is index
        candidate_commit_df['changed_files_score_reference_content'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[1], tfidf_files[x.name+3])[0][0], axis=1) 
        candidate_commit_df['git_diff_score_reference_content'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[1], tfidf_diffs[x.name+3])[0][0], axis=1) 

        # with code tokens
        candidate_commit_df['message_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_messages[2], tfidf_messages[x.name+3])[0][0], axis=1) #x.name is index
        candidate_commit_df['changed_files_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_files[2], tfidf_files[x.name+3])[0][0], axis=1) 
        candidate_commit_df['git_diff_score_code_tokens'] = candidate_commit_df.apply(lambda x: cosine_similarity(tfidf_diffs[2], tfidf_diffs[x.name+3])[0][0], axis=1) 
    return candidate_commit_df

def is_path(token):
    '''
    Checks whether the token is a path (used for the path similarity score feature)

    Input:
        token (str)

    Returns:
        bool: whether the token is a path
    '''
    return '/' in token.rstrip('.,;:?!"\'') or ('.' in token.rstrip('.,;:?!"\'') and token.rstrip('.,;:?!"\'').split('.')[-1] in relevant_extensions)

def extract_code_tokens(description):
    '''
    Extract code tokens from the description: tokens that are either dot.case, snake_case or CamelCase and no path
        (paths are used in a different feature)
    '''
    tokens = [token.rstrip('.,;:?!"\'') for token in description.split(' ')] #remove punctuation etc.
    relevant_tokens = [token for token in tokens if not is_path(token) and (dot_case_split(token) or snake_case_split(token) or camel_case_split(token))]
    return relevant_tokens

def extract_path_tokens_from_text(text):
    '''
    Used to look for paths in the text (i.e. vulnerability description)

    Input:
        text (str)

    Returns:
        list: a list of paths that are found
    '''
    return [re.split('\.|,|/', token.rstrip('.,;:?!"\'')) for token in text.split(' ') if ('/' in token.rstrip('.,;:?!"\'') and not token.startswith('</')) or ('.' in token.rstrip('.,;:?!"\'') and token.rstrip('.,;:?!"\'').split('.')[-1] in relevant_extensions)]

def compute_path_similarity_score(changed_files, path_tokens_list):
    '''
    Provides a score for the found path and the changed files.
    - a description can mention multiple paths, therefore a sum is returned
    - a path can match multiple files, therefore the scores are first stored 
    in an intermediate score list and only the highest score is kept.

    Input:
        changed_files (str/list): the files that have been changed by the commit
        path_tokens_list (list): a list of path tokens found in the description (by extract_path_tokens_from_text())
    
    Returns:
        int: the score
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
            if with_extension == False:
                changed_file_tokens.pop(0) #remove the extension

            same_token_count, same_tokens = 0, True
            while same_tokens == True and same_token_count < len(reversed_path_tokens) and same_token_count < len(changed_file_tokens):
                if reversed_path_tokens[same_token_count] == changed_file_tokens[same_token_count]:
                    same_token_count += 1
                else:
                    same_tokens = False

            # adjust for only changing the right extension
            if with_extension and same_token_count == 1:
                same_token_count -= 1 
            intermediate_scores.append(same_token_count)
        path_similarity_scores.append(max(intermediate_scores))
    return sum(path_similarity_scores)

def calculate_time_distance_before(commit_timestamp, published_timestamp, first_candidate_timestamp):
    '''
    Used to compute a feature reflecting the distance from a commit and the vulnerability publication data,
        through comparing timestamps. The score is equal to 0.0 if the commit is after the release date, 
        and between 0.5 and 1.0 if the commit was before the vulnerability release. 
        The closer the commit is to the release, the higher the value.
    
    Input:
        commit_timestamp (int): the timestamp of the commit
        published_timestamp (int): the timestamp of the vulnerability publication
        first_candidate_timestamp (int): the timestamp of the first candidate commit

    Returns:
        float: the score
    '''
    return 0.5 + ((commit_timestamp - first_candidate_timestamp) / (published_timestamp - first_candidate_timestamp)) / 2 if commit_timestamp < published_timestamp else 0.0

def calculate_time_distance_after(commit_timestamp, published_timestamp, last_candidate_timestamp):
    '''
    Used to compute a feature reflecting the distance from a commit and the vulnerability publication data,
        through comparing timestamps. The score is equal to 0.0 if the commit is before the release date, 
        and between 0.5 and 1.0 if the commit was after the vulnerability release. 
        The closer the commit is to the release, the higher the value.
    
    Input:
        commit_timestamp (int): the timestamp of the commit
        published_timestamp (int): the timestamp of the vulnerability publication
        last_candidate_timestamp (int): the timestamp of the last candidate commit

    Returns:
        float: the score
    '''
    return 1 - ((commit_timestamp - published_timestamp) / (last_candidate_timestamp - published_timestamp)) / 2 if commit_timestamp > published_timestamp else 0.0

def tag_to_major_minor(tag):
    '''
    Return the digits corresponding to the major and minor of the tag,
        when versioning is done as MAJOR.MINOR.PATCH
    
    Input:
        tag (str)
    
    Returns:
        tuple: major digit, minor digit
    '''
    splitted_tag = filter.recursively_split_version_string(tag)
    splitted_tag_digits = [value for value in splitted_tag if type(value) == int]

    #when the tag has no digits
    if len(splitted_tag_digits) == 0:
        major, minor = 999, 999
    elif len(splitted_tag_digits) == 1:
        major = splitted_tag_digits[0]
        minor = 999
    else:
        major, minor = splitted_tag_digits[0], splitted_tag_digits[1]
    return major, minor

def tags_to_tree(tags):
    '''
    Arrange the tags in a tree (dict) with as nodes (keys) the major and minor versions
        based on semantic versioning: MAJOR.MINOR.PATCH

    Input:
        tags (list): a list of tags in the repository (git_repo.get_tags())

    Returns:
        dict: a dictionary where the keys are all major versions, 
            and the values are another dictionary with the minor versions as keys
            and a list of tags belonging to that minor version as values.
    '''
    result = dict()

    for tag in tags:
        major, minor = tag_to_major_minor(tag)

        # add to results
        if major not in result.keys(): 
            result[major] = dict()
        if minor not in result[major].keys():
            result[major][minor] = list()
        result[major][minor].append(tag)

    return result #{major: sorted(result[major], key = lambda x : x[1]) for major in result}

def sort_tags_tree(tree, tag_timestamp_dict):
    '''
    Sort the tags in the same branch (same MAJOR.MINOR) based on their timestamp
    Input:
        tree (dict): tree created by tags_to_tree(tags)
        tag_timestamp_dict (dict): a dictionary with tags a keys and timestamp as values
    
    Returns:
        dict: a dictionary where the keys are all major versions, 
            and the values are another dictionary with the minor versions as keys
            and a list of tags belonging to that minor version as values sorted on timestamp.
    '''
    sorted_tree = copy.deepcopy(tree)

    for major in sorted(list(sorted_tree.keys())):
        for minor in sorted(list(sorted_tree[major].keys())):
            tags = [(tag, tag_timestamp_dict[tag]) for tag in sorted_tree[major][minor]]
            tags = sorted(tags, key = lambda x : x[1])
            sorted_tree[major][minor] = tuple([tag[0] for tag in tags])
    return sorted_tree

def find_next_tag_in_tags_tree(tag, sorted_tags_tree, tag_timestamp_dict, tag_timestamp=None, first_call=True):
    '''
    Return the next tag in the tags tree
    --> NOT looking for tags with a different MAJOR (MAJOR.MINOR.PATCH)
    --> only returning a tag if it is indeed with a later timestamp

    Input:
        tag (str): the tag to map onto the next tag
        sorted_tags_tree (dict): tags stored in a tree, where the tags are sorted on
            timestamp (as returned by sort_tags_tree())
        tag_timestamp_dict (dict): a dictionary to lookup the tag timestamps

        Used for recursion (do not provide a value)
            tag_timestamp: to validate it is a later tag
            first_call: to return the original tag if there is no tag found

    Returns:
        str: the tag that is the next one
    '''
    if tag_timestamp == None and first_call == True:
        tag_timestamp = tag_timestamp_dict[tag]

    major, minor = tag_to_major_minor(tag)

    # if there is another tag in the same MAJOR.MINOR, return that one
    if sorted_tags_tree[major][minor].index(tag) < len(sorted_tags_tree[major][minor]) - 1:
        return sorted_tags_tree[major][minor][sorted_tags_tree[major][minor].index(tag)+1]

    # if there is another MINOR, return the first one in the next MINOR list
    if tuple(sorted_tags_tree[major]).index(minor) < len(sorted_tags_tree[major]) - 1:
        next_minor = tuple(sorted_tags_tree[major])[tuple(sorted_tags_tree[major]).index(minor)+1]
        possible_next_tag = sorted_tags_tree[major][next_minor][0]

        # validate that this tag is indeed with a later timestamp
        if tag_timestamp_dict[tag] < tag_timestamp_dict[possible_next_tag]:
            return possible_next_tag
        # try again for the possible next tag
        else: 
            return find_next_tag_in_tags_tree(possible_next_tag, sorted_tags_tree, tag_timestamp_dict, tag_timestamp, first_call=False)

    # if there is no tag with a later timestamp in the same MAJOR, return the original tag
    if first_call:
        return tag

def map_tag_onto_next_tag(tag, tag_timestamp_dict):
    '''
    Find the next tag for a given tag

    Input:
        tag (str)
        tag_timestamp_dict (dict): a dictionary to lookup the tag timestamps

    Returns:
        str: next tag
    '''
    tags = tuple(tag_timestamp_dict.keys())
    tags_tree = tags_to_tree(tags)
    sorted_tags_tree = sort_tags_tree(tags_tree, tag_timestamp_dict)
    return find_next_tag_in_tags_tree(tag, sorted_tags_tree, tag_timestamp_dict)

def calculate_reachability_score(row, tag_timestamp_dict, reachable_commits, relevant_tags, days_before):
    '''
    A function that can be applied row wise on the candidate commit df to calculate the reachability feature;
        a score is provided when a commit is reachable and within n days, and the score equals
        1.0 - (0.01 * n days difference)

    Input:
        (row)
        tag_timestamp_dict (dict): a dictionary to lookup the tag timestamps
        reachable_commits (list): not all commits are reachable from a given tag, this list contains
            the IDs of commits that are reachable and for which a score should be calculated
        relevant_tags (list): a list of tags to calculate the reachability from
        days_before (int): the maximum number of days the commit can be away from the tag timestamp and get a score of higher than 0.0
    
    Returns:
        float: the reachability score
    '''
    return 1.0 - (min([int((int(tag_timestamp_dict[tag]) - int(row['timestamp']))/86400) if row['id'] in reachable_commits[tag] else days_before for tag in relevant_tags]) / days_before) if len(relevant_tags) > 0 else 0.0
    
def compute_commit_distance_components(advisory_record, candidate_commit_df, days_before=100):
    '''
    This function computes the commit distance  features:
        - time distance before
        - time distance after
        - reachability score
    
    Input:
        advisory_record: containing all information
        candidate_commit_df (pd.DataFrame): The dataframe containing the commit content
        days_before:  the maximum number of days the commit can be away from the tag timestamp and get a reachability score of higher than 0.0

    Returns:
        pd.DataFrame: the candidate_commit_df with the commit distance features
    '''
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

    cursor.execute("SELECT tag, tag_timestamp FROM tags WHERE repo_url = :repo_url", {'repo_url':advisory_record.repo_url}) 
    tag_timestamp_dict = {row['tag'] : row['tag_timestamp'] for row in cursor}

    tags_to_calculate_reachability_from = tuple([map_tag_onto_next_tag(tag, tag_timestamp_dict) for tag in advisory_record.relevant_tags])
    tags_to_calculate_reachability_from = tuple(dict.fromkeys([tag for tag in tags_to_calculate_reachability_from if tag != None])) # none if there was no correct mapping with map_tag_onto_next_tag

    if len(tags_to_calculate_reachability_from) == 0:
        candidate_commit_df['reachability_score'] =  [0.0 for i in range(len(candidate_commit_df))]
        return candidate_commit_df

    # if there are tags that have been mentioned
    reachable_commits = dict()
    for tag in tags_to_calculate_reachability_from:
        since, until = database.timestamp_to_timestamp_interval(timestamp=tag_timestamp_dict[tag], days_before=days_before, days_after=0)
        reachable_commits[tag] = advisory_record.git_repo.get_commits(ancestors_of=tag, exclude_ancestors_of=None, since=since, until=until)

    # calculate scores
    candidate_commit_df['reachability_score'] = candidate_commit_df.apply(calculate_reachability_score, tag_timestamp_dict=tag_timestamp_dict, reachable_commits=reachable_commits, relevant_tags=tags_to_calculate_reachability_from, days_before=days_before, axis=1)
    
    return candidate_commit_df

def if_commit_id_in_list(commit_id, commits_found_list):
    '''
    Checks whether a commit ID was referred to, based on the first 8 characters

    Input:
        commit_id (str): the commit ID of the candidate commit
        commits_found_list (list): a list of commit IDs that were extracted from the references

    Returns:
        int: 1 if the commit was referred to, and 0 otherwise
    '''
    return 1 if commit_id[:8] in commits_found_list else 0

def compute_referred_to_components(advisory_record, candidate_commit_df):
    '''
    This function computes the commit distance features:
        - referred to by NVD (1st level)
        - referred to by advisories (2nd level)
    
    Input:
        advisory_record: containing all information
        candidate_commit_df (pd.DataFrame): The dataframe containing the commit content

    Returns:
        pd.DataFrame: the candidate_commit_df with the referred to features
    '''
    if 'commits_found_nvd' not in advisory_record.__dict__ and 'commits_found_adv' not in advisory_record.__dict__:
        advisory_record.analyse_references()

    candidate_commit_df['referred_to_by_nvd'] = candidate_commit_df['id'].apply(if_commit_id_in_list, commits_found_list=advisory_record.commits_found_nvd)
    candidate_commit_df['referred_to_by_advisories'] = candidate_commit_df['id'].apply(if_commit_id_in_list, commits_found_list=advisory_record.commits_found_adv)

    return candidate_commit_df

def if_vulnerability_id_in_message(message, vulnerability_id):
    '''
    Checks whether the vulnerability ID is in the commit message
    '''
    return 1 if vulnerability_id.lower() in message.lower() else 0

def if_other_vulnerability_id_in_message(message, vulnerability_id):
    '''
    Checks whether the vulnerability ID is NOT in the commit message but a differint ID is
    '''
    if vulnerability_id.lower() not in message.lower() and 'cve-' in message.lower(): 
        return 1
    return 0

def hunks_to_n_hunks(hunks):
    '''
    Count the number of hunks
    '''
    return len(ast.literal_eval(hunks))

def hunks_to_avg_hunk_size(hunks):
    '''
    Compute the average hunk size
    '''
    hunks = ast.literal_eval(hunks)
    return sum([h[1] - h[0] for h in hunks]) / len(hunks) if len(hunks) != 0 else 0

def contains_issue_reference(message_column):
    '''
    Check whether the commit message refers to an issue by means of a # followed by digits
    '''
    return 1 if len([result.group(0) for result in re.finditer('#\d+:?', ' '.join(ast.literal_eval(message_column)))]) > 0 else 0

def contains_jira_reference(message_column):
    '''
    Check whether the commit message refers to a Jira issue by means of a NAME-REF
    '''
    return 1 if len([result.group(0) for result in re.finditer('\w+-\d+:?', ' '.join(ast.literal_eval(message_column)))]) > 0 else 0

def changed_files_to_n_changed_files(changed_files):
    '''
    Count the number of changed files
    '''
    return len(ast.literal_eval(changed_files))

def compute_ranking_vectors_for_advisory_records_with_db(advisory_record, vulnerability_specific_scaling):
    '''
    Core functionality:
        Compute the feature vectors for the candidate commits

    Input:
        advisory_record:
        vulnerability_specific_scaling: variables can be scaled vulnerability specific, or on the entire training set
            --> if True, the largest number of the candidates will be scaled to one, otherwise it will not be scaled

    Returns:
        pd.DataFrame: a dataframe with the commit IDs and the features
    '''
    if 'candidate_commits' not in advisory_record.__dict__:
        raise ValueError('Advisory record does not contain candidate commits to rank')

    # candidate commit DF
    candidate_commit_df = pd.read_sql("SELECT * FROM commits WHERE id IN {} AND repository_url = '{}'".format(tuple(advisory_record.candidate_commits + [advisory_record.candidate_commits[0]]), advisory_record.repo_url), advisory_record.connection) # +[adisory_record.candidate_commits[0]] as SQL requires at least 2 items
    candidate_commit_df = check_preprocessing(advisory_record, candidate_commit_df)

    # creating the feature vectors
    candidate_commit_df['vulnerability_id_in_message'] = candidate_commit_df['message'].apply(if_vulnerability_id_in_message, vulnerability_id=advisory_record.id)
    candidate_commit_df['other_CVE_in_message'] = candidate_commit_df['message'].apply(if_other_vulnerability_id_in_message, vulnerability_id=advisory_record.id)

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
    candidate_commit_df = compute_commit_distance_components(advisory_record, candidate_commit_df, days_before=100)
    candidate_commit_df = compute_referred_to_components(advisory_record, candidate_commit_df)
    
    # normalize the values
    candidate_commit_df.drop(columns=['timestamp', 'preprocessed_diff', 'preprocessed_message', 'preprocessed_changed_files'], inplace=True)
    if vulnerability_specific_scaling:
        candidate_commit_df.iloc[:,1:] = MinMaxScaler().fit_transform(candidate_commit_df.iloc[:,1:])

    # add the vulnerability timestamp as a somewhat normalized component to allow for learning
    candidate_commit_df['vulnerability_timestamp'] = [int(advisory_record.published_timestamp) / seconds_per_month for i in range(len(candidate_commit_df))]
    candidate_commit_df = candidate_commit_df.rename(columns={'id' : 'commit_id'})
    return candidate_commit_df

def get_first_commit_timestamp(repo_url, git_repo=None):
    '''
    Get the timestamp of the first commit in the repository; used for the slider in the interface
    '''
    if git_repo == None:
        git_repo = Git(repo_url, cache_path=GIT_CACHE)
        git_repo.clone(skip_existing=True)

    all_commits = tuple(git_repo.get_commits())
    first_commit_id = all_commits[-1]
    commit = Commit(git_repo, first_commit_id)
    first_commit_timestamp = commit._exec.run('git show -s --format="%ct" ' + commit._id)[0][1:-1]
    return int(first_commit_timestamp)

##################################
###
### EVALUATE RANKING
###
##################################

# def ranking_vector_dict_to_df(ranking_vector_dict, ranking_vector_names):
#     '''
#     Previously, dictionaries were used to store the ranking vectors. These dictionaries had vulnerability IDs as keys,
#         and another dict as values, with commit IDs as keys and the ranking vectors as values. This has been changed 
#         to pd.DataFrame usage, this function can be used to turn one of these dictionaries to a dataframe.
#     '''
#     column_names = ['vulnerability_id', 'commit_id'] + ranking_vector_names

#     ranking_vector_df = pd.DataFrame()
#     for vulnerability_id, ranking_vectors in ranking_vector_dict.items():
#         rows = [[vulnerability_id, commit_id] + ranking_vector for commit_id, ranking_vector in ranking_vectors.items()]
#         ranking_vector_df = ranking_vector_df.append(pd.DataFrame(rows, columns=column_names))
#     ranking_vector_df.reset_index(drop=True, inplace=True)
#     return ranking_vector_df

def rank_candidates(model, ranking_vectors):
    '''
    Rank the candidate commits
    @TODO: add test case that the column ID is not dropped from original

    Input:
        model: the model to use (Scikit-Learn model with predict_proba method)
        ranking_vectors (pd.DataFrame): the dataframe with the features
    
    Returns:
        tuple: the commit IDs sorted on the probability of being the fix commit
    '''
    commit_ids = tuple(ranking_vectors.commit_id)
    ranking_vectors = ranking_vectors.drop(columns=['commit_id'])

    # predict the probability of a ranking vector in being the fix, or not
    predictions = model.predict_proba(ranking_vectors)
    commit_scores = [(candidate, predictions[index][1]) for index, candidate in enumerate(commit_ids)]
    return tuple([commit[0] for commit in sorted(commit_scores, key = lambda x : x[1], reverse=True)])

def rank_ranking_vectors(ranking_vector_df, vulnerability_ids, model):
    '''
    Rank the candidate commits

    Input:
        ranking_vector_df (pd.DataFrame): the dataframe with the features
        vulnerability_ids (list): the vulnerability IDs of the vulnerabilities to rank
        model: the model to use (Scikit-Learn model with predict_proba method)

    Returns:
        dict: A dictionary with the vulnerability IDs as key, and a list of commit IDs as values.
            The commit IDs are sorted on the probability of being the fix (ranked)
    '''
    ranked_vulnerability_candidates = dict()
    for vulnerability in vulnerability_ids:
        if vulnerability in tuple(ranking_vector_df.vulnerability_id.unique()):
            subset = ranking_vector_df[ranking_vector_df.vulnerability_id == vulnerability]
            commit_ids = subset.commit_id
            subset.drop(columns=['vulnerability_id', 'commit_id'], inplace=True)
            predictions = model.predict_proba(subset.reset_index(drop=True))
            commit_scores = [(candidate, predictions[index][1]) for index, candidate in enumerate(commit_ids)]
            ranked_vulnerability_candidates[vulnerability] = [commit[0] for commit in sorted(commit_scores, key = lambda x : x[1], reverse=True)]
    return ranked_vulnerability_candidates

def evaluate_ranking(ranked_vulnerability_candidates, vulnerabilities, fix_commits_df, validation_method='all', k=[5, 10], verbose=True):
    '''
    Evaluate the ranking results

    Input:
        ranked_vulnerability_candidates (dict): the ranking results as returned by rank_ranking_vectors()
        vulnerabilities (list): the vulnerability IDs of the vulnerabilities to evaluate
        fix_commits_df (pd.DataFrame): the dataframe with fix commits 
        validation_method (str): if set to 'all' validation will be based on averaging on all known fix commits,
            otherwise just on the highest ranked fix commit
        k (list): a list of positions (int) to add as a column in the evaluation df
        verbose (bool): to print additional output
    
    Returns:
        pd.DataFrame: a dataframe presenting the evaluation of the ranking
    '''
    no_fixes_count = 0
    no_fixes_found_count = 0

    if type(k) == int:
        k = [k]

    df = pd.DataFrame()

    for vulnerability, ranked_candidates in ranked_vulnerability_candidates.items():
        if vulnerability in vulnerabilities:
            if vulnerability not in list(fix_commits_df.vulnerability_id):
                no_fixes_count += 1

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

def analyse_ranking_results(ranking_results_df, method, train_or_test, k=[5, 10, 20]):
    '''
    Analyse the evaluated ranking by evaluate_ranking()

    Input:
        ranking_results_df (pd.DataFrame): the result of evaluate_ranking()
        method (str): a textual column will be added containing this value
        train_or_test (str): to specify it is the train or test data
        k (list): a list of positions (int) to add as a column in the evaluation df
    
    Returns:
        pd.DataFrame: a dataframe presenting the ranking results
    '''
    df = pd.DataFrame()
    
    df.at[0, 'method'] = method
    df.at[0, 'train_or_test'] = train_or_test
    df.at[0, 'avg_precision'] = np.mean(ranking_results_df.precision)
    df.at[0, 'avg_max_ranking_pos'] = np.mean(ranking_results_df.max_ranking_position)
    df.at[0, 'med_max_ranking_pos'] = np.median(ranking_results_df.max_ranking_position)
    df.at[0, 'n'] = len(ranking_results_df)

    for position in k:
        fixes_in_top_k = len(ranking_results_df[(ranking_results_df.max_ranking_position < position) & (ranking_results_df.n_fix_commits <= position)]) + len(ranking_results_df[(ranking_results_df.max_ranking_position < ranking_results_df.n_fix_commits) & (ranking_results_df.n_fix_commits > position)])
        df.at[0, 'recall_at_{}'.format(position)] = round(fixes_in_top_k / len(ranking_results_df) * 100, 2)
    return df

def analyze_cross_validate_df(cross_validate_df, validation_methods_to_keep=['all', 'best']):
    '''
    Analyse the ranking results by analyse_ranking_results() on the different splits, reporting standard deviation etc.

    Input:
        ranking_results_df (pd.DataFrame): the results of analyse_ranking_results() with cross validation
        validation_methods_to_keep (list): a list of values used for the validation methods
    
    Returns:
        pd.DataFrame: a dataframe presenting the ranking results
    '''
    cross_validate_df = cross_validate_df.copy()

    columns = ['avg_precision', 'avg_max_ranking_pos', 'med_max_ranking_pos', 'recall_at_5', 'recall_at_10', 'recall_at_20']
    column_values_dict = {column : list() for column in columns}
    
    # # process the entries
    cross_validate_df['validation_method'] = cross_validate_df['method'].apply(lambda x: x.split('-')[1])
    cross_validate_df['method'] = cross_validate_df['method'].apply(lambda x: x.split('-')[0])
    cross_validate_df['avg_precision'] = cross_validate_df['avg_precision'].apply(lambda x: round(x * 100, 2))

    cross_validate_df = cross_validate_df[cross_validate_df.validation_method.isin(validation_methods_to_keep)]

    if len(validation_methods_to_keep) > 1:
        # #select the relevant rows
        cross_validate_df.drop(columns=['index'], inplace=True)
        grouped_cross_validate_df = cross_validate_df.groupby(['train_or_test', 'method', 'validation_method']).mean()
        
        for row in grouped_cross_validate_df.iterrows():
            subset = cross_validate_df[(cross_validate_df.method == row[0][1]) & (cross_validate_df.validation_method == row[0][2]) & (cross_validate_df.train_or_test == row[0][0])]
            for column in columns:
                column_values_dict[column].append('{} ({})'.format(round(row[1][column], 2), round(subset[column].std(), 2)))

        # add to the dataframe
        for column in columns:
            grouped_cross_validate_df[column] = column_values_dict[column]
        return grouped_cross_validate_df
    else:
        cross_validate_df.drop(columns=['index', 'validation_method'], inplace=True)
        grouped_cross_validate_df = cross_validate_df.groupby(['train_or_test', 'method']).mean()

        for row in grouped_cross_validate_df.iterrows():
            subset = cross_validate_df[(cross_validate_df.method == row[0][1]) & (cross_validate_df.train_or_test == row[0][0])]
            for column in columns:
                column_values_dict[column].append('{} ({})'.format(round(row[1][column], 2), round(subset[column].std(), 2)))

        # add to the dataframe
        for column in columns:
            grouped_cross_validate_df[column] = column_values_dict[column]
        return grouped_cross_validate_df
