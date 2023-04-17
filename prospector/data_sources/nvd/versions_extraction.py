import json
import re

import requests
import spacy

# TODO: Modify the list of keywords
VULN = ["version", "through", "versions"]

FIXED = [
    "before",
    "before release",
    "before version",
    "prior to",
    "upgrade to",
    "fixed in",
    "fixed in version",
    "fixed in release",
    "to version",
]


def extract_version_ranges_cpe(json_data):
    # json_data = json.loads(json_data)
    version_ranges = []
    if "configurations" in json_data:
        for configuration in json_data["configurations"]:
            for node in configuration["nodes"]:
                for cpe_match in node["cpeMatch"]:
                    if "versionStartIncluding" in cpe_match:
                        version_range = "[" + cpe_match["versionStartIncluding"] + ":"
                    elif "versionStartExcluding" in cpe_match:
                        version_range = "(" + cpe_match["versionStartExcluding"] + ":"
                    elif "criteria" in cpe_match:
                        if re.match(
                            r"\d+\.(?:\d+\.*)*\d", cpe_match["criteria"].split(":")[5]
                        ):
                            version_range = (
                                "[" + cpe_match["criteria"].split(":")[5] + ":"
                            )
                        else:
                            version_range = "None:"
                    else:
                        version_range = "(None:"

                    if "versionEndIncluding" in cpe_match:
                        version_range += cpe_match["versionEndIncluding"] + "]"
                    elif "versionEndExcluding" in cpe_match:
                        version_range += cpe_match["versionEndExcluding"] + ")"
                    else:
                        version_range += "None)"

                    version_ranges.append(version_range)
    return version_ranges


def process_ranges(ranges_list):
    if ranges_list:
        last_entry = ranges_list[-1]
        version_range = last_entry.strip("[]()")
    else:
        version_range = "None:None"
    return version_range


def is_real_version(text: str):
    return bool(re.match(r"\d+\.(?:\d+\.*)*\d", text))
    # return bool(re.match(r"^(v\d+(?:\.\d+)*\.?|\d+(?:\.\d+)*\.?)$", text))


# old method
def extract_version_ranges_desc(doc):
    # relevant_sentences = {}
    # relevant_sentence = ""
    fixed_version = ""
    vulnerable_version = ""
    for i in range(len(doc))[1:]:
        if is_real_version(doc[i].text):
            if doc[i - 1].text in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (doc[i - 2].text + " " + doc[i - 1].text) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (
                doc[i - 3].text + " " + doc[i - 2].text + " " + doc[i - 1].text
            ) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            else:
                # relevant_sentence = doc[: i + 1]
                vulnerable_version = doc[i].text

    # vulnerable_version = re.sub(r"^v\.?", "", vulnerable_version)
    # fixed_version = re.sub(r"^v\.?", "", fixed_version)
    return vulnerable_version, fixed_version


# New method. Need validation
def extract_version_ranges_description(doc):
    fixed_version = None
    affected_version = None
    for sent in doc.sents:
        versions = re.findall(r"\d+\.(?:\d+\.*)*\d", sent.text)
        if versions:
            for version in versions:
                min_dist_fixed = float("inf")
                min_dist_vuln = float("inf")
                for keyword in FIXED:
                    if keyword in sent.text:
                        keyword_index = sent.start + sent.text.index(keyword)
                        version_index = sent.start + sent.text.index(version)
                        dist = abs(keyword_index - version_index)
                        if dist < min_dist_fixed:
                            min_dist_fixed = dist
                            fixed_version = version
                # Check for vulnerable version keywords
                for keyword in VULN:
                    if keyword in sent.text:
                        keyword_index = sent.start + sent.text.index(keyword)
                        version_index = sent.start + sent.text.index(version)
                        dist = abs(keyword_index - version_index)
                        if dist < min_dist_vuln:
                            min_dist_vuln = dist
                            affected_version = version

    return affected_version, fixed_version
