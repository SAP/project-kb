import os, sys, re, difflib, spacy, time, datetime, ast
import numpy as np
import pandas as pd
nlp = spacy.load('en_core_web_sm')

current_working_directory = os.getcwd()
os.chdir('git_explorer')
sys.path.append(os.getcwd())

os.environ['GIT_CACHE'] = current_working_directory + '/git_explorer/git_explorer_cache'
GIT_CACHE = current_working_directory + '/git_explorer/git_explorer_cache'
from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

import database
import rank

##################################
###
### "MAGIC NUMBERS"
###
##################################

# the following extensions are regarded as relevant extensions for being a fix commit
relevant_extensions = ["java", "c", "cpp", "h", "py", "js", "xml", "go", "rb", "php", "sh", "scale", "lua", "m", "pl", "ts", "swift", "sql", "groovy", "erl", "swf", "vue", "bat", "s", "ejs", "yaml", "yml", "jar"]

##################################
###
### SELECTING COMMITS BASED ON VERSIONS
###
##################################

def filter_description(description):
    '''
    Returns:
        list: a list of relevant words within sentences where version numbers are mentioned 
    '''

    doc = nlp(description)

    relevant_sentences = list()

    for sentence in list(doc.sents): 

        relevant_tokens_in_sentence = list()

        for token_index, token in enumerate(sentence):
            if token.tag_ in ['IN', 'RBR', 'RB', 'VBG', 'JJR'] or token.is_alpha == False and token.is_punct == False or token.lemma_ in ['inclusive']: relevant_tokens_in_sentence.append(token)

            #only keep punctuation before  the version
            if token.text in ['-'] and 'd.d' in sentence[token_index - 1].shape_: relevant_tokens_in_sentence.append(token)

        for token in relevant_tokens_in_sentence:
            if 'd.d' in token.shape_ and token.text[-1].lower() != 'x' and relevant_tokens_in_sentence not in relevant_sentences:

                #apply a padding
                relevant_tokens_in_sentence = [nlp('padding')[0]] + relevant_tokens_in_sentence + [nlp('padding')[0]]
                relevant_sentences.append(relevant_tokens_in_sentence)

    return relevant_sentences

def retreive_all_versions_from_description(description):
    '''
    Input:
        description (str): the description of the vulnerability (with a version mentioned)

    Returns:
        list: a list with every version that is mentioned
    '''
    if type(description) != str:
        raise TypeError('The provided description should be a str data type but is of type {}.'.format(type(description)))

    versions = list()
    doc = nlp(description)

    for token in doc:
        if 'd.d' in token.shape_ and token.text[-1].lower() != 'x':
            versions.append(token.text)
    return versions

def recursively_split_version_string(input_version, output_version=[]):
    '''
    Splits a version/tag string into a list with integers and strings
        i.e. "8.0.0.RC10" --> [8, '.', 0, '.', 0, '.RC', 10]

    Input:
        input_version (str): a version or tag i.e. "8.0.0.RC10"
        output_version (list): an empty list, which will be filled iteratively

    Returns:
        list: the version/tag string in a list with integers and strings i.e. [8, '.', 0, '.', 0, '.RC', 10]
    '''
    if type(input_version) != str:
        raise TypeError('The provided version should be a str data type but is of type {}.'.format(type(input_version)))

    #when the part to split is only digits or no digits at all, the process is finished
    if input_version.isdigit() or any(char.isdigit() for char in input_version) == False:
        version = output_version + [input_version]
        return [int(character) if character.isdigit() else character for character in version]

    #otherwise check until what position it is a digit (since we want to keep i.e. a multiple digits number as one integer)
    pos = 0
    while input_version[pos].isdigit() == input_version[pos+1].isdigit() and pos != len(input_version)-2: # 
        pos += 1

    return recursively_split_version_string(input_version[pos+1:], output_version + [input_version[:pos+1]])

