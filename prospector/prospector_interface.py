# For SessionState obtained from https://gist.github.com/okld/0aba4869ba6fdc8d49132e6974e2e662
import streamlit as st
from streamlit.hashing import _CodeHasher

try:
    # Before Streamlit 0.65
    from streamlit.ReportThread import get_report_ctx
    from streamlit.server.Server import Server
except ModuleNotFoundError:
    # After Streamlit 0.65
    from streamlit.report_thread import get_report_ctx
    from streamlit.server.server import Server

# For Prospector
import pandas as pd
import numpy as np
import re, os, json, sqlite3, requests, time, datetime, ast, random, copy, sys, base64
from datetime import datetime, timedelta
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import spacy
nlp = spacy.load('en_core_web_sm')

current_working_directory = os.getcwd()
os.chdir('git_explorer')
sys.path.append(os.getcwd())

os.environ['GIT_CACHE'] = current_working_directory + '/git_explorer/git_explorer_cache'
GIT_CACHE = os.environ['GIT_CACHE']
from core import do_clone, Git, Commit, clone_repo_multiple, utils

os.chdir(current_working_directory)

import database
import filter
import rank
import main as prospector_main

### Magic Numbers
# MODELS
min_max_scaler_path = "models/Prospector-universal_columns_scaler.joblib"
model_path = "models/Prospector-LR.joblib"

# COLUMNS
vulnerability_specific_columns = ['message_score', 'changed_files_score', 'git_diff_score', 'message_score_reference_content','changed_files_score_code_tokens']
universal_columns = ['n_hunks', 'avg_hunk_size', 'n_changed_files', 'vulnerability_timestamp']
columns_to_drop = ['path_similarity_score', 'git_diff_score_code_tokens', 'message_score_code_tokens', 'changed_files_score_reference_content', 'git_diff_score_reference_content']

# DATABASE
vulnerabilities_db_path = 'data/prospector-vulnerabilities.db'
commits_db_path = 'data/prospector-commits.db'
# when testing # example vulnerability: CVE-2018-16166
# vulnerabilities_db_path = 'tests/test-vulnerabilities.db'
# commits_db_path = 'tests/test-commits.db'

