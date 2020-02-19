from github import Github
import os
import requests
import json
import iso8601
import datetime
import xlwt
"""
data = os.popen('curl -i https://api.github.com/repos/eosio/eos').read()

commits = os.popen('curl https://api.github.com/repos/eosio/eos/stats/commit_activity').read()
issues = os.popen('curl https://api.github.com/repos/eosio/eos/issues').read()
"""
username = 'ryhan123'
token = '2a70365fee78b3cee65dcd8079cc971def20ce90'
gh_session = requests.Session()
gh_session.auth = (username, token)

EOS_URL = 'https://api.github.com/repos/eosio/eos'
RELEASES_URL = '/releases'
COMMITS_URL = '/commits'
ISSUES_URL = '/issues'
PULL_REQUESTS_URL = '/pulls'
FORK_URL = '/forks'
BRANCH_URL = '/branches'

"""
#region Releases


total_releases = []
i = 1
while True:
	#r = requests.get(EOS_URL + RELEASES_URL + '?page={}&per_page=100'.format(i))
	releases = json.loads(gh_session.get(EOS_URL + RELEASES_URL + '?page={}&per_page=100'.format(i)).text)
	if len(releases) == 0:
		break
	total_releases += releases
	if len(releases) < 100:
		break
	i += 1

release_count = len(total_releases)
latest_release = iso8601.parse_date(total_releases[0]['created_at'])
release_issuers = {}
for i in range(release_count):
	curr_author = total_releases[i]['author']['login']
	if curr_author in release_issuers:
		release_issuers[curr_author] += 1
	else:
		release_issuers[curr_author] = 1
release_authors = release_issuers.keys()

release_data = {'Release_Count': release_count,
				'Latest_Release': latest_release,
				'Authors': release_authors}


#endregion
print('Finished with Releases')
with open('releases.txt', 'w') as outfile:
	json.dump(release_data, outfile, default=str)
#region Issues


cum_issues = []

i = 1
while True:
	issues = json.loads(gh_session.get(EOS_URL + ISSUES_URL + '?state=all&page={}&per_page=100'.format(i)).text)
	if len(issues) == 0:
		break
	cum_issues += issues
	if len(issues) < 100:
		break
	i += 1

total_issue_count = len(cum_issues)
latest_issue = cum_issues[0]['created_at']
unresolved_issues = []
unresolved_issue_labels = {}

resolved_issues = []
resolved_issue_labels = {}
comment_count = 0
commented_issue_count = 0
# Issues traversed newest to oldest, sorted into both resolved and unresolved, and then further by label
for i in range(total_issue_count):
	if cum_issues[i]['state'] == 'open': #issues are unresolved
		unresolved_issues.append(cum_issues[i])
		for label_index in range(len(cum_issues[i]['labels'])):

			label_key = cum_issues[i]['labels'][label_index]['name'] # easy to read 

			if label_key in unresolved_issue_labels: 
				unresolved_issue_labels[label_key].append(cum_issues[i])

			else:
				unresolved_issue_labels[label_key] = list()
				unresolved_issue_labels[label_key].append(cum_issues[i])
	else: #issues are resolved

		resolved_issues.append(cum_issues[i])
		for label_index in range(len(cum_issues[i]['labels'])):

			label_key = cum_issues[i]['labels'][label_index]['name']

			if label_key in resolved_issue_labels:

				resolved_issue_labels[label_key].append(cum_issues[i])

			else:
				resolved_issue_labels[label_key] = list()
				resolved_issue_labels[label_key].append(cum_issues[i])

		

	if cum_issues[i]['comments'] != 0:
		commented_issue_count += 1
		comment_count += cum_issues[i]['comments']


resolved_issue_count = len(resolved_issues) # Number of Resolved Issues
unresolved_issue_count = len(unresolved_issues) # Number of Unresolved Issues

resolved_issue_percentage = resolved_issue_count / total_issue_count # Percentage of Issues that are resolved
unresolved_issue_percentage = unresolved_issue_count / total_issue_count # Percentage of Issues that are unresolved

oldest_unresolved_issue = unresolved_issues[-1]['created_at'] #oldest unresolved issue
commented_issue_percent = commented_issue_count / total_issue_count # Percentage of issues that are commented on

resolved_issue_data = {}
unresolved_issue_data = {}

for label_key in resolved_issue_labels:
	each_label_count = len(resolved_issue_labels[label_key])
	time_to_resolve_issue = []
	for index in range(each_label_count):
		date_created = iso8601.parse_date(resolved_issue_labels[label_key][index]['created_at'])
		date_closed = iso8601.parse_date(resolved_issue_labels[label_key][index]['closed_at'])
		time_between = date_closed - date_created
		time_to_resolve_issue.append(time_between)

	time_to_resolve_issue = sorted(time_to_resolve_issue)
	min_resolve_time = time_to_resolve_issue[0] #useful
	max_resolve_time = time_to_resolve_issue[-1] #useful
	median_resolve_time = time_to_resolve_issue[len(time_to_resolve_issue) // 2] #useful as metric
	temp_days = 0
	temp_seconds = 0
	temp_microseconds = 0
	for timedelta_instance in time_to_resolve_issue:
		temp_days += timedelta_instance.days
		temp_seconds += timedelta_instance.seconds
		temp_microseconds += timedelta_instance.microseconds
	temp_days /= len(time_to_resolve_issue)
	temp_seconds /= len(time_to_resolve_issue)
	temp_microseconds /= len(time_to_resolve_issue)
	mean_resolve_time = datetime.timedelta(days=temp_days, seconds=temp_seconds, microseconds=temp_microseconds)



	resolved_issue_data[label_key] = {'amount': each_label_count, 'percentage': each_label_count / resolved_issue_count, 'min_resolve_time': min_resolve_time, 'max_resolve_time': max_resolve_time, 'median_resolve_time': median_resolve_time, 'mean_resolve_time': mean_resolve_time}


for label_key in unresolved_issue_labels:
	each_label_count = len(unresolved_issue_labels[label_key])
	time_unresolved_issue = []
	for index in range(each_label_count):
		date_created = iso8601.parse_date(unresolved_issue_labels[label_key][index]['created_at'])
		time_between = datetime.datetime.now().replace(tzinfo=None) - date_created.replace(tzinfo=None)
		time_unresolved_issue.append(time_between)

	time_unresolved_issue = sorted(time_unresolved_issue)
	min_unresolved_time = time_unresolved_issue[0] # probably not useful
	max_unresolved_time = time_unresolved_issue[-1] # potentially useful
	median_unresolved_time = time_unresolved_issue[len(time_unresolved_issue) // 2] #potentially useful
	temp_days = 0
	temp_seconds = 0
	temp_microseconds = 0
	for timedelta_instance in time_unresolved_issue:
		temp_days += timedelta_instance.days
		temp_seconds += timedelta_instance.seconds
		temp_microseconds += timedelta_instance.microseconds
	temp_days /= len(time_unresolved_issue)
	temp_seconds /= len(time_unresolved_issue)
	temp_microseconds /= len(time_unresolved_issue)
	mean_unresolved_time = datetime.timedelta(days=temp_days, seconds=temp_seconds, microseconds=temp_microseconds)


	unresolved_issue_data[label_key] = {'amount': each_label_count, 'percentage': each_label_count / unresolved_issue_count, 'min_unresolved_time': min_unresolved_time, 'max_unresolved_time': max_unresolved_time, 'median_unresolved_time': median_unresolved_time, 'mean_unresolved_time': mean_unresolved_time}


issue_data = {'Total_Issues': total_issue_count, 
				'Resolved_Issues': resolved_issue_count, 
				'Unresolved_Issues': unresolved_issue_count,
				'Commented_Issues': commented_issue_count,
				'Comment_Count': comment_count,
				'Percent_Commented': commented_issue_percent,
				'Latest_Issue': latest_issue,
				'Percent_Resolved': resolved_issue_percentage,
				'Percent_Unresolved': unresolved_issue_percentage}
#endregion
print('Finished with Issues')
with open('gen_issues.txt', 'w') as outfile:
	json.dump(issue_data, outfile, default=str)
with open('resolved_issues.txt', 'w') as outfile:
	json.dump(resolved_issue_data, outfile, default=str)
with open('unresolved_issues.txt', 'w') as outfile:
	json.dump(unresolved_issue_data, outfile, default=str)

#region Pull Requests

pulls = []
i = 1

while True:
	pull_requests = json.loads(gh_session.get(EOS_URL + PULL_REQUESTS_URL + '?state=all&page={}&per_page=100'.format(i)).text)
	if len(pull_requests) == 0:
		break
	pulls += pull_requests
	if len(pull_requests) < 100:
		break
	print(i)
	i += 1

total_pulls = len(pulls)
resolved_pulls = []
resolved_pull_labels = {}

unresolved_pulls = []
unresolved_pull_labels = {}

comment_count_pull = 0
commented_pull_count = 0

for i in range(total_pulls):

	if pulls[i]['state'] == 'open': #pull request is unresolved
		unresolved_pulls.append(pulls[i])
		for label_index in range(len(pulls[i]['labels'])):
			label_key = pulls[i]['labels'][label_index]['name']
			if label_key not in unresolved_pull_labels:
				unresolved_pull_labels[label_key] = list()
			unresolved_pull_labels[label_key].append(pulls[i])

	else: 
		resolved_pulls.append(pulls[i])
		for label_index in range(len(pulls[i]['labels'])):
			label_key = pulls[i]['labels'][label_index]['name']
			if label_key not in resolved_pull_labels:
				resolved_pull_labels[label_key] = list()
			resolved_pull_labels[label_key].append(pulls[i])

resolved_pull_count = len(resolved_pulls)
unresolved_pull_count = len(unresolved_pulls)

resolved_pull_percentage = resolved_pull_count / total_pulls
unresolved_pull_percentage = unresolved_pull_count / total_pulls
resolved_pull_data = {}
unresolved_pull_data = {}

for label_key in resolved_pull_labels:
	amount = len(resolved_pull_labels[label_key])
	percent = amount / resolved_pull_count
	resolved_pull_data[label_key] = {'amount': amount, 'percent': percent}


for label_key in unresolved_pull_labels:
	amount = len(unresolved_pull_labels[label_key])
	percent = amount / unresolved_pull_count
	unresolved_pull_data[label_key] = {'amount': amount, 'percent': percent}
latest_pull = pulls[0]


pull_data = {'Total_Requests': total_pulls,
				'Unresolved_Pulls': unresolved_pull_count,
				'Resolved_Pulls': resolved_pull_count,
				'Resolved_Pull_%': resolved_pull_percentage,
				'Unresolved_Pull_Percentage': unresolved_pull_percentage,
				'Oldest_Unresolved_Pull_Req': unresolved_pulls[-1]['created_at']}

#endregion
print('Finished with pulls')
with open('gen_pulls.txt', 'w') as outfile:
	json.dump(pull_data, outfile)
with open('resolved_pulls.txt', 'w') as outfile:
	json.dump(resolved_pull_data, outfile, default=str)
with open('unresolved_pulls.txt', 'w') as outfile:
	json.dump(unresolved_pull_data, outfile, default=str)
#region Commits

i = 1
total_commits = []
while True:
	commits = json.loads(gh_session.get(EOS_URL + COMMITS_URL + '?page={}&per_page=100'.format(i)).text)
	if len(commits) == 0:
		break
	total_commits += commits
	if len(commits) < 100:
		break
	print(i)
	i += 1
first_commit = total_commits[-1]['commit']['author']['date']
last_commit = total_commits[0]['commit']['author']['date']

commit_data = {'Total': len(total_commits), 'Latest_Commit': last_commit, 'First_Commit': first_commit}

#endregion
print('Finished with Commits')
with open('commits.txt', 'w') as outfile:
	json.dump(commit_data, outfile, default=str)
#region Forks

total_forks = []

i = 1
while True:
	forks = json.loads(gh_session.get(EOS_URL + FORK_URL + '?page={}&per_page=100'.format(i)).text)
	if len(forks) == 0:
		break

	total_forks += forks
	print(i)
	if len(forks) < 100:
		break

	i += 1
latest_fork = total_forks[0]['created_at']
first_fork = total_forks[-1]['created_at']

fork_data = {'Total': len(total_forks), 'Latest_Fork': latest_fork, 'First_Fork': first_fork}

#endregion
print('Finished with Forks')
with open('forks.txt', 'w') as outfile:
	json.dump(fork_data, outfile, default=str)
#region Branches


total_branches = []
i = 1
while True:
	branches = json.loads(gh_session.get(EOS_URL + BRANCH_URL + '?page={}&per_page=100'.format(i)).text)
	if len(branches) == 0:
		break

	total_branches += branches
	if len(branches) < 100:
		break
	i += 1
#print(total_branches[0]['commit'].keys())
branch_last_updated = []

for branch_num in range(len(total_branches)):
	date = iso8601.parse_date(json.loads(gh_session.get(total_branches[branch_num]['commit']['url']).text)['commit']['committer']['date'])
	print(branch_num, total_branches[branch_num]['name'])
	time_since_last_update = datetime.datetime.now().replace(tzinfo=None) - date.replace(tzinfo=None)
	branch_last_updated.append(time_since_last_update)
branch_last_updated = sorted(branch_last_updated)
active_one_month = 0
active_three_months = 0
active_twelve_months = 0
for date in branch_last_updated:
	if date.days <= 30:
		active_one_month += 1
	if date.days <= 92:
		active_three_months += 1
	if date.days <= 365:
		active_twelve_months += 1
active_one_month_percent = active_one_month / len(total_branches)
active_three_months_percent = active_three_months / len(total_branches)
active_twelve_months_percent = active_twelve_months / len(total_branches)

branch_data = {'Total': len(total_branches), 
				'Active_Last_Month': active_one_month, 
				'Active_3_Month': active_three_months,
				'Active_Last_Year': active_twelve_months,
				'Percent_Last_Month': active_one_month_percent,
				'Percent_3_Months': active_three_months_percent,
				'Percent_12_Months': active_twelve_months_percent}




#endregion
print('Finished with Branches')
with open('branches.txt', 'w') as outfile:
	json.dump(branch_data, outfile, default=str)
#region Contributors (Unfinished)
"""
"""
i = 1

h = json.loads(gh_session.get(EOS_URL + '/stats/contributors?page={}&per_page=100'.format(i)).text)
print(h[0]['author']['login'])
print(h[1]['author']['login'])
print(len(h))
"""