def get_tag_for_version(tags, version):
    '''
    Map a version onto an existing tag

    Input:
        tags (list): a list of tags to map version onto
        version (str): the version

    Returns:
        list: list with tags that could be the version
        @TODO: only return the most relevant tag i.e. for key 8 version 4.1 returns ['version-3.4.1', 'version-4.1', 'version-4.4.1']
    '''
    if type(tags) != list or len(tags) == 0:
        raise ValueError('tags should be a list of tags to map the version onto, is a {} of length {}'.format(type(tags), len(tags)))

    # stripped_tags = [tag[len(tag)-len(version):] for tag in tags]
    stripped_tags = [tag[tag.index([str(value) for value in recursively_split_version_string(tag) if type(value) == int][0]):] if any(char.isdigit() for char in tag) else tag for tag in tags]
    stripped_version = version[version.index([str(value) for value in recursively_split_version_string(version) if type(value) == int][0]):] if any(char.isdigit() for char in version) else version

    if version in tags and tags.count(version) == 1:
        tag = version
    elif version in stripped_tags and stripped_tags.count(version) == 1:
        tag = tags[stripped_tags.index(version)]
    elif version in stripped_tags and stripped_tags.count(version) > 1:
        return [tags[index] for index, tag in enumerate(stripped_tags) if tag == version]
    elif stripped_version in stripped_tags and stripped_tags.count(stripped_version) == 1:
        tag = tags[stripped_tags.index(stripped_version)]
    elif stripped_version in stripped_tags and stripped_tags.count(stripped_version) > 1:
        return [tags[index] for index, tag in enumerate(stripped_tags) if tag == stripped_version]

    else:
        version = re.sub("[^0-9]", "", version)
        best_match = ('', 0.0)
        for tag in tags:
            t_strip = re.sub("[^0-9]", "", tag)
            match_score = difflib.SequenceMatcher(None, t_strip, version).ratio()
            if match_score > best_match[1]:
                best_match = (tag, match_score)
        tag = best_match[0]
    return [tag]

def get_timestamp_for_tag(tag, git_repo):
    '''
    Retreive the timestamp the tag was created.

    Input:
        repo_url (str): the repository where the tag can be found
        tag (str): the tag

    Return:
        int: timestamp (use datetime.fromtimestamp(timestamp) for datetime)
    '''
    if type(git_repo) != Git:
        raise TypeError('git-repo should be of type git_explorer.core.Git, not {}'.format(type(git_repo)))
    if type(tag) != str:
        raise TypeError('tag must be str, not {}'.format(type(tag)))
    if tag not in git_repo.get_tags():
        raise ValueError('tag {} not found in git_repo'.format(tag))


    commit_id = git_repo.get_commit_id_for_tag(tag)
    commit = Commit(git_repo, commit_id)
    return int(commit.get_timestamp())

def find_next_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
    '''
    Tries to find the next tag by means of incrementing digits in the tag

    Input:
        tag (str): the tag
        tags (list): all tags
        (digit_indices should not be provided, is used for the recursion)
        (loop does not have to be provided, is used for the recursion)

    Returns:
        str: the next tag
    '''
    if type(tags) != list or len(tags) == 0:
        raise ValueError('tags should be a list of tags to map the version onto, is a {} of length {}'.format(type(tags), len(tags)))
    if type(git_repo) != Git:
        raise TypeError('git-repo should be of type git_explorer.core.Git, not {}'.format(type(git_repo)))

    # splits the tag into a list of integers and strings
    splitted_tag = recursively_split_version_string(tag, [])

    # determines which indices in the list correspond to digits of the version number
    if digit_indices == None:
        if tag_timestamp == None:
            tag_timestamp = get_timestamp_for_tag(tag, git_repo)
        digit_indices = list(reversed([index for index, val in enumerate(splitted_tag) if type(val) == int]))
        loop = 0

    # searching for valid tags: recursively to evaluate different 
    tried_indices = []
    for index in digit_indices:

        # as we're looking for the next tag, it is unlikely that there will be a gap of more than 10
        for i in range(10): 
            splitted_tag[index] += 1

            possible_tag = ''.join([str(x) for x in splitted_tag])

            if possible_tag in tags:
                possible_tag_timestamp = get_timestamp_for_tag(possible_tag, git_repo)
                if tag_timestamp < possible_tag_timestamp:
                    return possible_tag

            if len(tried_indices) != 0:
                result = find_next_tag(possible_tag, tags, tag_timestamp, git_repo, tried_indices, loop+1)
                if result:
                    return result

        #when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.9
        splitted_tag[index] = 0
        tried_indices.append(index)

    #when every combination is tried, chop off the last part of the tag
    if loop == 0 and len(tag) > 1:
        shortened_tag = ''.join([str(x) for x in recursively_split_version_string(tag, [])[:-1]])
        return find_next_tag(shortened_tag, tags, tag_timestamp, git_repo)

    # None is returned when there is no match
    return

