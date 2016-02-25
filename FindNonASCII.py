import os

def check_for_non_ASCII_chars(file, filedir):
	row = 0
	lines = file.readlines()
	for line in lines:
		row += 1
		col = 0
		for c in line:
			col += 1
			if ord(c) >= 128:
				print(filedir + ": Non-ascii char found at line " + \
				      str(row) + " column " + str(col))
				break


def walk_through_files(dir):
	print("Checking files...")
	for root, dirs, files in os.walk(dir):
		for file in files:
			if file.endswith(".cpp") or file.endswith(".h"):
				f = open(root + '\\'+ file, 'r')
				check_for_non_ASCII_chars(f, root + '\\'+ file)
				f.close()
				
def main():
	walk_through_files(os.getcwd())
	
if __name__ == "__main__":
	main()