#endregion
with open('gen_issues.txt') as json_file:
	issue_data = json.load(json_file)
with open('resolved_issues.txt') as json_file:
	resolved_issue_data = json.load(json_file)
with open('unresolved_issues.txt') as json_file:
	unresolved_issue_data = json.load(json_file)
with open('releases.txt') as json_file:
	release_data = json.load(json_file)
with open('gen_pulls.txt') as json_file:
	pull_data = json.load(json_file)
with open('resolved_pulls.txt') as json_file:
	resolved_pull_data = json.load(json_file)
with open('unresolved_pulls.txt') as json_file:
	unresolved_pull_data = json.load(json_file)
with open('forks.txt') as json_file:
	fork_data = json.load(json_file)
with open('branches.txt') as json_file:
	branch_data = json.load(json_file)
with open('commits.txt') as json_file:
	commit_data = json.load(json_file)
	
wb = xlwt.Workbook()
ws = wb.add_sheet('EOS_Github_Data')
curr_row = 0 #Column always resets to 0
curr_col = 0

#Write RELEASES data
ws.write(curr_row, curr_col, 'RELEASES')
curr_row += 1
for attribute in release_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, release_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing Releases')
#Write BRANCHES data
ws.write(curr_row, curr_col, 'BRANCHES')
curr_row += 1
for attribute in branch_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, branch_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing Branches', curr_row)
#Write FORKS data
ws.write(curr_row, curr_col, 'FORKS')
curr_row += 1
for attribute in fork_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, fork_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing Forks', curr_row)
#Write COMMITS data
ws.write(curr_row, curr_col, 'COMMITS')
curr_row += 1
for attribute in commit_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, commit_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing Commits', curr_row)
#Write GENERAL PULL REQUEST data
ws.write(curr_row, curr_col, 'PULL REQUESTS')
curr_row += 1
for attribute in pull_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, pull_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing gen_pulls', curr_row)
#Write RESOLVED PULL REQUEST data
ws.write(curr_row, curr_col, 'Resolved_Pull_Requests')
curr_row += 1
ws.write(curr_row, curr_col, 'Name')
att_count = 0
for label in resolved_pull_data:
	temp_row = curr_row
	curr_col += 1
	ws.write(temp_row, curr_col, label)
	for attribute in resolved_pull_data[label]:
		temp_row += 1
		if curr_col == 1:
			att_count += 1
			ws.write(temp_row, 0, attribute)
		ws.write(temp_row, curr_col, resolved_pull_data[label][attribute])