def find_previous_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
    '''
    Tries to find the previous tag by means of decrementing digits in the tag, 
        and checking whether the new tag exists. It starts at the last digit and works it way back. 
        When all digits have become 0, the last element of tag is removed and the process is tried again.

    Input:
        tag (str): the tag
        tags (list): all tags
        (digit_indices should not be provided, is used for the recursion)

    Returns:
        str: the previous tag
    '''
    if type(tags) != list or len(tags) == 0:
        raise ValueError('tags should be a list of tags to map the version onto, is a {} of length {}'.format(type(tags), len(tags)))
    if type(git_repo) != Git:
        raise TypeError('git-repo should be of type git_explorer.core.Git, not {}'.format(type(git_repo)))

    # splits the tag into a list of integers and strings
    splitted_tag = recursively_split_version_string(tag, [])

    # determines which indices in the list correspond to digits of the version number
    if digit_indices == None:
        if tag_timestamp == None:
            tag_timestamp = get_timestamp_for_tag(tag, git_repo)
        loop = 0
        digit_indices = list(reversed([index for index, val in enumerate(splitted_tag) if type(val) == int]))

    # searching for valid tags: recursively to evaluate different 
    tried_indices = []
    for index in digit_indices:

        i = 0
        #sometimes a date is used (thus takes a long time)
        if splitted_tag[index] < 100:
            while splitted_tag[index] > 0: 
                i += 1
                splitted_tag[index] -= 1

                possible_tag = ''.join([str(x) for x in splitted_tag])

                if possible_tag in tags:
                    possible_tag_timestamp = get_timestamp_for_tag(possible_tag, git_repo)
                    if tag_timestamp > possible_tag_timestamp:
                        return possible_tag

                if len(tried_indices) != 0:
                    result = find_previous_tag(possible_tag, tags, tag_timestamp, git_repo, tried_indices, loop+1)
                    if result:
                        return result

        #when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.99
        splitted_tag[index] = 99
        tried_indices.append(index) 

    #when every combination is tried, chop off the last part of the tag
    if loop == 0 and len(tag) > 1:
        shortened_tag = ''.join([str(x) for x in recursively_split_version_string(tag, [])[:-1]])
        # print(shortened_tag)
        return find_previous_tag(shortened_tag, tags, tag_timestamp, git_repo)
    return

def version_to_wide_interval_tags(tags, version, git_repo, tag_margin=1):
    '''
    A version is mapped onto a tag, and a tuple of a wide version interval is returned
        [0] corresponds to the previous tag
        [1] corresponds to the next tag

    Input:
        tags (list): a list of tags to map version onto
        version (str): the version
        git_repo (git_explorer.GIT): 
        tag_margin (int): how wide the interval can be

    Returns:
        # tuple: previous tag, next tag
        list: for every tag, returns a tuple with previous tag, current next tag
        @TODO: return only one tuple: previous tag, next tag
    '''
    result = list()

    # can return multiple tags now, as matching is not perfect
    for tag in get_tag_for_version(tags, version):

        tag_timestamp = get_timestamp_for_tag(tag, git_repo)

        previous_tag = find_previous_tag(tag, tags, tag_timestamp, git_repo)
        if previous_tag == None:
            if tags.index(tag) != 0:
                previous_tag = tags[tags.index(tag)-1]
            else:
                previous_tag = tags[tags.index(tag)]

        for i in range(tag_margin-1):
            # when no valid new version has been found but the current version is in the tags
            possible_previous_tag = find_previous_tag(previous_tag, tags, tag_timestamp, git_repo)
            if possible_previous_tag == None:
                break
            else:
                previous_tag = possible_previous_tag

        next_tag = find_next_tag(tag, tags, tag_timestamp, git_repo)
        if next_tag == None:
            if tags.index(tag) != len(tags)-1:
                next_tag = tags[tags.index(tag)+1]
            else:
                next_tag = tags[tags.index(tag)]

        for i in range(tag_margin-1):
            possible_next_tag = find_next_tag(next_tag, tags, tag_timestamp, git_repo)
            if possible_next_tag == None:
                break
            else:
                next_tag = possible_next_tag

        if (previous_tag, tag) not in result: result.append((previous_tag, tag))
        if (tag, next_tag) not in result: result.append((tag, next_tag))
    return result

# def description_to_narrow_intervals(description, tags):
#     '''
#     Input:
#         description (str): the description of the vulnerability (with a version mentioned)

#     Returns:
#         list: a list of pairs of versions
#             [0]: the last known configuration that was vulnerable
#             [1]: the first known configuration that was no longer vulnerable (patched)
#     '''
#     tag_intervals = list()

#     relevant_sentences = filter_description(description)

#     for sentence in relevant_sentences:
#         for token_index, token in enumerate(sentence):
            
