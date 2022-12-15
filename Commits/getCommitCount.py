import requests
from urllib.parse import parse_qs, urlparse
from dateutil import parser
import pandas as pd
import time

def get_commits_count( owner_name: str, repo_name: str,headers) -> int:
    """
    Returns the number of commits to a GitHub repository.
    """
    url = f"https://api.github.com/repos/{owner_name}/{repo_name}/commits?per_page=1"
    dataLastCommit = requests.get(url, headers=headers)
    #print(url)
    #print(dataLastCommit.json())

    commits_count = 0
    first_commit_date = 0
    last_commit_date = 0
    numOfMonths = 0
    is_repo_valid = False

    links = dataLastCommit.links
    print (links)
    rel_last_link_url = urlparse(links["last"]["url"])
    rel_last_link_url_args = parse_qs(rel_last_link_url.query)
    rel_last_link_url_page_arg = rel_last_link_url_args["page"][0]
    commits_count = int(rel_last_link_url_page_arg)
    print("commitCount:",commits_count)

    if commits_count == 0:
        print("no commits at all")
        commits_count = 0
    else:
        try:
            last_commit_date = parser.parse(dataLastCommit.json()[0]['commit']['committer']['date'])
            try:
                dataFirstCommit = requests.get(links["last"]["url"], headers=headers).json()
                first_commit_date = parser.parse(dataFirstCommit[0]['commit']['committer']['date'])

                numOfMonths = (last_commit_date.year - first_commit_date.year) * 12 + (
                            last_commit_date.month - first_commit_date.month) + 1
                print("first commti date:",first_commit_date,"last commit date:",last_commit_date,
                      "number of months in between:",numOfMonths , "commit count:",commits_count)
                #print(int(commits_count)/int(numOfMonths))
                if(int(commits_count)/int(numOfMonths)) >=2:
                    #print("yeeeeeees")
                    is_repo_valid = True
                #else:
                    #print("nnnnnnnnnnn")
            except:
                print("*** no first commit date")
                commits_count = 0
        except:
            print("^^^^^^ No last date.")
            commits_count = 0


    return first_commit_date, last_commit_date,commits_count, numOfMonths,is_repo_valid


orgName = "wikimedia"
df = pd.read_csv(f"{orgName}_repository.csv")
#filter repos based on 11% pp condition;
dfData = df['isCriteria2Met'] == 1
filteredRepos = df[dfData]
print("number of repositories with at least 11% pp files:", len(filteredRepos))
# make sure indexes pair with number of rows
filteredData = filteredRepos.reset_index()

headers = {
    'Authorization': 'token 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'
}

repoList = []
for index, repo in filteredData.iterrows():
    print("next repository name:", repo['name'],"index=====>:",index)
    first_commit_date, last_commit_date, commits_count, numOfMonths, is_repo_valid = get_commits_count(orgName, repo['name'],headers)
    time.sleep(5)

    iacFile = {"repo_name": repo['name'], "first_commit_date": first_commit_date,
               "last_commit_date": last_commit_date, "commits_count": commits_count,
               "numOfMonths": numOfMonths, "is_repo_valid": is_repo_valid}
    repoList.append(iacFile)

    #print(num)

dfFile = pd.DataFrame(repoList)
dfFile.to_csv(f"{orgName}_avg_repos.csv")

dfData = dfFile['is_repo_valid'] == True
print("number of repositories with criteria 3", len(dfData))

