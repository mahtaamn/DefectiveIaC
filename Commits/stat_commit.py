import pandas as pd
import requests
from dateutil import parser
import time


headers = {
    'Authorization': 'token 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'
}

orgName = "mirantis"
df = pd.read_csv(f"{orgName}_repository.csv")
#filter repos based on 11% pp condition;
dfData = df['isCriteria2Met'] == 1
filteredRepos = df[dfData]
print("number of repositories with at least 11% pp files:", len(filteredRepos))
# make sure indexes pair with number of rows
filteredData = filteredRepos.reset_index()


#define variables for all of data
validCommits = []
repoSummaryList = []

# for loop for each repository
for index, repo in filteredData.iterrows():
    print("next repository name:", repo['name'],"index=====>:",index)
    pageCount = list(range(1, 55))

    #reset variables per repository
    repoCommitFiles = []
    commitDateArr = {}
    firstCommitDate = None
    lastCommitDate = None

    ppCommitCountPerRepo = 0
    commitCountPerRepo = 0
    numTotalFileChange = 0
    numTotalIacChange = 0

    # for loop to get all commits in each repository
    for i, page in enumerate(pageCount):

        # if page > 10:
        #     print("break from page*************,project:",repo['name'])
        #     break

        print("repository name:", repo['name'], ",i*******", i,"page:",page)

        url = f"https://api.github.com/repos/{orgName}/{repo['name']}/commits?per_page=100&page={page}"
        dataCommitList = requests.get(url, headers=headers).json()

        #if the repository has commits
        if len(dataCommitList) > 0:
            # print(len(data))

            # for loop to get the modified files in each commit
            for j, commit in enumerate(dataCommitList):
                print("j=>",j);
                commitCountPerRepo += 1
                time.sleep(3)

                #if j == 30 or j == 50 or j == 80:
                    #time.sleep(8)
                ############################################################
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
                ##############################################################

                urlCommit = f"https://api.github.com/repos/{orgName}/{repo['name']}/commits/{commit['sha']}"
                #print(urlCommit)
                dataCommit = requests.get(urlCommit, headers=headers).json()

                # print("files count:",len(dataCommit['files']))
                for file in dataCommit['files']:

                    # print(file['filename'])
                    numTotalFileChange += 1

                    if ((file['filename'].endswith('.pp'))):
                        numTotalIacChange += 1

                        iacFile = {"repo_name": repo['name'], "commit_sha": commit['sha'],
                                   "commit_msg": commit['commit']['message'], "commit_html": commit['html_url'],
                                   "file_name": file['filename'], "file_status": file['status']}
                        repoCommitFiles.append(iacFile)

                isIncludePP = False
                for fileItem in dataCommit['files']:
                    if fileItem['filename'].endswith('.pp') and isIncludePP is False:
                        ppCommitCountPerRepo += 1
                        isIncludePP = True
                        print("found a pp file",fileItem['filename'])
                # gen = (xfile for xfile in dataCommit['files'] if xfile.endswith('.pp'))
                # if len(gen) > 0:
                #     print("found a pp file")
                #     ppCommitCountPerRepo += 1
                # else:
                #     print("noooo pp");

        else:
            print("no more commits")
            break


    ########## calculate length of datetime array#########################
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
    #####################################################################

    #print date array for each repo
    #for i in commitDateArr:
        #print("key:", i, "value:", commitDateArr[i])

    print("first commit date:", firstCommitDate)
    print("last commit date:", lastCommitDate)
    print("commitArrLen should be:", commitArrLen)
    print("commitArrLen is:", len(commitDateArr))

    ################if condition 3 is met##############################
    isCommited2perMonth = True
    if len(commitDateArr) == commitArrLen and commitArrLen is not None:
        for i in commitDateArr:
            #print("key:", i, "value:", commitDateArr[i])
            if int(commitDateArr[i]) < 2:
                isCommited2perMonth = False
        if isCommited2perMonth:
            print("this repo is ok******:", repo['name'])
            validCommits += repoCommitFiles
    else:
        isCommited2perMonth = False
    ####################################################################

    rcItem = {"repo_name": repo['name'], "first_commit_date": firstCommitDate,
                  "last_commit_date": lastCommitDate, "#months_between_commits": commitArrLen,
                  "isCriteria3Met": isCommited2perMonth, "#total_file_changes": numTotalFileChange,
                  "#total_iac_changes": numTotalIacChange, "#total_commits": commitCountPerRepo,
                  "#total_iac_commits": ppCommitCountPerRepo}

    # if numTotalIacChange != 0 and numTotalFileChange != 0:
    #     rcItem["ratio_iac_files"] = round((numTotalFileChange/numTotalFileChange),2)
    # else:
    #     rcItem["ratio_iac_files"] = 0

    if numTotalIacChange != 0 and commitArrLen != 0:
        rcItem["average_iac_change_rate"] = round((numTotalIacChange / commitArrLen), 2)
    else:
        rcItem["average_iac_change_rate"] = 0

    repoSummaryList.append(rcItem)


# &&&&&&&&& for loop finished- end of line
#print("all commits,per files:",len(validCommits))


dfFile = pd.DataFrame(validCommits)
dfFile.to_csv(f"{orgName}_commits_list.csv")

dfCommitDetailFile = pd.DataFrame(repoSummaryList)
dfCommitDetailFile.to_csv(f"{orgName}_repo_commit_withstats.csv")




