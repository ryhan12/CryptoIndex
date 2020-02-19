import requests
import json
import iso8601
import datetime
import os
import csv
import pandas
import mat
username = 'ryhan123'
token = '2a70365fee78b3cee65dcd8079cc971def20ce90'
gh_session = requests.Session()
gh_session.auth = (username, token)
paged_attribute_url_tags = {'RELEASES': '/releases', 'COMMITS': '/commits', 'ISSUES': '/issues', 'PULLS': '/pulls', 'BRANCHES': '/branches', 'FORKS': '/forks', 'CONTRIBUTORS': '/stats/contributors'}
repo_urls = {'EOS': 'https://api.github.com/repos/eosio/eos', 'TRON': 'https://api.github.com/repos/tronprotocol/java-tron'}

def getPagedAttributes(REPO, ATTRIBUTE, STATE=''):
	total_attributes = []
	i = 1
	while True:
		#r = requests.get(EOS_URL + RELEASES_URL + '?page={}&per_page=100'.format(i))
		attributes = json.loads(gh_session.get(REPO + ATTRIBUTE + '?{}page={}&per_page=100'.format(STATE, i)).text)
		if len(attributes) == 0:
			break
		total_attributes += attributes
		if len(attributes) < 100:
			break
		i += 1
	print('Finished collecting {} for {}'.format(ATTRIBUTE, REPO))
	print('\tStats: Total size = {}'.format(len(total_attributes)))
	if 'created_at' in total_attributes[0]:
		total_attributes = sorted(total_attributes, key = lambda i: iso8601.parse_date(i['created_at']))
	return total_attributes

def getRepoReleaseData(total_releases):

	release_count = len(total_releases)
	latest_release = iso8601.parse_date(total_releases[-1]['created_at'])
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
	print('Finished organizing repo data: {} releases'.format(release_count))
	return release_data

def getRepoIssueData(total_issues):

	total_issue_count = len(total_issues)
	latest_issue = total_issues[-1]['created_at']
	unresolved_issues = []
	unresolved_issue_labels = {}

	resolved_issues = []
	resolved_issue_labels = {}
	comment_count = 0
	commented_issue_count = 0
	three_month_count = 0;
	six_month_count = 0;

	# Issues traversed newest to oldest, sorted into both resolved and unresolved, and then further by label
	for i in range(total_issue_count):



		if total_issues[i]['state'] == 'open': #issues are unresolved
			unresolved_issues.append(total_issues[i])
			for label_index in range(len(total_issues[i]['labels'])):

				label_key = total_issues[i]['labels'][label_index]['name'] # easy to read 

				if label_key in unresolved_issue_labels: 
					unresolved_issue_labels[label_key].append(total_issues[i])

				else:
					unresolved_issue_labels[label_key] = list()
					unresolved_issue_labels[label_key].append(total_issues[i])
		else: #issues are resolved

			resolved_issues.append(total_issues[i])
			for label_index in range(len(total_issues[i]['labels'])):

				label_key = total_issues[i]['labels'][label_index]['name']

				if label_key in resolved_issue_labels:

					resolved_issue_labels[label_key].append(total_issues[i])

				else:
					resolved_issue_labels[label_key] = list()
					resolved_issue_labels[label_key].append(total_issues[i])

		

		if total_issues[i]['comments'] != 0:
			commented_issue_count += 1
			comment_count += total_issues[i]['comments']


	resolved_issue_count = len(resolved_issues) # Number of Resolved Issues
	unresolved_issue_count = len(unresolved_issues) # Number of Unresolved Issues

	resolved_issue_percentage = resolved_issue_count / total_issue_count # Percentage of Issues that are resolved
	unresolved_issue_percentage = unresolved_issue_count / total_issue_count # Percentage of Issues that are unresolved

	oldest_unresolved_issue = unresolved_issues[0]['created_at'] #oldest unresolved issue
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
	print('Finished organizing issue data')
	return issue_data, resolved_issue_data, unresolved_issue_data

def getRepoPullData(pulls):

	total_pulls = len(pulls)
	resolved_pulls = []
	resolved_pull_labels = {}

	unresolved_pulls = []
	unresolved_pull_labels = {}

	comment_count_pull = 0
	commented_pull_count = 0
	print(total_pulls)
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
	latest_pull = pulls[-1]


	pull_data = {'Total_Requests': total_pulls,
				'Unresolved_Pulls': unresolved_pull_count,
				'Resolved_Pulls': resolved_pull_count,
				'Resolved_Pull_%': resolved_pull_percentage,
				'Unresolved_Pull_Percentage': unresolved_pull_percentage,
				'Oldest_Unresolved_Pull_Req': unresolved_pulls[0]['created_at'] if unresolved_pull_count != 0 else 'N/A'}
	print('Finished organizing pull data')
	return pull_data, resolved_pull_data, unresolved_pull_data

def getRepoCommitData(total_commits):

	first_commit = total_commits[0]['commit']['author']['date']
	last_commit = total_commits[-1]['commit']['author']['date']

	commit_data = {'Total': len(total_commits), 'Latest_Commit': last_commit, 'First_Commit': first_commit}
	print('Finished organizing commit data')
	return commit_data

def getRepoForkData(total_forks):

	latest_fork = total_forks[-1]['created_at']
	first_fork = total_forks[0]['created_at']


	fork_data = {'Total': len(total_forks), 'Latest_Fork': latest_fork, 'First_Fork': first_fork}
	print('Finished organizing fork data')
	return fork_data

