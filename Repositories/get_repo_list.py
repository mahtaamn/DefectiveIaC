import requests
import pandas as pd
import time

orgName = "mirantis"

def get_iac_percent(headers, repo, owner):
    url = f"https://api.github.com/search/code?q=*+repo:{owner}/{repo}"
    data = requests.get(url, headers=headers).json()

    try:
        total_count = data["total_count"]
    except:
        total_count = 0


    url = f"https://api.github.com/search/code?q=*+extension:.pp+repo:{owner}/{repo}"
    filteredData = requests.get(url, headers=headers).json()

    try:
        iac_count = filteredData["total_count"]
    except:
        iac_count = 0

    try:
        iaC_percent = iac_count / total_count
        # print("percentage",iaC_percent)
    except:
        iaC_percent = 0
    return total_count, iac_count, iaC_percent


headers = {
    'Authorization': 'token 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',
    'Content-Type': 'application/json'
}

pageCount = list(range(1, 60))
repoCount = 0
repoArr = []
totalCount = 0
for i, page in enumerate(pageCount):
    #print("page count:",i)
    print("page number:", page,",index number:",i)
    url = f"https://api.github.com/orgs/{orgName}/repos?type=all&per_page=100&page={page}&sort=created"

    data = requests.get(url, headers=headers).json()
    repoCount = repoCount + len(data)
    # print("repoCount count:",repoCount)

    if len(data) == 0:
        print("break- no more repos")
        break;


    for j, repo in enumerate(data):
        #print(data)
        totalCount += 1
        print("j:", j,"repo name:",repo["name"],",total count:", totalCount)
        item = {"name": repo["name"], "fulName": repo["full_name"], "id": repo["id"]}

        total_count, iac_count, iaC_percent = get_iac_percent(headers,item["name"],orgName)
        item["total_count"] = total_count
        item["iac_count"] = iac_count
        item["iacPercent"] = iaC_percent

        if float(iaC_percent) >= 0.11:
            item["isCriteria2Met"] = 1
        elif float(iaC_percent) < 0.11:
            item["isCriteria2Met"] = 0

        repoArr.append(item)
        time.sleep(12)
        df = pd.DataFrame(repoArr)
        # print(df)
        df.to_csv(f"{orgName}_repository.csv")
