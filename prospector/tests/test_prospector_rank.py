# Test cases for Prospectors mapping functions in August 2020
#   created by Daan Hommersom and Antonino Sabetta at SAP
#
# For every function in prospector/map.py two test cases are created:
#  - The first one tests cases that should succeed
#  - The second one tests the cases for which an exception should be raised

import pytest
import os 
import sys
import json
import random
import spacy
nlp = spacy.load('en_core_web_sm')

current_working_directory = os.getcwd()

os.chdir('../../prospector')
sys.path.insert(1, '../prospector')

import rank

os.chdir(current_working_directory)

##################################
###
### FIXTURES
###
##################################

@pytest.fixture()
def example_commit_content():
    example_commit_content = {
        'message': ["Add #795 to changelog as it's now merged"],
        'diff': ['diff --git a/CHANGELOG.md b/CHANGELOG.md', 'index 507498f..66834c6 100644', '--- a/CHANGELOG.md', '+++ b/CHANGELOG.md', '@@ -11,2 +11,3 @@ A pre-release can be downloaded from https://ci.jenkins.io/job/Plugins/job/docke', ' * Update terminology and reference non-deprecated image names [#802](https://github.com/jenkinsci/docker-plugin/issues/802), [#811](https://github.com/jenkinsci/docker-plugin/issues/811)', '+* Enhancement: templates can now specify cpu period and cpu quota [#795](https://github.com/jenkinsci/docker-plugin/issues/795)']
    }
    return example_commit_content

##################################
###
### FILTERING TEXT
###
##################################

#
# CamelCase split 
#


@pytest.mark.text_preprocessing
@pytest.mark.parametrize('token, result', [
    ('ExampleCamelCase', ['ExampleCamelCase', 'example', 'camel', 'case']),
    ('exampleCamelcase', ['exampleCamelcase', 'example', 'camelcase']),
    ('shouldreturnnone', None)   
])
def test_camel_case_split(token, result):
    assert result == rank.camel_case_split(token)

@pytest.mark.exception_handling
@pytest.mark.parametrize('token, error', [
    (['CamelCaseToken.'], TypeError)
])
def test_camel_case_split_errors(token, error):
    with pytest.raises(error):
        rank.camel_case_split(token)


#
# snake_case split 
#
@pytest.mark.text_preprocessing
@pytest.mark.parametrize('token, result', [
    ('example_snake_case', ['example_snake_case', 'example', 'snake', 'case']),
    ('shouldreturnnone', None)   
])
def test_snake_case_split(token, result):
    assert result == rank.snake_case_split(token)

@pytest.mark.exception_handling
@pytest.mark.parametrize('token, error', [
    (['snake_case_token'], TypeError)
])
def test_snake_case_split_errors(token, error):
    with pytest.raises(error):
        rank.snake_case_split(token)

#
# text_into_chunks
#

@pytest.mark.text_preprocessing
@pytest.mark.parametrize('text, chunk_size', [
    ('Just an example string, which should remain one sentence', 1000),
    ('Just an example string, which should not remain one sentence', 10),
])
def test_text_into_chunks(text, chunk_size):
    chunks = rank.text_into_chunks(text, chunk_size)
    for chunk in chunks:
        assert len(chunk) <= chunk_size
    assert ''.join(chunks) == text
    
@pytest.mark.text_preprocessing
def test_text_into_chunks_with_commit(example_commit_content):
    '''
    The function should be able to handle real commit content, where the message and diff are provided as list
    '''
    # larger text than the chunk size specified
    chunks = rank.text_into_chunks(text=example_commit_content['diff'], chunk_size=100)
    for chunk in chunks:
        assert len(chunk) <= 100
    assert len(chunks) == 6
    assert ''.join(chunks) == ' '.join(example_commit_content['diff'])
    
    # smaller text than the chunk size specified
    chunks = rank.text_into_chunks(text=example_commit_content['message'], chunk_size=100)
    assert len(chunks) == 1
    assert len(chunks[0]) == 40

@pytest.mark.exception_handling
@pytest.mark.parametrize('text, error', [
    (['Check what happens', 12345, 'When there are integers in the list'], TypeError),
])
def test_text_into_chunks_errors(text, error):
    with pytest.raises(error):
        rank.text_into_chunks(text)

#
# filter_text
#

@pytest.mark.text_preprocessing
def test_filter_text_2():
    text = 'This is an example sentence to test the functionalities of filtered_text'
    assert rank.filter_text(text) == 'example sentence test functionality filtered_text filter text'
    assert type(rank.filter_text(text, as_tokens=True)[0]) == spacy.tokens.token.Token
    assert rank.filter_text(text, as_list=True) == ['example', 'sentence', 'test', 'functionality', 'filtered_text', 'filter', 'text']