#             # often stated like: version 1.11.x before 1.11.23, therefore a version ending on x can be skipped
#             if 'd.d' in token.shape_ and token.text[-1].lower() != 'x':
#                 vulnerable_version, fixed_version = 0, 0

#                 # when the term (i.e. early) is before the version number the version is most likely fixed
#                 if sentence[token_index - 1].lemma_ in ['before', 'early', 'to']:
#                     fixed_version = token.text

#                 # when the term (i.e. early) is after the version number the version is most likely vulnerable
#                 elif sentence[token_index + 1].lemma_ in ['before', 'early', 'to', 'inclusive']:
#                     vulnerable_version = token.text

#                 # when it is an enumeration i.e. 1.2, 1.3, 1.4 and 1.5, or a standalone 
#                 # elif 'd.d' in sentence[token_index + 1].shape_ and sentence[token_index + 1].text != version_to_next_version(token.text):
#                 #     vulnerable_version = token.text
                
#                 # not indicating a range
#                 elif sentence[token_index - 1].lemma_ in ['through', 'in', 'include', 'inclusive'] and sentence[token_index + 1].text not in ['-']: 
#                     vulnerable_version = token.text

#                 # add to tag intervals list
#                 if vulnerable_version != 0:
#                     for tag in get_tag_for_version(tags, vulnerable_version):
#                         next_tag = find_next_tag(tag, tags)
#                         if next_tag != None and (tag, next_tag) not in tag_intervals: tag_intervals.append((tag, next_tag))
#                 elif fixed_version != 0:
#                     for tag in get_tag_for_version(tags, fixed_version):
#                         previous_tag = find_previous_tag(tag, tags)
#                         if previous_tag != None and (previous_tag, tag) not in tag_intervals: tag_intervals.append((previous_tag, tag))
#                 else: # when it is none of the above, add both version intervals
#                     for tag in get_tag_for_version(tags, token.text):
#                         next_tag = find_next_tag(tag, tags)
#                         previous_tag = find_previous_tag(tag, tags)
#                         if next_tag != None and (tag, next_tag) not in tag_intervals: tag_intervals.append((tag, next_tag))
#                         if previous_tag != None and (previous_tag, tag) not in tag_intervals: tag_intervals.append((previous_tag, tag))
#     return tag_intervalsTypeError

def get_commits_between_interval_tags(intervals_tags, git_repo=None, repo_url=None):
    '''
    Finds the commits between intervals tags

    Input:
        intervals_tags (list): tags for version intervals
        repo_url (str): the URL of the repository to draw the commits from

    Returns:
        list: a list with IDs for commits in the intervals
    '''
    candidate_commits = list()

    # obtain candidate commits with git-explorer
    if git_repo == None:
        try: 
            git_repo = Git(repo_url, cache_path=GIT_CACHE)
            git_repo.clone(skip_existing=True)
        except:
            raise TypeError('git-repo should be of type git_explorer.core.Git, not {}, or repo_url should be a valid github repository url.'.format(type(git_repo)))

    for interval_tags in intervals_tags:
        t1, t2 = interval_tags

        #@TODO: one tag before this one
        cid_1 = git_repo.get_commit_id_for_tag(t1)
        c1 = Commit(git_repo, cid_1)
        time_1 = c1.get_timestamp()

        cid_2 = git_repo.get_commit_id_for_tag(t2)
        c2 = Commit(git_repo, cid_2)

        candidates = git_repo.get_commits(since=time_1, ancestors_of=cid_2, exclude_ancestors_of=cid_1, filter_files='*')

        candidate_commits += candidates

    return list(dict.fromkeys(candidate_commits)) #only unique ids

##################################
###
### SELECTING COMMITS BASED ON NVD RELEASE DATE
###
##################################

