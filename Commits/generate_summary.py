import pandas as pd


orgName = "mirantis"
df = pd.read_csv(f"{orgName}_repo_commit_withstats.csv")
#filter repos based on 11% pp condition;
dfData = df['isCriteria3Met'] == True
filteredRepos = df[dfData]
print("number of repositories that meet the 3rd criteria:", len(filteredRepos))
# make sure indexes pair with number of rows
filteredData = filteredRepos.reset_index()


sumAvgCount = 0
numberOfAllCommits = 0
numberOfIACCommits = 0
numberofIACScripts = 0
for index, repo in filteredData.iterrows():
    print(repo['repo_name'])
    print(repo['average_iac_change_rate'])
    sumAvgCount += repo['average_iac_change_rate']
    print("sumAvgCount:",sumAvgCount)
    numberOfAllCommits+=repo['#total_commits']
    numberOfIACCommits += repo['#total_iac_commits']
    numberofIACScripts += repo['#total_iac_changes']
    #print("next repository name:", repo['name'],"index=====>:",index)
    #print("average_iac_change_rate:",repo['average_iac_change_rate'])
finalAverage = round(sumAvgCount/len(filteredRepos),2)
print("finalAverage:",finalAverage)
# print("numberOfAllCommits:",numberOfAllCommits)
# print("numberOfIACCommits:",numberOfIACCommits)
# print("numberofIACScripts:",numberofIACScripts)