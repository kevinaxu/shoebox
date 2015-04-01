import os
import sys
import tempfile
from os import listdir, sep
from os.path import abspath, basename, isdir
from StringIO import StringIO
from dropbox import client, rest, session

class DropboxClient(): 

	ACCESS_TOKEN = "k6VdpVxf8QEAAAAAAAABe9s-cC-vm5NtlvcfBu53yParxIxK073xU5NjaA9goH92"
	colors = {'green': '\033[1;32m', 
			'blue': '\033[1;36m', 
			'native': '\033[m'
			}
	
	def __init__(self):
		self.temp = "what up" 
		self.api_client = client.DropboxClient(self.ACCESS_TOKEN)

		self.current_path = ''

	def ls(self): 
		client_path = self.api_client.metadata(self.current_path)

		if 'contents' in client_path:
			for f in client_path['contents']:
				name = os.path.basename(f['path'])
				if f['is_dir']: 
					print self.colors['blue'] + name + self.colors['native']
				else: 
					print name 

	def show(self, curr_dir='', padding='  '):

		# Print out the directory name before printing files 
		root = basename(curr_dir)
		if curr_dir == '': 
			root = "shoebox"
		print padding[:-1] + '+-' + root + '/'
		padding = padding + '  '

		# Get all the files in the current directory 
		client_path = self.api_client.metadata(curr_dir)
		files = client_path['contents']
		count = 0

		# Go through each file 
		for f in files: 
			count += 1
			f_path = basename(f['path'])
			path = curr_dir + sep + f_path
			if f['is_dir']:
				if count == len(files):
					self.show(path, padding + " ")
				else: 
					self.show(path, padding + "|")
			else: 
				print padding + "+-" + f_path

	# TODO: change from hardcoded "/shoebox" to whatever the user named the directory 
	def pwd(self): 
		print "/shoebox" + self.current_path

	def cd(self, path): 
		if path == "..": 
			# Don't change directory if we're already at root 
			if self.current_path == '':
				pass
			self.current_path = "/".join(self.current_path.split("/")[0:-1])
			# TODO: expand this line 
		else:
			self.current_path += "/" + path

	def mv(self, src_file, target): 

		f_metadata = self.api_client.metadata(self.current_path + "/" + target)

		# If the target is a directory, then move the file. 
		# Handle case [mv file ../] accordingly 
		if f_metadata['is_dir']:
			to_file_path = self.current_path + "/" + target
			if target == "../": 
				to_file_path =  "/".join(self.current_path.split("/")[0:-1]) 
			self.api_client.file_move(self.current_path + "/" + src_file,
					to_file_path + "/" + os.path.basename(src_file))

		# If it's not a directory, just do a rename 
		else: 
			self.api_client.file_move(self.current_path + "/" + src_file, 
					self.current_path + "/" + target)
					
	def mkdir(self, dir_path): 
		self.api_client.file_create_folder(self.current_path + "/" + dir_path)

	def rm(self, path): 
		self.api_client.file_delete(self.current_path + "/" + path)

	# def do_put(self, from_path, to_path):
	def put(self, src_file, new_file_name): 
		"""
		Copy local file to Dropbox

		Examples:
		Dropbox> put ~/test.txt dropbox-copy-test.txt
		"""
		from_file = open(os.path.expanduser(src_file), "rb")
		self.api_client.put_file(self.current_path + "/" + new_file_name, from_file)
		
		#from_file = open(os.path.expanduser(from_path), "rb")

		#encoding = locale.getdefaultlocale()[1] or 'ascii'
		#full_path = (self.current_path + "/" + to_path).decode(encoding)
		#self.api_client.put_file(full_path, from_file)

	# def cat(self, src_file): 

	""" 
	get is a little bit special. 
	It takes the name of the src_file, and writes to a temporary file
	this is then passed to the shoebox client, which reads from the temporary files
	to reconstruct the file
	"""
	def get(self, src_file): 
		# to_file = open(os.path.expanduser(src_file), "wb")

		temp = tempfile.TemporaryFile()
		f = self.api_client.get_file(self.current_path + "/" + src_file)
		temp.write(f.read())
		temp.seek(0)
		#print temp.read()
		#temp.close()
		return temp

		"""
	def do_get(self, from_path, to_path):
		Copy file from Dropbox to local file and print out the metadata.

		Examples:
		Dropbox> get file.txt ~/dropbox-file.txt
		to_file = open(os.path.expanduser(to_path), "wb")

		f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + from_path)
		#print 'Metadata:', metadata
		#to_file.write(f.read())
		"""

def main():
	db = DropboxClient()
	db.ls()
	print "\n"
	db.put("dog.txt.key", "dog.txt")
	db.ls()

	# db.get("cat.txt")
	# db.put("mycreds.cipher")
	#print "\n"
	#db.ls()
	# db.mv("db-test-file.txt", "temp-folder")

if __name__ == '__main__':
    main()

