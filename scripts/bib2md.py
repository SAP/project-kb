# Install the library before, with the following command:
# pip install bibtexparser --pre

# to run on the CLI:
# python bib2md.py your_referenceFile.bib 
# default order: desc. 
# To change add at the end of your command: -ord "asc"

import bibtexparser
import sys
import argparse
import html

def process_entry(entry):
    try:
        authors = entry['author'].split(' and ')
        if len(authors) > 1:
            authors[-1] = 'and ' + authors[-1]

        authors_formatted = ', '.join([a.replace('\n', ' ').strip() for a in authors])
        title = html.unescape(entry['title'])  
        year = int(entry['year'])
        venue = entry.get('journal') or entry.get('booktitle') or entry.get('archivePrefix')

        if not venue:
            id_unprocessed = "[" + entry.key + " - " + entry.entry_type + "]"
            return None, id_unprocessed
            
        return (year, f"{authors_formatted}. {title}. {venue.value}. ({year})."), None

    except KeyError as e:
        print(f"One or more necessary fields {str(e)} not present in this BibTeX entry.")
        return None, None

def format_simple(entry_str, order='desc'):
    library = bibtexparser.parse_string(entry_str)
    formatted_entries = []
    unprocessed_entries = []
    
    for entry in library.entries:
        processed_entry, unprocessed_entry = process_entry(entry)
        if processed_entry:
            formatted_entries.append(processed_entry)
        elif unprocessed_entry:
            unprocessed_entries.append(unprocessed_entry)

    if order == 'asc':
        formatted_entries.sort(key=lambda x: x[0])
    elif order == 'desc':
        formatted_entries.sort(key=lambda x: x[0], reverse=True)
        
    if len(unprocessed_entries) > 0:
        print('Warning: Some entries were not processed due to unknown type', file=sys.stderr)
        print("List of unprocessed entrie(s):", unprocessed_entries)
            
    return [entry[1] for entry in formatted_entries]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, help='a .bib file as argument')
    parser.add_argument('-ord', '--order', type=str, 
                        choices=['asc', 'desc'],
                        help='here we set a sort order. We have the choice between "asc" and "desc"',
                        default='desc', required=False)
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as bibtex_file:
        bibtex_str = bibtex_file.read()

    citations = format_simple(bibtex_str, args.order)
    for cit in citations:
        print()
        print(cit)

if __name__ == "__main__":
    main()

# bibtex_str = """
# @comment{
#     This is my example comment.
# }

# @ARTICLE{Cesar2013,
#   author = {Jean César},
#   title = {An amazing title},
#   year = {2013},
#   volume = {12},
#   pages = {12--23},
#   journal = {Nice Journal}
# }

# @article{CitekeyArticle,
#   author   = "P. J. Cohen",
#   title    = "The independence of the continuum hypothesis",
#   journal  = "Proceedings of the National Academy of Sciences",
#   year     = 1963,
#   volume   = "50",
#   number   = "6",
#   pages    = "1143--1148",
# }

# @misc{sharma2022surveymachinelearningtechniques,
#   title={A Survey on Machine Learning Techniques for Source Code Analysis},
#   author={Tushar Sharma and Maria Kechagia and Stefanos Georgiou and Rohit Tiwari and Indira Vats and Hadi Moazen and Federica Sarro},
#   year={2022},
#   eprint={2110.09610},
#   archivePrefix={arXiv},
#   primaryClass={cs.SE},
#   url={https://arxiv.org/abs/2110.09610},
# }

# @inproceedings{10.1145/3593434.3593481,
# author = {Reis, Sofia and Abreu, Rui and Pasareanu, Corina},
# title = {Are security commit messages informative? Not enough!},
# year = {2023},
# isbn = {9798400700446},
# publisher = {Association for Computing Machinery},
# address = {New York, NY, USA},
# url = {https://doi.org/10.1145/3593434.3593481},
# doi = {10.1145/3593434.3593481},
# abstract = {The fast distribution and deployment of security patches are important to protect users against cyberattacks...},
# booktitle = {Proceedings of the 27th International Conference on Evaluation and Assessment in Software Engineering},
# pages = {196–199},
# numpages = {4},
# keywords = {Security, Patch Management Process, Convention, Commit Messages, Best Practices},
# location = {Oulu, Finland},
# series = {EASE '23}
# }

# @inproceedings{lee-chieu-2021-co,
#     title = "Co-training for Commit Classification",
#     author = "Lee, Jian Yi David  and
#       Chieu, Hai Leong",
#     editor = "Xu, Wei  and
#       Ritter, Alan  and
#       Baldwin, Tim  and
#       Rahimi, Afshin",
#     booktitle = "Proceedings of the Seventh Workshop on Noisy User-generated Text (W-NUT 2021)",
#     month = nov,
#     year = "2021",
#     address = "Online",
#     publisher = "Association for Computational Linguistics",
#     url = "https://aclanthology.org/2021.wnut-1.43",
#     doi = "10.18653/v1/2021.wnut-1.43",
#     pages = "389--395",
#     abstract = "Commits in version control systems (e.g. Git) track changes in a software project. Commits comprise noisy user-generated natural language and code patches. Automatic commit classification (CC) has been used to determine the type of code maintenance activities performed, as well as to detect bug fixes in code repositories. Much prior work occurs in the fully-supervised setting {--} a setting that can be a stretch in resource-scarce situations presenting difficulties in labeling commits. In this paper, we apply co-training, a semi-supervised learning method, to take advantage of the two views available {--} the commit message (natural language) and the code changes (programming language) {--} to improve commit classification.",
# }

# @misc{ponta2021usedbloatedvulnerablereducing,
#       title={The Used, the Bloated, and the Vulnerable: Reducing the Attack Surface of an Industrial Application},
#       author={Serena Elisa Ponta and Wolfram Fischer and Henrik Plate and Antonino Sabetta},
#       year={2021},
#       eprint={2108.05115},
#       archivePrefix={arXiv},
#       primaryClass={cs.SE},
#       url={https://arxiv.org/abs/2108.05115},
# }

# @misc{aladics2023astbasedcodechangerepresentation,
#       title={An AST-based Code Change Representation and its Performance in Just-in-time Vulnerability Prediction},
#       author={Tamás Aladics and Péter Hegedűs and Rudolf Ferenc},
#       year={2023},
#       eprint={2303.16591},
#       archivePrefix={arXiv},
#       primaryClass={cs.SE},
#       url={https://arxiv.org/abs/2303.16591},
# }

