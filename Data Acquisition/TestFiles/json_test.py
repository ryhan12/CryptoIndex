from github import Github
import os
import requests
import json
import iso8601
import datetime
import xlwt
import csv

now = datetime.datetime.now()
with open('test.csv', 'w', newline='') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|')
	spamwriter.writerow([1, 2, 3, 4] + [5, 6, 7])
	spamwriter.writerow([])


"""
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
fork_data['Latest_Fork'] = fork_data['Latest_Fork']['full_name']
fork_data['First_Fork'] = fork_data['First_Fork']['full_name']
pull_data['Oldest_Unresolved_Pull_Req'] = pull_data['Oldest_Unresolved_Pull_Req']['created_at']

print(type(fork_data['First_Fork']))
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
"""