def getRepoBranchData(total_branches):

	branch_last_updated = []

	for branch_num in range(len(total_branches)):
		date = iso8601.parse_date(json.loads(gh_session.get(total_branches[branch_num]['commit']['url']).text)['commit']['committer']['date'])
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
	print('Finished organizing branch data')
	return branch_data

def getRepoContributorData(total_contributors):

	top_contributors = total_contributors[:5]
	print(total_contributors[0]['author']['login'])
	print(total_contributors[1]['author']['login'])
	print(len(total_contributors))
	return top_contributors

def findReleaseOverlap(releases, issues):
	release_ranges = {}
	offset = 0
	for i in range(len(releases)):
		current_release_date = iso8601.parse_date(releases[i]['created_at'])
		range_low_end = current_release_date - datetime.timedelta(days=2)
		range_high_end = current_release_date + datetime.timedelta(days=2)
		release_ranges[(releases[i]['tag_name'], releases[i]['created_at'])] = list()
		for j in range(offset, len(issues)):
			issue_time = iso8601.parse_date(issues[j]['created_at'])
			if issue_time > range_low_end and issue_time < range_high_end:
				release_ranges[(releases[i]['tag_name'], releases[i]['created_at'])].append(issues[j]['id'])
			if issue_time < range_low_end:
				offset += 1

	return release_ranges

def writeGeneralToFile(title, data_set, csv_file_writer):
	if data_set == {}:
		return
	curr_line = list()
	csv_file_writer.writerow([title])
	csv_file_writer.writerow(data_set.keys())
	for i in data_set:
		curr_line.append(data_set[i])
	csv_file_writer.writerow(curr_line)
	csv_file_writer.writerow([])

def writeSpecificToFile(title, data_set, csv_file_writer):
	if data_set == {}:
		return
	print(data_set)
	curr_line = list()
	csv_file_writer.writerow([title])
	csv_file_writer.writerow(['Name'] + list(data_set.keys()))
	for i in data_set[list(data_set.keys())[0]].keys():
		curr_line = list()
		curr_line.append(i)
		for j in data_set:
			curr_line.append(data_set[j][i])
		csv_file_writer.writerow(curr_line)
	csv_file_writer.writerow([])

#def writeHeaderData(title, data_set, csv_file_writer):
def getCountOverTime(attribute, years=0, months=1):

def main():
	overall_repo_attributes = {}
	overall_repo_data = {}
	for repo in repo_urls:
		releases = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['RELEASES'])
		pulls = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['PULLS'], 'state=all&')
		issues = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['ISSUES'], 'state=all&')
		commits = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['COMMITS'])
		branches = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['BRANCHES'])
		forks = getPagedAttributes(repo_urls[repo], paged_attribute_url_tags['FORKS'])
		within_range = findReleaseOverlap(releases, issues)
		release_data = getRepoReleaseData(releases)
		pull_data, resolved_pull_data, unresolved_pull_data = getRepoPullData(pulls)
		issue_data, resolved_issue_data, unresolved_issue_data = getRepoIssueData(issues)
		commit_data = getRepoCommitData(commits)
		branch_data = getRepoBranchData(branches)
		fork_data = getRepoForkData(forks)
		with open('{}_output.csv'.format(repo), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			writeGeneralToFile('RELEASES', release_data, writer)
			writeGeneralToFile('BRANCHES', branch_data, writer)
			writeGeneralToFile('FORKS', fork_data, writer)
			writeGeneralToFile('PULL REQUESTS', pull_data, writer)
			writeSpecificToFile('Resolved Pull Requests', resolved_pull_data, writer)
			writeSpecificToFile('Unresolved Pull Requests', unresolved_pull_data, writer)
			writeGeneralToFile('ISSUES', issue_data, writer)
			writeSpecificToFile('Resolved Issues', resolved_issue_data, writer)
			writeSpecificToFile('Unresolved Issues', unresolved_issue_data, writer)
			curr_line = list()
			writer.writerow(['Release/Issue overlap'])
			curr_line.append('Release Names')
			for release in within_range:
				curr_line.append(release[0])
			writer.writerow(curr_line)

			curr_line = list()
			curr_line.append('Release Dates')
			for release in within_range:
				curr_line.append(release[1])
			writer.writerow(curr_line)
		
			curr_line = list()
			curr_line.append('Issues in Release Range')
			for key in within_range:
				curr_line.append(len(within_range[key]))
			writer.writerow(curr_line)
		overall_repo_attributes[repo] = {'release_data': release_data, 
											'branch_data': branch_data, 
											'fork_data': fork_data, 
											'pull_data': pull_data, 
											'resolved_pull_data': resolved_pull_data, 
											'unresolved_pull_data': unresolved_pull_data,
											'issue_data': issue_data,
											'resolved_issue_data': resolved_issue_data,
											'unresolved_issue_data': unresolved_issue_data}
		overall_repo_data[repo] = {'releases': releases, 
											'branchs': branches, 
											'forks': forks, 
											'pulls': pulls, 
											'issues': issues}

	#print(resolved_pull_data[list(resolved_pull_data.keys())[0]])

	#contributors = getPagedAttributes(repo_urls['TRON'], paged_attribute_url_tags['CONTRIBUTORS'])
	#print(contributors) 

	
	#contributor_data = getRepoContributorData(contributors)

if __name__ == '__main__':
	main()




