import csv

def writeToFile(data, file_writer):
	file_writer.writerow([data])


def main():

	with open('test_file.csv', 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writeToFile('x', writer)
		writeToFile('z', writer)


if __name__ == '__main__':
	main()


