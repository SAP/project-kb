# This file is used to create a database with commit content

import os, sys, ast, json, time, datetime, requests, sqlite3, re, random
from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

current_working_directory = os.getcwd()
os.chdir('git_explorer')
sys.path.append(os.getcwd())

# os.environ['GIT_CACHE'] = current_working_directory + '/git_explorer/git_explorer_cache'
# GIT_CACHE = current_working_directory + '/git_explorer/git_explorer_cache'

GIT_CACHE = ''
if 'GIT_CACHE' in os.environ:
    GIT_CACHE = os.environ['GIT_CACHE']

from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

import filter
import rank

##################################
###
### "MAGIC NUMBERS"
###
##################################

# to remove from extracted content
strings_on_every_GitHub_page = ['Skip to content', 'Why GitHub?', 'Features', '→', 'Code review', 'Project management', 'Integrations', 'Actions', 'Packages', 'Security', 'Team management', 'Hosting', 'Mobile', 'Customer stories', '→', 'Security', '→', 'Team', 'Enterprise', 'Explore', 'Explore GitHub', '→', 'Learn & contribute', 'Topics', 'Collections', 'Trending', 'Learning Lab', 'Open source guides', 'Connect with others', 'Events', 'Community forum', 'GitHub Education', 'Marketplace', 'Pricing', 'Plans', '→', 'Compare plans', 'Contact Sales', 'Nonprofit', '→', 'Education', '→', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'No suggested jump to results', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'In this repository', 'All GitHub', '↵', 'Jump to', '↵', 'Sign\xa0in', 'Sign\xa0up', '/', 'Watch', 'Star', 'Fork', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'More', 'Code', 'Pull requests', 'Actions', 'Security', 'Insights', 'Dismiss', 'Join GitHub today', 'GitHub is home to over 50 million developers working together to host and review code, manage projects, and build software together.', 'Sign up', 'New issue', 'Have a question about this project?', 'Sign up for a free GitHub account to open an issue and contact its maintainers and the community.', 'Pick a username', 'Email Address', 'Password', 'Sign up for GitHub', 'By clicking “Sign up for GitHub”, you agree to our', 'terms of service', 'and', 'privacy statement', '. We’ll occasionally send you account related emails.', 'Already on GitHub?', 'Sign in', 'to your account', 'Merged', 'Merged', 'Copy link', 'Quote reply', 'commented', 'Copy link', 'Quote reply', 'commented', 'Sign up for free', 'to join this conversation on GitHub', '.\n    Already have an account?', 'Sign in to comment', 'Assignees', 'Labels', 'None yet', 'None yet', 'Milestone', 'None yet', '© 2020 GitHub, Inc.', 'Terms', 'Privacy', 'Security', 'Status', 'Help', 'Contact GitHub', 'Pricing', 'API', 'Training', 'Blog', 'About', 'You can’t perform that action at this time.', 'You signed in with another tab or window.', 'Reload', 'to refresh your session.', 'You signed out in another tab or window.', 'Reload', 'to refresh your session.']

# these terms are used as test urls and do not refer to an actual reference
test_url_terms = ['localhost', 'example', 'mydomain']

##################################
###
### MAPPING
###
##################################

