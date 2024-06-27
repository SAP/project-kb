import os
import json

directory = "data_sources/reports/"

# Now analyse the reports
for filename in os.listdir(directory):
    filepath = directory + filename
    with open(filepath, "r") as f:
        data = json.load(f)

    if not data:
        print("Error occured, JSON file could not be found.")

    results = {
        "relevance": [],
        "no_llm_rule_match": [],
    }

    print(data["commits"][0])

    for commit in data["commits"]:
        results["relevance"].append(
            {
                commit["commit_id"]: sum(
                    [rule["relevance"] for rule in commit["matched_rules"]]
                )
            }
        )
        if commit["matched_rules"]:
            print(commit["matched_rules"][0]["relevance"])
