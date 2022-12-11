import pandas as pd
import requests
from dateutil import parser


headers = {
    'Authorization': 'token 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'
}

orgName = "wikimedia"
df = pd.read_csv(f"{orgName}_repository.csv")
#filter repos based on 11% pp condition;
dfData = df['isCriteria2Met'] == 1
filteredRepos = df[dfData]
print("number of repositories with at least 11% pp files:", len(filteredRepos))
# make sure indexes pair with number of rows
filteredData = filteredRepos.reset_index()


#define variables for all of data
numOfAllRepos = 0
numOfOrgCommits = 0
validCommits = []
validRepoCommitList = []
repoCommitFileArr = {}
# for loop for each repository
for index, repo in filteredData.iterrows():
    print("next repository name:", repo['name'],"index=====>:",index)
    pageCount = list(range(1, 55))

    # if index > 6:
    #     print("break from repoooooo")
    #     break

    #reset variables per repository
    repoCommitFiles = []
    commitDateArr = {}
    firstCommitDate = None
    lastCommitDate = None
    ppCommitCountPerRepo = 0
    commitCountPerRepo = 0
    # for loop to get all commits in each repository
    for i, page in enumerate(pageCount):

        print("page number:",i,"page:",page)
        #print("repository name:", repo['name'], ",i*******", i)
        url = f"https://api.github.com/repos/{orgName}/{repo['name']}/commits?per_page=100&page={page}"
        print(url)
        dataCommitList = requests.get(url, headers=headers).json()

        #if the repository has commits
        if len(dataCommitList) > 0:
            # print(len(data))

            # for loop to get the modified files in each commit
            for j, commit in enumerate(dataCommitList):

                #commitCountPerRepo += 1

                # if it is the first commit, get the commit date
                if i == 0 and j == 0:
                    #print("first commit dateeeee")
                    firstCommitDate = parser.parse(commit['commit']['committer']['date'])
                lastCommitDate = parser.parse(commit['commit']['committer']['date'])
                commit_yearMonth = str(lastCommitDate.year) + "-" + str(lastCommitDate.month)

                # save commit date into array
                if commit_yearMonth in commitDateArr:
                    commitDateArr[commit_yearMonth] += 1
                else:
                    commitDateArr[commit_yearMonth] = 1

                urlCommit = f"https://api.github.com/repos/{orgName}/{repo['name']}/commits/{commit['sha']}"
                #print(urlCommit)
                dataCommit = requests.get(urlCommit, headers=headers).json()

                # print("files count:",len(dataCommit['files']))
                for file in dataCommit['files']:
                    # print(file['filename'])
                    if ((file['filename'].endswith('.pp'))):
                        #print(commit['sha'])
                        # print(file['status'])

                        iacFile = {"repo_name": repo['name'], "commit_sha": commit['sha'],
                                   "commit_msg": commit['commit']['message'], "commit_html": commit['html_url'],
                                   "file_name": file['filename'], "file_status": file['status']}
                        repoCommitFiles.append(iacFile)

                        #create a unique array of pp files for each repo
                        if repo['name'] in repoCommitFileArr:
                            if file['filename'] not in repoCommitFileArr[repo['name']]:
                                repoCommitFileArr[repo['name']].append(file['filename'])
                        else:
                            repoCommitFileArr[repo['name']] = []

                if(fileItem['filename'].endswith('.pp') for fileItem in dataCommit['files']):
                    #print("yeeeeeeeeeeeeeeeeeeeeeeeeees",dataCommit['commit']['message']);
                    numOfOrgCommits += 1
                    ppCommitCountPerRepo += 1


        else:
            print("no more commits")
            break

    if firstCommitDate is not None:
        # if first and last commit were in the same month
        if firstCommitDate.strftime("%Y-%m") == lastCommitDate.strftime("%Y-%m"):
            print("first last in same month&^%&^&%^", lastCommitDate.strftime("%Y-%m"))
            commitArrLen = 1
        # calculate the months between commits
        else:
            commitArrLen = (firstCommitDate.year - lastCommitDate.year) * 12 + (firstCommitDate.month - lastCommitDate.month) + 1
    # if there were no commits
    else:
        commitArrLen = None

    #print date array for each repo
    #for i in commitDateArr:
        #print("key:", i, "value:", commitDateArr[i])

    print("first commit date:", firstCommitDate)
    print("last commit date:", lastCommitDate)
    print("commitArrLen should be:", commitArrLen)
    print("commitArrLen is:", len(commitDateArr))

    #if we have at least one commit per month between start and end date
    if len(commitDateArr) == commitArrLen and commitArrLen is not None:
        isCommited2perMonth = True
        for i in commitDateArr:
            #print("key:", i, "value:", commitDateArr[i])
            if int(commitDateArr[i]) < 2:
                isCommited2perMonth = False

        #if we have at least two commits per month
        if isCommited2perMonth:
            print("this repo is ok******:",repo['name'])
            #validCommits.append(perRepoCommits)
            numOfAllRepos += 1
            validCommits += repoCommitFiles

            #create an array for valid repositories with first-last commit date
            rcItem = {"repo_name": repo['name'], "first_commit_date": firstCommitDate,
                      "last_commit_date": lastCommitDate, "all_commit_count": commitCountPerRepo,
                      "iac_commit_count": ppCommitCountPerRepo, "number_of_months": commitArrLen}

            #get distribution of commits && commit with iac file
            if commitArrLen != 0:
                if commitCountPerRepo != 0:
                    rcItem["average_commit_distribution"] = round((commitCountPerRepo / commitArrLen), 2)
                else:
                    rcItem["average_commit_distribution"] = 0
                if ppCommitCountPerRepo != 0:
                    rcItem["average_ppCommit_distribution"] = round((ppCommitCountPerRepo / commitArrLen), 2)
                else:
                    rcItem["average_ppCommit_distribution"] = 0
                validRepoCommitList.append(rcItem)

#print("all commits,per files:",len(validCommits))
print("number of all repos:",numOfAllRepos)
print("number of all commits:",numOfOrgCommits)

for i in repoCommitFileArr:
    print("key for file array^^^^:", i, "value:", repoCommitFileArr[i])
# for i in repoCommitFileArr:
#     for j in repoCommitFileArr[i]:
#         rcItem = {"repository_name": repoCommitFileArr[i],
#                   "iac_file_name": repoCommitFileArr[i][j]}



dfFile = pd.DataFrame(validCommits)
dfFile.to_csv(f"{orgName}_commits.csv")

dfCommitDetailFile = pd.DataFrame(validRepoCommitList)
dfCommitDetailFile.to_csv(f"{orgName}_repo_commitDetails.csv")