# A list of URLs in the data set that are not GitHub repositories
repo_urls_to_github_url_mapping_dict = {
    'http://svn.apache.org/repos/asf/tomcat/tc6.0.x' : 'https://github.com/apache/tomcat',
    'http://git.apache.org/cordova-plugin-file-transfer' : 'https://github.com/apache/cordova-plugin-file-transfer',
    'http://svn.apache.org/repos/asf/tomcat/tc8.0.x' : 'https://github.com/apache/tomcat',
    'http://svn.apache.org/repos/asf/httpcomponents/httpclient' : 'https://github.com/apache/httpcomponents-client',
    'http://svn.apache.org/repos/asf/hive' : 'https://github.com/apache/hive',
    'https://git.apache.org/hive' : 'https://github.com/apache/hive',
    'http://git.apache.org/ambari' : 'https://github.com/apache/ambari',
    'http://git.apache.org/camel' : 'https://github.com/apache/camel',
    'https://git-wip-us.apache.org/repos/asf/camel': 'https://github.com/apache/camel',
    'http://git.apache.org/cxf' : 'https://github.com/apache/cxf',
    'http://svn.apache.org/repos/asf/cxf' : 'https://github.com/apache/cxf',
    'https://svn.apache.org/repos/asf/cxf' : 'https://github.com/apache/cxf',
    'https://git-wip-us.apache.org/repos/asf/cxf' : 'https://github.com/apache/cxf',
    'https://git1-us-west.apache.org/repos/asf/cxf' : 'https://github.com/apache/cxf',
    'http://git.apache.org/cxf-fediz' : 'https://github.com/apache/cxf-fediz',
    'http://git.apache.org/hbase' : 'https://github.com/apache/hbase',
    'http://git.apache.org/struts' : 'https://github.com/apache/struts',
    'http://svn.apache.org/repos/asf/struts' : 'https://github.com/apache/struts',
    'https://git.apache.org/struts' : 'https://github.com/apache/struts',
    'http://git.apache.org/tapestry-5' : 'https://github.com/apache/tapestry-5',
    'http://svn.apache.org/repos/asf/activemq' : 'https://github.com/apache/activemq',
    'https://git-wip-us.apache.org/repos/asf/activemq' : 'https://github.com/apache/activemq',
    'https://git.apache.org/activemq' : 'https://github.com/apache/activemq',
    'http://svn.apache.org/repos/asf/myfaces' : 'https://github.com/apache/myfaces',
    'http://svn.apache.org/repos/asf/pdfbox': 'https://github.com/apache/pdfbox',
    'http://svn.apache.org/repos/asf/poi' : 'https://github.com/apache/poi',
    'https://svn.apache.org/repos/asf/poi' : 'https://github.com/apache/poi',
    'http://svn.apache.org/repos/asf/roller' : 'https://github.com/apache/roller',
    'http://svn.apache.org/repos/asf/shiro' : 'https://github.com/apache/shiro',
    'http://svn.apache.org/repos/asf/sling' : 'https://github.com/apache/sling',
    'http://svn.apache.org/repos/asf/syncope' : 'https://github.com/apache/syncope',
    'http://svn.apache.org/repos/asf/tomcat' : 'https://github.com/apache/tomcat',
    'http://git.bouncycastle.org/repositories/bc-java' : 'https://github.com/bcgit/bc-java',
    'http://svn.apache.org/repos/asf/qpid' : 'https://github.com/apache/qpid',
    'http://svn.apache.org/repos/asf/santuario/xml-security-java' : 'https://github.com/apache/santuario-xml-security-java',
    'http://svn.apache.org/repos/asf/geronimo' : 'https://github.com/apache/geronimo',
    'http://svn.apache.org/repos/asf/jakarta/httpcomponents/httpclient' : 'https://github.com/apache/httpcomponents-client',
    'http://svn.apache.org/repos/asf/xmlgraphics/batik' : 'https://github.com/apache/xmlgraphics-batik',
    'https://svn.apache.org/repos/asf/db/derby' : 'https://github.com/apache/derby',
    'https://git-wip-us.apache.org/repos/asf/commons-fileupload' : 'https://github.com/apache/commons-fileupload',
    'https://git-wip-us.apache.org/repos/asf/lucene-solr' : 'https://github.com/apache/lucene-solr',
    'https://git-wip-us.apache.org/repos/asf/tomee' : 'https://github.com/apache/tomee',
    'https://android.googlesource.com/platform//external/conscrypt' : 'https://github.com/google/conscrypt'
 }

##################################
###
### FUNCTIONS
###
##################################

def timestamp_to_timestamp_interval(timestamp, days_before, days_after):
    '''
    Function to map a timestamp to an interval of two timestamps, 
        the interval can be specified by the variables days_before and days_after.

    Input:
        timestamp (str/int/float): timestamp in format i.e. '123456789'
        days_before (str/int): the number of days before the input timestamp
        days_after (str/int): the number of days after the input timestamp

    Returns:
        tuple: timestamp - days_before, timestamp + days_after
    '''
    since = str(int((datetime.datetime.fromtimestamp(int(timestamp)) - datetime.timedelta(days=int(days_before))).timestamp()))
    until = str(int((datetime.datetime.fromtimestamp(int(timestamp)) + datetime.timedelta(days=int(days_after))).timestamp()))
    return since, until

def get_commit_ids_between_timestamp_interval(since, until, git_repo=None, repository_url=None):
    '''
    Function to get all commit IDs that have been committed in the timestamp interval
        Based on git_explorer.core.get_commits()
        The order is from newest to oldest: the result[0] is the most recent one (larger timestamp), the result[-1] is the oldest (smallest timestamp)
    
    Input:
        since (str/int/float): timestamp in format i.e. '123456789'
        until (str/int/float): timestamp in format i.e. '123456789'
        git_repo (git_explorer.core.Git): to use for extracting the content
        repository_url (str): if git_repo is not provided, a repository url is needed to initialize the git_repo
    
    Returns:
        list: the commit IDs that have been committed in the timestamp interval
    '''
    if git_repo == None and repository_url ==None:
        raise ValueError('Provide a git_repo or a repository_url')
    
    if int(since) >= int(until):
        raise ValueError('The timestamps provided result in an interval without commit IDs, as since >= until.')
    
    if git_repo == None:
        git_repo = Git(repository_url, cache_path=GIT_CACHE)
        git_repo.clone(skip_existing=True)
        
    # create git command
    cmd = ["git", "rev-list", "--all"]
    cmd.append("--since=" + str(since))
    cmd.append("--until=" + str(until))
    
    try:
        out = git_repo._exec.run(cmd)
    except:
        print("Git command failed. Could not obtain commit ids.")
        return
    
    return [l.strip() for l in out]

