#! /usr/bin/env python
# tree.py

from os import listdir, sep
from os.path import abspath, basename, isdir
from sys import argv

def tree(dir, padding, print_files=False):
	# Print the directory name 
	print padding[:-1] + '+-' + basename(abspath(dir)) + '/'
	padding = padding + ' '
	#files = []

	# Get all the files 
	#if print_files:
	files = listdir(dir)
   # else:
	  #  files = [x for x in listdir(dir) if isdir(dir + sep + x)]
	count = 0

	# Print the file
	# If it's a directory, then recursively call tree 
	for file in files:
		count += 1
		print padding + '|'
		path = dir + sep + file
		if isdir(path):
			if count == len(files):
				tree(path, padding + ' ', print_files)
			else:
				tree(path, padding + '|', print_files)
		else:
			print padding + '+-' + file

def main():
	# Always print files as well as directories 
	path = argv[1]
	if isdir(path):
		tree("./", ' ', True)
	else:
		print 'ERROR: \'' + path + '\' is not a directory'

if __name__ == '__main__':
	main()