curr_col = 0
curr_row += att_count + 2
print('Finished writing resolved_pulls', curr_row)
#Write UNRESOLVED PULL REQUEST data
ws.write(curr_row, curr_col, 'Unesolved_Pull_Requests')
curr_row += 1
ws.write(curr_row, curr_col, 'Name')
att_count = 0
for label in unresolved_pull_data:
	temp_row = curr_row
	curr_col += 1
	ws.write(temp_row, curr_col, label)
	for attribute in unresolved_pull_data[label]:
		temp_row += 1
		if curr_col == 1:
			att_count += 1
			ws.write(temp_row, 0, attribute)
		ws.write(temp_row, curr_col, unresolved_pull_data[label][attribute])
curr_col = 0
curr_row += att_count + 2
print('Finished writing unresolved_pulls', curr_row)
#Write GENERAL ISSUES data

ws.write(curr_row, curr_col, 'ISSUES')
curr_row += 1
for attribute in issue_data:
	ws.write(curr_row, curr_col, attribute)
	ws.write(curr_row + 1, curr_col, issue_data[attribute])
	curr_col += 1
curr_row += 3
curr_col = 0
print('Finished writing gen_issues', curr_row)
#Write RESOLVED ISSUES data

ws.write(curr_row, curr_col, 'Resolved_Issues')
curr_row += 1
ws.write(curr_row, curr_col, 'Name')
att_count = 0
for label in resolved_issue_data:
	temp_row = curr_row
	curr_col += 1
	ws.write(temp_row, curr_col, label)
	for attribute in resolved_issue_data[label]:
		temp_row += 1
		if curr_col == 1:
			att_count += 1
			ws.write(temp_row, 0, attribute)
		ws.write(temp_row, curr_col, resolved_issue_data[label][attribute])
curr_col = 0
curr_row += att_count + 2
print('Finished writing resolved_issues', curr_row)

#Write UNRESOLVED ISSUES data

ws.write(curr_row, curr_col, 'Unresolved_Issues')
curr_row += 1
ws.write(curr_row, curr_col, 'Name')
att_count = 0
for label in unresolved_issue_data:
	temp_row = curr_row
	curr_col += 1
	ws.write(temp_row, curr_col, label)
	for attribute in unresolved_issue_data[label]:
		
		temp_row += 1
		if curr_col == 1:
			att_count += 1
			ws.write(temp_row, 0, attribute)
		ws.write(temp_row, curr_col, unresolved_issue_data[label][attribute])
curr_col = 0
curr_row += att_count + 2
print('Finished writing unresolved_issues', curr_row)
wb.save('Github_data_pull.xls')