def get_hunks_from_diff(diff_lines): 
    '''  
    Extracts the hunks from the Git diff
        based on git_explorer/commit.py get_hunks()

    Input:
        diff_lines (list): the diff content as returned by Git

    Returns:
        list: a list of integer tuples containing the hunk information
    '''
    def is_hunk_line(line):
        return line[0] in '-+' and (len(line) < 2 or (line[1] != line[0]))

    def flatten_groups(hunk_groups):
        hunks = []
        for group in hunk_groups:
            for h in group:
                hunks.append(h)
        return hunks

    def is_new_file(l):
        return (l[0:11] == 'diff --git ')

    # in the DB, the content is stored as strings as
    if type(diff_lines) == str:
        try:
            diff_lines = ast.literal_eval(diff_lines)
            print('The diff_lines is in string format, while a list is expected. ast.literal_eval() is used to transform it.')
        except:
            raise TypeError('The diff_lines provided do not seem be git diff lines!')

    first_line_of_current_hunk, current_group, line_no, hunks = -1, [], 0, []

    for line_no, line in enumerate(diff_lines):

        if is_new_file(line):
            if len(current_group) > 0:
                hunks.append(current_group)
                current_group = []
                first_line_of_current_hunk = -1

        elif is_hunk_line(line):
            if first_line_of_current_hunk == -1:
                # print('first_line_of_current_hunk', line_no)
                first_line_of_current_hunk = line_no
        else:
            if first_line_of_current_hunk != -1:
                current_group.append((first_line_of_current_hunk, line_no))
                first_line_of_current_hunk = -1

    if first_line_of_current_hunk != -1:
        # wrap up hunk that ends at the end of the patch
        # print('line_no:', line_no)
        current_group.append((first_line_of_current_hunk, line_no + 1))

    hunks.append(current_group)

    return flatten_groups(hunks)

def get_changed_files_from_diff(diff_lines):
    '''  
    Extracts the changed files from the Git diff

    Input:
        diff_lines (str/list): the diff content as returned by Git

    Returns:
        list: a list of changed files
    '''  
    if type(diff_lines) == str:
        try:
            diff_lines = ast.literal_eval(diff_lines)
            print('The diff_lines is in string format, while a list is expected. ast.literal_eval() is used to transform it.')
        except:
            raise TypeError('The diff_lines provided do not seem be git diff lines!')

    return list(dict.fromkeys([changed_file.lstrip('a/, b/') for line in diff_lines if line.startswith('diff --git') for changed_file in line.lstrip('diff --git ').split(' ')]))

def extract_commit_message_reference_content(commit_message, repo_url, driver=None):
    '''
    Can be used to find references in commit messages and extract the content from these references

    Input:
        commit_message (list/str): the commit message
        repo_url (str): the repository URL (when commits refer to a Git issue)
        driver: a webdriver can be provided to avoid javascript required pages
    
    Returns:
        list: a list containing the preprocessed content of the references that have been found
    '''
    if type(commit_message) == list:
        commit_message = ' '.join(commit_message)

    repo_url = re.sub('\.git$|/$', '', repo_url) 
    references = rank.find_references(commit_message)
    references_content = list()
    
    for reference in references:
        time.sleep(0.5)
        try:
            if 'http' not in reference:
                url = repo_url + '/issues/' + reference.lstrip('#')
                r = requests.get(url)
                soup = BeautifulSoup(r.content, "html.parser")

                # check if reference is found and whether it is an issue or pull page
                if reference.lstrip('#') in r.url and ('/issues/' in r.url or '/pull/' in r.url):
                    references_content.append(rank.simpler_filter_text(' '.join([string for string in soup.stripped_strings if string not in strings_on_every_GitHub_page])))
            else: 
                if 'securityfocus.com' in reference.strip('/.'): #securityfocus.com requires a selection in a menu
                    reference = reference.strip('/.') + '/discuss' 

                try:
                    r = requests.get(reference.strip('.')) #can be end of the sentence
                    soup = BeautifulSoup(r.content, "html.parser")
                    reference_content = ' '.join([string for string in soup.stripped_strings])

                    # Apache pony mail requires the webdriver to see the content
                    if 'requires JavaScript enabled' in reference_content and driver != None:

                        driver.get(reference.strip('.'))
                        time.sleep(0.5)
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        reference_content = ' '.join([string for string in soup.stripped_strings])

                    references_content.append(rank.simpler_filter_text(reference_content))
                except:
                    if driver != None:
                        driver.get(reference.strip('.'))
                        time.sleep(0.5)
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        reference_content = ' '.join([string for string in soup.stripped_strings])
                        references_content.append(rank.simpler_filter_text(reference_content))
        except:
            print('Failed in obtaining content for reference {}'.format(reference))

    return references_content