# functionality
def main():
    state = _get_state()

    try:
        if state.vulnerabilities_df == None:
            state.vulnerabilities_df, state.db_references_df, state.advisory_references_df, state.tags_df, state.repository_url_df, state.fixes_df = load_vulnerabilities()
    except:
        pass

    pages = {
        "Dashboard": dashboard_page,
        "Inspect": inspect_page,
    }

    st.sidebar.title("Page navigation")
    page = st.sidebar.radio("Select your page", ("Dashboard", "Inspect"), index=0)

    # Display the selected page with the session state
    pages[page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


# load the data
# @st.cache(allow_output_mutation=True)
def load_vulnerabilities():
    prospector_connection, prospector_cursor = database.connect_with_database(commits_db_path)
    vulnerabilities_connection, vulnerabilities_cursor = database.connect_with_vulnerabilities_database(vulnerabilities_db_path)
    
    print("Reading vulnerabilities")
    vulnerabilities_df = pd.read_sql("SELECT * FROM vulnerabilities", vulnerabilities_connection).set_index("vulnerability_id")
    db_references_df = pd.read_sql("SELECT vulnerability_id, url, preprocessed_content FROM vulnerability_references", vulnerabilities_connection)
    advisory_references_df = pd.read_sql("SELECT vulnerability_id, url FROM advisory_references", vulnerabilities_connection)
    fixes_df = pd.read_sql("SELECT * FROM fix_commits", vulnerabilities_connection)

    # prospector_connection, prospector_cursor = database.connect_with_database(commits_db_path)
    tags_df = pd.read_sql("SELECT * FROM tags", prospector_connection)

    # Create repository_url_df
    repository_url_df = pd.DataFrame()
    for i, repo_url in enumerate(list(vulnerabilities_df.repo_url.unique())):
        repository_url_df.at[i, 'repo_url'] = repo_url
        repository_url_df.at[i, 'project_name'] = rank.simpler_filter_text(re.sub('^https?://|[^\w]', ' ', repo_url)).lower()
    repository_url_df['project_name'] = repository_url_df.apply(lambda x: ' '.join([token for token in x['project_name'].split(' ') if token not in ['github', 'com', 'git', 'org']]), axis=1)

    return vulnerabilities_df, db_references_df, advisory_references_df, tags_df, repository_url_df, fixes_df

# @st.cache
def map_description_to_repository_url(vulnerability_id, description, vulnerabilities_df, repository_url_df):
    # if the vulnerabilities df is empty
    if type(vulnerabilities_df) == type(None):
        return 

    if vulnerability_id in list(vulnerabilities_df.index):
        return vulnerabilities_df.at[vulnerability_id, 'repo_url']

    # else return url with highest lexical similarity
    repo_urls = list(repository_url_df.repo_url)
    project_names = list(repository_url_df.project_name)

    preprocessed_description = rank.simpler_filter_text([re.sub('[^\w]', ' ', token.text) for token in nlp(description)]).lower()
    tfidf_vectorized_strings = TfidfVectorizer().fit_transform([preprocessed_description] + project_names)

    scores = {repo_url : cosine_similarity(tfidf_vectorized_strings[0], tfidf_vectorized_strings[i+1])[0][0] for i, repo_url in enumerate(repo_urls) }
    return list({k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}.keys())[0]

# @st.cache
def load_model():
    return load(model_path), load(min_max_scaler_path)

# @st.cache(allow_output_mutation=True)
# @st.cache(hash_funcs={sqlite3.Cursor: id}, allow_output_mutation=True)
# @st.cache
def gather_tags(repo_url, tags_df):
    # clean repo_url entry
    clean_repo_url = re.sub('\.git$|/$', '', repo_url)

    tags = list(tags_df[tags_df.repo_url == clean_repo_url].tag)
    if len(tags) != 0:
        return tags
    else: # the tags have not been added to the df
        prospector_connection, prospector_cursor = connect_with_commits_database(commits_db_path)
        database.add_tags_to_database(prospector_connection, tags=None, git_repo=None, repo_url=repo_url, verbose=True)

# @st.cache
def get_vulnerability_data(vulnerability_id, vulnerabilities_df, db_references_df):
    if type(vulnerabilities_df) != type(None) and vulnerability_id in list(vulnerabilities_df.index):
        repo_url, cve_description, cve_published_timestamp, preprocessed_description = vulnerabilities_df.loc[vulnerability_id]
        # cve_project_name = ' '.join(re.split('/|-|\.', cve_repo_url.lstrip('https?://')))
        references = list(db_references_df[db_references_df.vulnerability_id == vulnerability_id].url)
    else:
        cve_description, cve_published_timestamp, references = database.extract_nvd_content(vulnerability_id)
        references = []
        preprocessed_description = rank.simpler_filter_text(cve_description)
    return cve_description, cve_published_timestamp, preprocessed_description, references

# @st.cache(allow_output_mutation=True)
def connect_with_commits_database(path):
    return database.connect_with_database(path)

def dashboard_page(state):

    st.title("PROSPECTOR")

    st.subheader("The search engine for fix-commits for security vulnerabilities in OSS")
    st.write('By SAP - Antonino SABETTA & Daan HOMMERSOM')
    st.write('''
        How to use Prospector:
        \n1) Provide a vulnerability description, (GitHub) repository URL and a release date (or pick a CVE).
        \n2) Check whether Prospector fills in the rest correctly, and provide additional information if needed.
        \n3) Find security fixes!
    ''')

    # with st.beta_expander(label="Find out more", expanded=False):
    st.write('''
        The objective of Prospector is to minimize the (manual) effort needed for finding 
        the fix commit of a known vulnerability in an open-source software project. 
        Since these repositories can contain hundreds thousands commits, the commits are 
        firstly filtered by only selecting all commits within two years before and 
        one hundred days after the release date with a maximum of respectively 5215 and 100 commits. 
        A study has shown that this selection has 93% recall.
        \n
        Firstly, an advisory record is created containing information on the vulnerability.
        This advisory record is used to select candidate commits. For these candidate commits, 
        ranking vectors are computed. These ranking vectors consist of several components that
        can be used to predict whether a candidate commit is the fix commit we are looking for.
        These candidates are then ranked on this probability score. 
        
        In 77.68% of the cases, the fix is in the top 5. In 84.03% in the top 10,
        and in 88.59% in the top 20.
    ''')

    st.subheader("ADVISORY RECORD")
    state.vulnerability_id = st.text_input("Vulnerability identifyer:", value=state.vulnerability_id if state.vulnerability_id else '').upper()

    if state.vulnerability_id:
        try:
            cve_description, cve_published_timestamp, preprocessed_description, references = get_vulnerability_data(state.vulnerability_id, state.vulnerabilities_df, state.db_references_df)
        except:
            references = st.text_input("Please provide useful references (separated by commas)")
            references = references.split(',')
            cve_description, cve_published_timestamp, preprocessed_description = '', time.time(), None
    else:
        cve_description, cve_published_timestamp, preprocessed_description, references = '', time.time(), None, []

    vulnerability_description = st.text_area("Vulnerability description", value=cve_description)
    project_name = st.text_input("Project name", value=' '.join([token.text for token in nlp(vulnerability_description) if token.tag_ == 'NNP']))
    repo_url = st.text_input("Repository URL", value=map_description_to_repository_url(vulnerability_id=state.vulnerability_id, description=project_name, vulnerabilities_df=state.vulnerabilities_df, repository_url_df=state.repository_url_df) if project_name != '' else '')
    published_date = st.date_input("Vulnerability published date", value=datetime.fromtimestamp(int(cve_published_timestamp)))
    published_timestamp = int(time.mktime(published_date.timetuple()))
    
    state.advisory_record_confirmed = st.button("CONFIRM ADVISORY RECORD") if not state.advisory_record_confirmed else True
    if state.advisory_record_confirmed:

        # option to clear the state
        if st.button("CLEAR FIELDS"):
            state.clear()

        # if it was a new vulnerability, add it to the DB
        if type(state.vulnerabilities_df) == type(None) or state.vulnerability_id not in list(state.vulnerabilities_df.index):
            vulnerabilities_connection, vulnerabilities_cursor = database.connect_with_vulnerabilities_database(vulnerabilities_db_path)
            database.add_vulnerability_to_database(vulnerabilities_connection, state.vulnerability_id, repo_url, vulnerability_description, published_timestamp)
            
            # if it was not an NVD CVE, or the extraction failed
            if len(references) == 0:
                try:
                    cve_description, cve_published_timestamp, references = database.extract_nvd_content(state.vulnerability_id)
                    references = [reference for reference in references]
                except:
                    references = st.text_input("Please provide useful references (separated by commas)")
                    references = references.split(',')
            
            database.add_vulnerability_references_to_database(vulnerabilities_connection, state.vulnerability_id, references, driver=None)
            prospector_connection, prospector_cursor = connect_with_commits_database(commits_db_path)
            database.add_tags_to_database(prospector_connection, tags=None, git_repo=None, repo_url=repo_url, verbose=True)
            state.vulnerabilities_df, state.db_references_df, state.advisory_references_df, state.tags_df, state.repository_url_df, state.fixes_df = load_vulnerabilities()

        # gather values
        repository_tags = gather_tags(repo_url, state.tags_df)
        versions_in_description = filter.retreive_all_versions_from_description(vulnerability_description)
        tags_in_description = list(dict.fromkeys([tag for version in versions_in_description for tag in filter.get_tag_for_version(repository_tags, version)]))
        references = [state.db_references_df.at[index, 'url'] for index in state.db_references_df[state.db_references_df.vulnerability_id == state.vulnerability_id].index]
    
        advisory_references = list(state.advisory_references_df[state.advisory_references_df.vulnerability_id == state.vulnerability_id].url)

        # allow the user to influence the filtering
        state.advanced_settings = st.checkbox("Show advanced settings", state.advanced_settings)
        if state.advanced_settings:

            # the adding of references can be gone wrong
            first_commit_timestamp = rank.get_first_commit_timestamp(repo_url) #@TODO: add a column to the database containing this value
            first_commit_date, today = datetime.fromtimestamp(int(first_commit_timestamp)).date(), datetime.fromtimestamp(int(time.time())).date()
            lower_bound = published_date - timedelta(days=730) if published_date - timedelta(days=730) > first_commit_date else first_commit_date
            upper_bound = published_date + timedelta(days=100) if published_date + timedelta(days=100) < today else today
            
            since, until = st.slider("Published date based interval", min_value = first_commit_date, max_value = today, value=(lower_bound, upper_bound))
            since, until = int(time.mktime(since.timetuple())), int(time.mktime(until.timetuple()))

            # references
            additional_references = st.text_input("Additional references (separated by commas)")
            if additional_references:
                references += additional_references.split(',')
                vulnerabilities_connection, vulnerabilities_cursor = database.connect_with_vulnerabilities_database(vulnerabilities_db_path)
                database.add_vulnerability_references_to_database(vulnerabilities_connection, state.vulnerability_id, references, driver=None)

            selected_references = st.multiselect('Advisory references', tuple(references), default=tuple(references))

            # affected versions
            relevant_tags = st.multiselect('Relevant tags', tuple(repository_tags), default=tuple(tags_in_description) if len(tags_in_description) != 0 else None)
            # st input int k
            k = st.number_input("The number of results to show", min_value=1, max_value=50, value=10, step=1)
        else:
            selected_references = references
            relevant_tags = tags_in_description
            since, until = None, None
            k = 10

        # st.write('vulnerability_description:', vulnerability_description)
        # st.write('references_content:', references_content)
        # st.write('vulnerability_id:', state.vulnerability_id)
        # st.write('since - published_timestamp - until:', since, published_timestamp, until)
        # st.write('repo_url:', repo_url)
        # # st.write('references:', references)
        # # st.write('advisory_references:', advisory_references)
        # st.write('relevant_tags:', relevant_tags)

        if st.button("Search prospects!"):
            model, min_max_scaler = load_model()
            prospector_connection, prospector_cursor = connect_with_commits_database(commits_db_path)

            preprocessed_description = rank.simpler_filter_text(vulnerability_description)

            references_content = tuple(state.db_references_df[(state.db_references_df.vulnerability_id == state.vulnerability_id) & (state.db_references_df.url.isin(selected_references))].preprocessed_content)
            references_content = rank.extract_n_most_occurring_words(rank.remove_forbidden_words_from_string(string=' '.join(references_content), forbidden_words = rank.reference_stopwords + project_name.split(' ')), n=20)
            
            st.write(references_content)

            advisory_record = rank.Advisory_record(state.vulnerability_id, published_timestamp, repo_url, selected_references, references_content, advisory_references, vulnerability_description, prospector_connection, preprocessed_vulnerability_description=preprocessed_description, relevant_tags=relevant_tags, verbose=True, since=since, until=until)
            
            print("\nGathering candidate commits and computing ranking vectors.")
            advisory_record.gather_candidate_commits()
            advisory_record.compute_ranking_vectors()

            # scaling some columns using the pretrained scaler, and some vulnerability specific
            advisory_record.ranking_vectors[vulnerability_specific_columns] = MinMaxScaler().fit_transform(advisory_record.ranking_vectors[vulnerability_specific_columns])
            advisory_record.ranking_vectors[universal_columns] = min_max_scaler.transform(advisory_record.ranking_vectors[universal_columns])
            advisory_record.ranking_vectors.drop(columns=columns_to_drop, inplace=True)

            advisory_record.ranked_candidate_commits = rank.rank_candidates(model, advisory_record.ranking_vectors)

            advisory_record.ranking_vectors.set_index('commit_id', inplace=True)
            output = prospector_main.advisory_record_to_output(advisory_record, model, prospector_cursor, k=k)
            tmp_download_link = download_link(output, 'Prospector_results-{}.txt'.format(state.vulnerability_id), "Click here to download Prospector's results as a txt file!")
            
            st.header("Results")

            st.markdown(tmp_download_link, unsafe_allow_html=True)

            st.write("Showing the top {} candidates from {} candidates considered".format(k, len(advisory_record.ranking_vectors)))
            st.write(output)

def create_advisory_record(vulnerability_id, published_timestamp, repo_url, references, advisory_references, vulnerability_description, prospector_connection, preprocessed_description, relevant_tags):
    return rank.Advisory_record(vulnerability_id, published_timestamp, repo_url, references, advisory_references, vulnerability_description, prospector_connection, preprocessed_description, relevant_tags)

def inspect_page(state):
    st.title(":wrench: Inspect")

    st.write("To see what is in the database")
    st.dataframe(state.vulnerabilities_df)

    if st.button("Select random vulnerability"):
        random_vulnerability = state.vulnerabilities_df.index[random.randint(0, len(state.vulnerabilities_df)-1)]
        st.subheader(random_vulnerability)
        st.write('Affected repository:', state.vulnerabilities_df.at[random_vulnerability, 'repo_url'])
        st.write('Vulnerability description:', state.vulnerabilities_df.at[random_vulnerability, 'description'])
        st.write('Published date:', datetime.fromtimestamp(int(state.vulnerabilities_df.at[random_vulnerability, 'published_date'])))

class _SessionState:
    '''
    Copied from:
        #https://github.com/gaurav-gunhawk/Python/blob/master/Streamlit/Streamlit-SessionStateManagement.py
    '''
    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)

def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session

def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state

def download_link(object_to_download, download_filename, download_link_text):
    """
    From: https://discuss.streamlit.io/t/heres-a-download-function-that-works-for-dataframes-and-txt/4052

    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

if __name__ == "__main__":
    main()