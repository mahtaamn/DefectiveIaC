import pandas as pd
import requests
from dateutil import parser
import time
repo={};
repo['name'] = 1
page=3
commitCountPerRepo=0;

headers = {
    'Authorization': 'token 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'
}

orgName = "wikimedia"
df = pd.read_csv(f"{orgName}_repository.csv")
#filter repos based on 11% pp condition;
dfData = df['isCriteria2Met'] == 1
filteredRepos = df[dfData]
# make sure indexes pair with number of rows
filteredData = filteredRepos.reset_index()


headers = {
    'Authorization': 'token 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'
}


url = f"https://api.github.com/repos/{orgName}/{repo['name']}/issues?per_page=100&page={page}"
dataIssueList = requests.get(url, headers=headers).json()

# if the repository has commits
if len(dataIssueList) > 0:
    for j, commit in enumerate(dataIssueList):
        print("j=>", j);
        commitCountPerRepo += 1
        #time.sleep(3);