##################################
###
### DATABASE
###
##################################

def connect_with_database(path, as_row_factory=True, verbose=True):
    '''
    Connects with the database, if create_new_database is True a new .db will be created:

    Input:
        path (str): the path where the database can be found or should be created. Can be set to ":memory:" to prototype in memory.
        as_row_factory (bool): SQLite allows for a dict-like usage, when as_row_factory=True this functionality is used.
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    
    Returns:
        sqlite3.connection: the connection with the database
        sqlite3.cursor: the cursor of the database
    '''
    # creates the file if it is not there, otherwise connects with it
    connection = sqlite3.connect(path)
    
    if as_row_factory:
        connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT COUNT(id) FROM commits")
        if verbose: print('Opening database on path {}'.format(path))
    except:
        if verbose: print('Creating new database on path {}'.format(path))
        create_commits_table(connection)
        create_repositories_table(connection)
        create_tags_table(connection)

    cursor.execute("SELECT COUNT(id) FROM commits")
    if as_row_factory and verbose:
        print('Database contains {} commits'.format(cursor.fetchone()['COUNT(id)']))
    elif verbose:
        print('Database contains {} commits'.format(cursor.fetchone()[0]))
    return connection, cursor

##################################
###
### COMMITS TABLE
###
##################################

def create_commits_table(connection):
    '''
    Input:
        sqlite3.connection: the connection with the database
    '''
    cursor = connection.cursor()
    with connection:
        cursor.execute('''CREATE TABLE commits (
            repository_url text,
            id text,
            timestamp text,

            message text,
            changed_files text,
            diff text,
            hunks text,
            commit_message_reference_content text,

            preprocessed_message text,
            preprocessed_diff text,
            preprocessed_changed_files text,
            preprocessed_commit_message_reference_content text

        )''')

        cursor.execute("CREATE INDEX IF NOT EXISTS commit_index ON commits(id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS repository_index ON commits(repository_url)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS commit_repository_index ON commits(id, repository_url)")

    print('    Table commits successfully created')
    cursor.close()
    return

def add_commits_to_database(connection, commit_ids, git_repo=None, repository_url=None, driver=None, with_message_references_content=False, verbose=True):
    '''
    Add commits to the database

    Input:
        connection (sqlite3.connection): the connection to the database
        commit_ids (list): a list of commit_ids
        git_repo (git_explorer.core.Git): to use for extracting the content
        repository_url (str): if git_repo is not provided, a repository url is needed to initialize the git_repo
        driver: a webdriver can be provided to avoid javascript required pages
        with_message_references_content (bool): to add commits references (requires additional time)
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    if git_repo == None and repository_url ==None:
        raise ValueError('Provide a git_repo or a repository_url')
        
    if git_repo == None:
        git_repo = Git(repository_url, cache_path=GIT_CACHE)
        git_repo.clone(skip_existing=True)
    
    if repository_url==None:
        repository_url = git_repo.get_url()
    repository_url = re.sub('\.git$|/$', '', repository_url)
    
    if type(commit_ids) == str:
        commit_ids = [commit_ids]
    if len(commit_ids) == 0:
        print('No commit IDs were provided')
        return
    
    cursor = connection.cursor()
    
    # to not add duplicates
    commit_ids = list(dict.fromkeys(commit_ids))  # to get only unique ids
    commits_already_in_the_db = list(pd.read_sql("SELECT id FROM commits WHERE id IN {} and repository_url = '{}'".format(tuple(commit_ids+[commit_ids[0]]), repository_url), connection).id)
    commits_to_add = [commit_id for commit_id in commit_ids if commit_id not in commits_already_in_the_db]

    if len(commits_to_add) == 0:
        cursor.close()
        return

    if verbose: print('    {} / {} are already in the database, now adding the rest.'.format(len(commits_already_in_the_db), len(commit_ids)))

    for commit_id in tqdm(commits_to_add):
        try:
            # initialize commit object
            commit = Commit(git_repo, commit_id)

            # message execution is combined with timestamp execution to speed up to process
            message = commit._exec.run(['git', 'log', '--format=%B%n%ct', '-n1', commit._id])
            timestamp = message.pop(-1)

            diff = commit._exec.run(['git', 'diff', '--unified=1', commit._id + "^.." + commit._id])
            changed_files = get_changed_files_from_diff(diff)
            hunks = get_hunks_from_diff(diff)

            preprocessed_message = rank.simpler_filter_text(message)
            preprocessed_diff = rank.simpler_filter_text(re.sub('[^A-Za-z0-9]+', ' ', ' '.join(rank.extract_relevant_lines_from_commit_diff(diff))))
            preprocessed_changed_files = rank.simpler_filter_text(changed_files)
            
            if with_message_references_content:
                commit_message_reference_content = extract_commit_message_reference_content(message, repository_url, driver)
                preprocessed_commit_message_reference_content = rank.extract_n_most_occurring_words(commit_message_reference_content, n=20)
            else:
                commit_message_reference_content, preprocessed_commit_message_reference_content = None, None
                
            # add to database
            with connection:
                cursor.execute("INSERT INTO commits VALUES (:repository_url, :id, :timestamp, :message, :changed_files, :diff, :hunks, :commit_message_reference_content, :preprocessed_message, :preprocessed_diff, :preprocessed_changed_files, :preprocessed_commit_message_reference_content)", 
                    {'repository_url':repository_url, 'id':commit_id, 'timestamp':str(timestamp), 'message':str(message), 'changed_files':str(changed_files), 'diff':str(diff), 'hunks':str(hunks), 'commit_message_reference_content':commit_message_reference_content, 'preprocessed_message':preprocessed_message, 'preprocessed_diff':preprocessed_diff, 'preprocessed_changed_files':preprocessed_changed_files, 'preprocessed_commit_message_reference_content':preprocessed_commit_message_reference_content})
        except:
            print('    Failed to add commit {}'.format(commit_id))
    if verbose: print('    All commits have been added to the database.')
    cursor.close()
    return

##################################
###
### REPOSITORIES TABLE
###
##################################

def create_repositories_table(connection):
    '''
    Create the repositories table

    Input:
        sqlite3.connection: the connection with the database
    '''
    cursor = connection.cursor()
    with connection:
        cursor.execute('''CREATE TABLE repositories (
            repo_url text,
            project_name text
        )''')

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS repository_index ON repositories(repo_url)")

    print('    Table repositories successfully created')
    cursor.close()
    return

def add_repository_to_database(connection, repo_url, project_name, verbose=True):
    '''
    Add repositories to the database

    Input:
        connection (sqlite3.connection): the connection to the database
        repo_url (str): the repository url to add
        project_name (str): the project name to add
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    repo_url = re.sub('\.git$|/$', '', repo_url) 
    cursor = connection.cursor()

    # if it does not exist yet
    if cursor.execute("SELECT EXISTS(SELECT 1 FROM repositories WHERE repo_url = :repo_url LIMIT 1) AS 'exists';", {'repo_url':'repo_url'}).fetchone()['exists'] == 0:
        with connection:
            cursor.execute("INSERT INTO repositories VALUES (:repo_url, :project_name)", 
                {'repo_url':repo_url, 'project_name':project_name})
        if verbose: print('    Successfully added repository to the repositories table.')
    elif verbose:
        print('    repo_url {} is already in the db'.format(repo_url))
    cursor.close()
    return
    