@pytest.mark.text_preprocessing
@pytest.mark.parametrize('text, remove_duplicates, case_sensitive, lemmatize, result', [
    ('This is an example.', True, False, True, 'example'),
    ('This is an example: Example.', False, True, False, 'example Example'),
    ('This is an example. In this example, example occurs more than once.', True, False, True, 'example occur'),
    ('This is an example. In this example, example occurs more than once.', False, False, True, 'example example example occur'),
    (['This is an example.', 'In this example, example occurs more than once.'], False, False, True, 'example example example occur'),
])
def test_filter_text(text, remove_duplicates, case_sensitive, lemmatize, result):
    assert result == rank.filter_text(text, as_tokens=False, as_list=False, remove_duplicates=remove_duplicates, case_sensitive=case_sensitive, lemmatize=lemmatize)

#
# filter_doc
#

@pytest.mark.text_preprocessing
def test_filter_doc(example_commit_content):
    '''
    The function should be able to handle real commit content, where the message and diff are provided as list
    '''
    text = ' '.join(example_commit_content['message'])
    doc = nlp(text)
    assert rank.filter_doc(doc=doc) == 'add changelog merge'

@pytest.mark.exception_handling
def test_filter_doc_errors(example_commit_content):
    '''
    The doc provided should be a spacy.tokens.doc.Doc
    '''
    with pytest.raises(TypeError):
        rank.text_into_chunks(doc=example_commit_content['message'])

#
# simpler_filter_text
#

@pytest.mark.text_preprocessing
def test_simpler_filter_text(example_commit_content):
    '''
    The function should be able to handle real commit content, where the message and diff are provided as list
    '''
    assert rank.simpler_filter_text(text=example_commit_content['message']) == 'add changelog merge'
    assert rank.simpler_filter_text(text=' '.join(example_commit_content['message'])) == 'add changelog merge'
    assert rank.simpler_filter_text(text='This is an example sentence to test the functionalities of filtered_text') == 'example sentence test functionality filtered_text filter text'

#
# extract_relevant_lines_from_commit_diff
#
@pytest.mark.text_preprocessing
def test_extract_relevant_lines_from_commit_diff(example_commit_content):
    assert len(rank.extract_relevant_lines_from_commit_diff(git_diff=example_commit_content['diff'], max_lines=10000)) == 2
    assert len(rank.extract_relevant_lines_from_commit_diff(git_diff=example_commit_content['diff'], max_lines=1)) == 1
    assert rank.extract_relevant_lines_from_commit_diff(git_diff=example_commit_content['diff'])[1] == '+* Enhancement: templates can now specify cpu period and cpu quota [#795](https://github.com/jenkinsci/docker-plugin/issues/795)'

@pytest.mark.exception_handling
def test_extract_relevant_lines_from_commit_errors(example_commit_content):
    '''
    The doc provided should be a spacy.tokens.doc.Doc
    '''
    with pytest.raises(TypeError):
        rank.extract_relevant_lines_from_commit_diff(git_diff=' '.join(example_commit_content['diff']))

#
# extract_n_most_occurring_words
#

@pytest.mark.text_preprocessing
def test_extract_n_most_occurring_words(example_commit_content):
    assert rank.extract_n_most_occurring_words(rank.simpler_filter_text('Messages contain fix indicating words like fixing, fix or fixes, can also contain a lot of different words. And we do not want a lot of stopwords! From this description, fix should be the returned word and and and not not not a stopword.'), n=1) == 'fix'
    assert rank.extract_n_most_occurring_words(rank.simpler_filter_text(example_commit_content['message']), n=1) == 'add'
    assert rank.extract_n_most_occurring_words(rank.simpler_filter_text(' '.join(example_commit_content['message'])), n=1) == 'add'

@pytest.mark.exception_handling
@pytest.mark.parametrize('text, error', [
    (['Check what happens', 12345, 'When there are integers in the list'], TypeError),
])
def test_extract_n_most_occurring_words(text, error):
    with pytest.raises(error):
        rank.extract_n_most_occurring_words(text)

#
# find_references
#

@pytest.mark.text_preprocessing
def test_find_references(example_commit_content):
    assert len(rank.find_references('No reference here!')) == 0
    assert type(rank.find_references(example_commit_content['message'])) == list
    assert rank.find_references(example_commit_content['message']) == ['#795']
    assert len(rank.find_references(example_commit_content['diff'])) == 7
    assert 'https://github.com/jenkinsci/docker-plugin/issues/802' in rank.find_references(example_commit_content['diff'])

# @pytest.mark.text_preprocessing
# def test_remove_project_name():
#     project_name = 'jpcertcc LogonTracer logon tracer'
#     description = 'LogonTracer logon tracer early allow remote attacker conduct xml external entity xxe attack unspecified vector'
#     assert rank.remove_project_name_from_string(project_name, description) == 'early allow remote attacker conduct xml external entity xxe attack unspecified vector'

##################################
###
### RANKING
###
##################################

# @pytest.mark.ranking