def select_commit_ids_based_on_vulnerability_publish_date(vulnerability_published_timestamp, git_repo=None, repo_url=None, days_before=730, days_after=100, commits_before_cap=5215, commits_after_cap=100):
    '''
    To select commit IDs based on the vulnerability publish date. 
    This can be used as a starting position for the search for fix commits.

    Input:
        vulnerability_published_timestamp (int): the timestamp at which the vulnerability is been published i.e. in the NVD
        git_repo (git_explorer.core.Git): to use for extracting the content
        repository_url: if git_repo is not provided, a repository url is needed to initialize the git_repo
        days_before (int): the maximum number of days before the release timestamp (edge)
        days_after (int): the maximum number of days after the release timestamp (edge)
        commits_before_cap (int): the maximum number of commits before the release timestamp (edge)
        commits_after_cap (int): the maximum number of commits after the release timestamp (edge)

    Returns:
        list: a list of commit IDs within the interval
    '''

    if git_repo == None:
        try: 
            git_repo = Git(repo_url, cache_path=GIT_CACHE)
            git_repo.clone(skip_existing=True)
        except:
            raise TypeError('git-repo should be of type git_explorer.core.Git, not {}, or repo_url should be a valid github repository url.'.format(type(git_repo)))

    ### Add commits before NVD release
    since, until = database.timestamp_to_timestamp_interval(int(vulnerability_published_timestamp), days_before=days_before, days_after=0)
    commit_ids_to_add_before = database.get_commit_ids_between_timestamp_interval(str(since), str(until), git_repo=git_repo, repository_url=repo_url)

    # maximum to add
    if len(commit_ids_to_add_before) > commits_before_cap:
        commit_ids_to_add_before = commit_ids_to_add_before[:commits_before_cap] #add the 5215 closest before the NVD release date

    ### Add commits after NVD release
    since, until = database.timestamp_to_timestamp_interval(int(vulnerability_published_timestamp), days_before=0, days_after=days_after)
    commit_ids_to_add_after = database.get_commit_ids_between_timestamp_interval(str(since), str(until), git_repo=git_repo, repository_url=repo_url)

    # maximum to add
    if len(commit_ids_to_add_after) > commits_after_cap:
        commit_ids_to_add_after = commit_ids_to_add_after[-commits_after_cap:] #add the 100 closest before the NVD release date

    commit_ids = commit_ids_to_add_before + commit_ids_to_add_after

    return commit_ids

##################################
###
### MAIN FUNCTION
###
##################################

def map_advisory_record_onto_candidate_commits(advisory_record):
    '''
    Map the advisory record onto candidate commits.

    Input: 
        advisory_record (dict)

    Returns:
        list: a list of IDs of candidate commits
    '''
    if 'repo_url' not in advisory_record or 'description' not in advisory_record:
        raise ValueError('advisory record should contain variables repo_url and description.')

    # clone repository
    git_repo = Git(advisory_record['repo_url'], cache_path=GIT_CACHE)
    git_repo.clone(skip_existing=False)
    tags = git_repo.get_tags()

    versions_in_description = retreive_all_versions_from_description(advisory_record['description'])

    tag_intervals = list()

    for version in versions_in_description:

        # map the mentioned version onto an interval of tags and add them to the list
        for version_interval_tags in version_to_wide_interval_tags(tags, version, git_repo):
            if version_interval_tags not in tag_intervals and version_interval_tags != None:
                tag_intervals.append(version_interval_tags)

    #map the list of intervals onto candidate commits
    candidate_commits = get_commits_between_interval_tags(tag_intervals, git_repo=git_repo)
    return candidate_commits

##################################
###
### FILTER FUNCTIONS
###
##################################

def extract_extensions_from_changed_files(changed_files):
    if type(changed_files) == str:
        changed_files = ast.literal_eval(changed_files)
    return [changed_file.split(".")[-1] for changed_file in changed_files]

def changes_relevant_file(extensions):
    return any([extension in relevant_extensions for extension in extensions]) 

# makes use of the DB
def filter_commits_on_files_changed_extensions(commit_ids, connection, return_irrelevant_commits=False, verbose=True):
    '''
    Removes commits that did not change a code file, and hence cannot be a fix commit

    Input:
        commit_ids (list): the commits to inspect
        connection (sqlite3.connection): the connection with the database
        cursor (sqlite3.cursor): the cursor of the database
    '''
    commit_changed_files_df = pd.read_sql_query("SELECT id, changed_files FROM commits WHERE id in {}".format(tuple(commit_ids+[commit_ids[0]])), connection)
    commit_changed_files_df['extensions'] = commit_changed_files_df['changed_files'].apply(extract_extensions_from_changed_files)
    commit_changed_files_df['changes_relevant_file'] = commit_changed_files_df['extensions'].apply(changes_relevant_file)
    irrelevant_commits_based_on_extension = list(commit_changed_files_df[commit_changed_files_df.changes_relevant_file == False].id)

    if verbose: print('    {} / {} candidates do not change a relevant file based on the extension'.format(len(irrelevant_commits_based_on_extension), len(commit_ids)))
    if return_irrelevant_commits:
        return irrelevant_commits_based_on_extension
    return [commit_id for commit_id in commit_ids if commit_id not in irrelevant_commits_based_on_extension] 