##################################
###
### TAGS TABLE
###
##################################

def create_tags_table(connection):
    '''
    Create the tags table

    Input:
        sqlite3.connection: the connection with the database
    '''
    cursor = connection.cursor()
    with connection:
        cursor.execute('''CREATE TABLE tags (
            tag text,
            repo_url text,
            tag_timestamp text
        )''')

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS tags_index ON tags(tag, repo_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS repository_index ON tags(repo_url)")
    print('    Table tags successfull created')
    cursor.close()
    return

def add_tags_to_database(connection, tags=None, git_repo=None, repo_url=None, verbose=True):
    '''
    Add tags to the database

    Input:
        connection (sqlite3.connection): the connection to the database
        tags (list): a list of tags
        git_repo (git_explorer.core.Git): to use for extracting the content
        repo_url (str): if git_repo is not provided, a repository url is needed to initialize the git_repo
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    if git_repo == None and repo_url ==None:
        raise ValueError('Provide a git_repo or a repo_url')

    if git_repo == None:
        git_repo = Git(repo_url, cache_path=GIT_CACHE)
        git_repo.clone(skip_existing=False)
    
    if repo_url==None:
        repo_url = git_repo.get_url()

    repo_url = re.sub('\.git$|/$', '', repo_url) 

    if tags == None:
        tags = git_repo.get_tags()
    elif type(tags) == str:
        tags = [tags]
    if len(tags) == 0:
        return

    cursor = connection.cursor()

    # to not add duplicates
    tags = list(dict.fromkeys(tags))  # to get only unique tags
    cursor.execute("SELECT tag FROM tags WHERE repo_url = :repo_url AND tag IN {}".format(tuple(tags)), {'repo_url':repo_url})
    tags_already_in_the_db = list(pd.read_sql("SELECT tag FROM tags WHERE tag IN {} and repo_url = '{}'".format(tuple(tags+[tags[0]]), repo_url), connection).tag)
    tags_to_add = [tag for tag in tags if tag not in tags_already_in_the_db]

    if len(tags_to_add) == 0:
        cursor.close()
        return

    print('    Adding new tags to the database')
    for tag in tqdm(tags_to_add):
        try:
            tag_timestamp = filter.get_timestamp_for_tag(tag, git_repo)

            # add to database
            cursor.execute("INSERT INTO tags VALUES (:tag, :repo_url, :tag_timestamp)",
                {'tag':tag, 'repo_url':repo_url, 'tag_timestamp':str(tag_timestamp)})
        except:
            print('    Failed to add tag {}'.format(tag))

    connection.commit()
    if verbose: print('    {} / {} tags were already in the database and added the rest.'.format(len(tags_already_in_the_db), len(tags)))
    cursor.close()
    return

##################################
###
### VULNERABILITIES DATABASE
###
##################################

def connect_with_vulnerabilities_database(path, as_row_factory=True, verbose=True):
    '''
    Connects with a VULNERABILITIES database, if create_new_database is True a new .db will be created
        @TODO: This database can be combined into one database; not really a need for two separate DBs

    Input:
        path (str): the path where the database can be found or should be created. Can be set to ":memory:" to prototype in memory.
        as_row_factory (bool): SQLite allows for a dict-like usage, when as_row_factory=True this functionality is used.
        verbose: "Definition of verbose: containing more words than necessary: WORDY"

    Returns:
        sqlite3.connection: the connection with the database
        sqlite3.cursor: the cursor of the database
    '''
    # creates the file if it is not there, otherwise connects with it
    connection = sqlite3.connect(path)
    
    if as_row_factory:
        connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS vulnerability_id ON vulnerabilities(vulnerability_id)")
    except:
        # db does not exist yet
        create_vulnerabilities_table(connection)
        create_vulnerability_references_table(connection)
        create_vulnerability_fixes_table(connection)
        create_advisory_references_table(connection)

    cursor.execute("SELECT COUNT(vulnerability_id) FROM vulnerabilities")
    if as_row_factory and verbose:
        print('Database contains {} vulnerabilities'.format(cursor.fetchone()['COUNT(vulnerability_id)']))
    elif verbose:
        print('Database contains {} vulnerabilities'.format(cursor.fetchone()[0]))
    return connection, cursor

# VULNERABILITIES

def create_vulnerabilities_table(connection):
    '''
    @TODO: change published_date --> published_timestamp, and type from string to int

    Input:
        sqlite3.connection: the connection with the database
    '''
    cursor = connection.cursor()
    
    with connection:
        cursor.execute('''CREATE TABLE vulnerabilities (
            vulnerability_id text,
            repo_url text,
            description text,
            published_date text,

            preprocessed_description text
        )''')
        cursor.execute("CREATE INDEX IF NOT EXISTS vulnerability_id ON vulnerabilities(vulnerability_id)")

    print('    Table vulnerabilities successful created')
    cursor.close()
    return

def if_new_vulnerability(cursor, vulnerability_id):
    '''
    Check whether the vulnerability is already in the database, based on the vulnerability ID

    Input:
        cursor (sqlite3.cursor): the cursor of the database
        vulnerability_id (str): the identifier of the vulnerability

    Returns:
        boolean: True when the vulnerability ID is not yet in the db
    '''
    if cursor.execute("SELECT EXISTS(SELECT 1 FROM vulnerabilities WHERE vulnerability_id = :vulnerability_id LIMIT 1) AS 'exists';", {'vulnerability_id':vulnerability_id}).fetchone()['exists'] == 0:
        return True
    return False

def extract_nvd_content(vulnerability_id):
    '''
    Extracts the content from the NVD by means of the rest-api

    Input:
        vulnerability_id (str): the vulnerability ID provided by the user

    Returns:
        str: the vulnerability description
        int: the NVD published timestamp
        list: the references from the NVD
    '''
    vulnerability_id = re.sub('https://|nvd.nist.gov/vuln/detail/', '', vulnerability_id) #someone might provide an NVD url
    nist_nvd_request_url = 'https://services.nvd.nist.gov/rest/json/cve/1.0/'
    r = requests.get(nist_nvd_request_url+vulnerability_id)
    assert r.ok == True, "vulnerability ID {} is not in the NVD".format(vulnerability_id)
    cve_content = r.json()

    description = cve_content['result']['CVE_Items'][0]['cve']['description']['description_data'][0]['value']
    published_timestamp = int(time.mktime(datetime.datetime.strptime(cve_content['result']['CVE_Items'][0]['publishedDate'].split('T')[0], "%Y-%m-%d").timetuple()))
    references = [reference['url'] for reference in cve_content['result']['CVE_Items'][0]['cve']['references']['reference_data']]
    return description, published_timestamp, references

def add_vulnerability_to_database(connection, vulnerability_id, repo_url, description=None, published_timestamp=None, references=None, driver=None, verbose=True):
    '''
    Input:
        connection (sqlite3.connection): the connection with the database
        vulnerability_id (str): the identifier of the vulnerability
        repo_url (str): the repository url
        description (str): the description of the vulnerability can be provided manually, or will be extracted from the NVD
        published_timestamp (str): vulnerability published timestamp can be provided manually, or will be extracted from the NVD
        references (list): vulnerability references can be provided manually, or will be extracted from the NVD
        driver: i.e. a chromedriver can be provided to scrape with when requests does not succeed
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    if type(published_timestamp) == int:
        published_timestamp = str(published_timestamp)

    #preprocess repo_url entry
    repo_url = re.sub('\.git$|/$', '', repo_url)

    cursor = connection.cursor()
    if if_new_vulnerability(cursor, vulnerability_id):

        # gather information for the new vulnerability if needed
        if description == None or published_timestamp == None or references == None:
            try:
                nvd_description, nvd_published_timestamp, nvd_references = extract_nvd_content(vulnerability_id)
            except: #if the vulnerability is not in the NVD
                nvd_description, nvd_published_timestamp, nvd_references = None, None, None

            if description == None:
                if nvd_description == None:
                    raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability description manually.".format(vulnerability_id))
                else:
                    description = nvd_description
            if published_timestamp == None:
                if nvd_published_timestamp == None:
                    raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a vulnerability published timestamp manually.".format(vulnerability_id))
                else:
                    published_timestamp = nvd_published_timestamp
            if references == None:
                if nvd_references == None:
                    raise ValueError("Since the provided vulnerability ID {} cannot be found in the NVD, you must provide a advisory references manually.".format(vulnerability_id))
                else:
                    references = nvd_references
            
        # add to the database
        preprocessed_description = rank.simpler_filter_text(description)
        with connection:
            cursor.execute("INSERT INTO vulnerabilities VALUES (:vulnerability_id, :repo_url, :description, :published_timestamp, :preprocessed_description)",
            {'vulnerability_id':vulnerability_id, 'repo_url':repo_url, 'description':description, 'published_timestamp':str(published_timestamp), 'preprocessed_description':preprocessed_description})
    
        # add the references to the database
        if references != None and len(references) > 0:
            add_vulnerability_references_to_database(connection, vulnerability_id, references, driver=driver, verbose=verbose)
    elif verbose:
        print("    There is already a vulnerability with ID {} in the database".format(vulnerability_id))
    cursor.close()
    return

# REFERENCES

def create_vulnerability_references_table(connection):
    '''
    Input:
        sqlite3.connection: the connection with the database
        sqlite3.cursor: the cursor of the database
    '''
    cursor = connection.cursor()
    
    with connection:
        cursor.execute('''CREATE TABLE vulnerability_references (
            url text,
            vulnerability_id text,
            preprocessed_content text
        )''')
        cursor.execute("CREATE INDEX IF NOT EXISTS reference_index ON vulnerability_references(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS vulnerability_id_index ON vulnerability_references(vulnerability_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS reference_and_vulnerability_id_index ON vulnerability_references(url, vulnerability_id)")

    print('    Table vulnerability_references successful created')
    cursor.close()
    return

def add_vulnerability_references_to_database(connection, vulnerability_id, references, driver=None, verbose=True):
    '''
    Input:
        connection (sqlite3.connection): the connection with the database
        vulnerability_id (str): the identifier of the vulnerability
        references (list): the (NVD) references
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
        driver: a webdriver can be provided to avoid javascript required pages
    '''
    if type(references) == str:
        references = [references]

    cursor = connection.cursor()

    for reference in references:
        # cursor.execute("SELECT * FROM vulnerability_references WHERE url = :url AND vulnerability_id = :vulnerability_id;",
                    #    {'url' : reference, 'vulnerability_id':vulnerability_id})
        # if len(cursor.fetchall()) == 0:

        if cursor.execute("SELECT EXISTS(SELECT 1 FROM vulnerability_references WHERE  url = :url AND vulnerability_id = :vulnerability_id LIMIT 1) AS 'exists';", {'url' : reference, 'vulnerability_id':vulnerability_id}).fetchone()['exists'] == 0:
            time.sleep(random.random())
            if reference[-4:] == '.pdf' and verbose:
                print('    Skipping reference since reference is a pdf')
            elif any([term in reference for term in test_url_terms]) == False:
                try:
                    if 'securityfocus.com' in reference.strip('/.'): #securityfocus.com requires a selection in a menu
                        reference = reference.strip('/.') + '/discuss' 
                    try:
                        r = requests.get(reference.strip('.')) #can be end of the sentence
                        soup = BeautifulSoup(r.content, "html.parser")
                        reference_content = ' '.join([string for string in soup.stripped_strings])

                        # Apache pony mail requires the webdriver to see the content
                        if 'requires JavaScript enabled' in reference_content and driver != None:

                            driver.get(reference.strip('.'))
                            time.sleep(0.5)
                            soup = BeautifulSoup(driver.page_source, "html.parser")
                            reference_content = ' '.join([string for string in soup.stripped_strings])
                    except:
                        if driver != None:
                            driver.get(reference.strip('.'))
                            time.sleep(0.5)
                            soup = BeautifulSoup(driver.page_source, "html.parser")
                            reference_content = ' '.join([string for string in soup.stripped_strings])

                    preprocessed_reference_content = rank.simpler_filter_text(reference_content)

                    # add to database
                    with connection:
                        cursor.execute("INSERT INTO vulnerability_references VALUES (:url, :vulnerability_id, :preprocessed_content)",
                            {'url':reference.strip('/'), 'vulnerability_id':vulnerability_id, 'preprocessed_content':str(preprocessed_reference_content)})

                    try:
                        # add the urls referred to on these pages to the advisory references DB
                        urls_found = [link.get('href').strip('/') for link in soup.find_all('a') if link.get('href') and 'http' in link.get('href')]
                        add_advisory_references_to_database(connection, vulnerability_id, urls_found)
                    except:
                        print("Failed in adding advisory references")
                except:
                    print('    reference {} could not be added to the db'.format(reference))
        elif verbose:
            print('    reference {} is already in the db'.format(reference))
    cursor.close()
    return

def create_advisory_references_table(connection, verbose=True):
    '''
    # @TODO: add a column that contains the URL from which this URL is obtained, 
        to allow for deselecting references on the NVD level and thereby also deselecting
        the advisory references that have been extracted from this NVD reference.

    Input:
        sqlite3.connection: the connection with the database
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    cursor = connection.cursor()
    
    with connection:
        cursor.execute('''CREATE TABLE advisory_references (
            url text,
            vulnerability_id text
        )''')

        cursor.execute("CREATE INDEX IF NOT EXISTS reference_index ON advisory_references(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS vulnerability_id_index ON advisory_references(vulnerability_id)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS reference_and_vulnerability_id_index ON advisory_references(url, vulnerability_id)")
    if verbose: print('    Table advisory_references successfully created')
    cursor.close()
    return

def add_advisory_references_to_database(connection, vulnerability_id, references, verbose=True):
    '''
    # @TODO: add a column that contains the URL from which this URL is obtained

    Input:
        connection (sqlite3.connection): the connection with the database
        vulnerability_id (str): the identifier of the vulnerability
        references (list): the advisory references
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    if type(references) == str:
        references = [references]

    cursor = connection.cursor()

    for reference in references:
        # check if the advisory url is not in the DB
        if cursor.execute("SELECT EXISTS(SELECT 1 FROM advisory_references WHERE  url = :url AND vulnerability_id = :vulnerability_id LIMIT 1) AS 'exists';", {'url' : reference, 'vulnerability_id':vulnerability_id}).fetchone()['exists'] == 0:
        
            # add to database
            with connection:
                cursor.execute("INSERT INTO advisory_references VALUES (:url, :vulnerability_id)",
                    {'url':reference, 'vulnerability_id':vulnerability_id})
        elif verbose:
            print('    reference {} is already in the db'.format(reference))
    cursor.close()
    return

# FIXES

def create_vulnerability_fixes_table(connection):
    '''
    Input:
        sqlite3.connection: the connection with the database
        sqlite3.cursor: the cursor of the database
    '''
    cursor = connection.cursor()
    
    with connection:
        cursor.execute('''CREATE TABLE fix_commits (
            commit_id text,
            vulnerability_id text,
            repo_url text
        )''')

        cursor.execute("CREATE INDEX IF NOT EXISTS commit_index ON fix_commits(commit_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS vulnerability_id_index ON fix_commits(vulnerability_id)")
    print('    Table fix_commits successfully created')
    cursor.close()
    return

def add_vulnerability_fixes_to_database(connection, vulnerability_id, commit_ids, repo_url, verbose=True):
    '''
    Input:
        connection (sqlite3.connection): the connection with the database
        vulnerability_id (str): the identifier of the vulnerability
        commit_ids (list): the identifier of the fix commits
        repo_url (str): the repository url
        verbose (bool): "Definition of verbose: containing more words than necessary: WORDY"
    '''
    cursor = connection.cursor()
    
    if type(commit_ids) == str: #if one commit id is provided
        commit_ids = [commit_ids]
    repo_url = re.sub('\.git$|/$', '', repo_url)

    for commit_id in commit_ids:

        if cursor.execute("SELECT EXISTS(SELECT 1 FROM fix_commits WHERE  commit_id = :commit_id AND vulnerability_id = :vulnerability_id LIMIT 1) AS 'exists';", {'commit_id' : commit_id, 'vulnerability_id':vulnerability_id}).fetchone()['exists'] == 0:

            # add to database
            with connection:
                cursor.execute("INSERT INTO fix_commits VALUES (:commit_id, :vulnerability_id, :repo_url)",
                    {'commit_id':commit_id, 'vulnerability_id':vulnerability_id, 'repo_url':repo_url})
        elif verbose:
            print("    Fix {} for vulnerability {} is already in the db".format(commit_id, vulnerability_id))
    cursor.close()
    return
