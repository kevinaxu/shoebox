import os 
import ConfigParser 
from os.path import basename, expanduser
import tempfile
from dropbox import client, rest, session

class DropboxClient(): 

	def __init__(self):
		self.colors = {'green': '\033[1;32m', 'blue': '\033[1;36m', 'native': '\033[m'}
		self.current_path = ''

		# Read settings from config file 
		parse = ConfigParser.ConfigParser()
		parse.read("../config/app.ini")
		access_token = parse.get("creds", "dropbox.access_token")
		self.api_client = client.DropboxClient(access_token)

	""" Display the directory and file structure of the remote Dropbox directory """
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

		# Traverse files and either print names or recusively call
		for f in files: 
			count += 1
			f_path = basename(f['path'])
			path = curr_dir + os.sep + f_path
			if f['is_dir']:
				if count == len(files):
					self.show(path, padding + " ")
				else: 
					self.show(path, padding + "|")
			else: 
				print padding + "+-" + f_path

	""" List the contents of the current directory """
	def ls(self): 
		client_path = self.api_client.metadata(self.current_path)

		if 'contents' in client_path:
			for f in client_path['contents']:
				name = basename(f['path'])
				if f['is_dir']: 
					print self.colors['blue'] + name + self.colors['native']
				else: 
					print name 

	# TODO: change from hardcoded "/shoebox" to whatever the user named the directory 
	""" Return the working directory name """
	def pwd(self): 
		print "/shoebox" + self.current_path

	""" Change directory to path """
	def cd(self, path): 
		
		# Check if there is a valid directory named path in the current dir 
		if not self.in_current_dir(path): 
			self.e_path(path)
			return False 

		if path == "..": 
			if self.current_path == '':
				pass
			self.current_path = "/".join(self.current_path.split("/")[0:-1])
		else:
			self.current_path += "/" + path

	""" Check if the path exists in the current directory """
	def in_current_dir(self, path):
		client_path = self.api_client.metadata(self.current_path)

		if 'contents' in client_path:
			for f in client_path['contents']:
				name = basename(f['path'])
				if path == name: 
					return True
		return False 

	""" Move/rename a file or directory """ 
	def mv(self, src_file, target): 

		if not self.in_current_dir(src_file):
			self.e_path(src_file)

		f_metadata = self.api_client.metadata(self.current_path + "/" + target)

		# If the target is a directory, then move the file. 
		# Handle case [mv file ../] accordingly 
		if f_metadata['is_dir']:
			to_file_path = self.current_path + "/" + target
			if target == "../": 
				to_file_path =  "/".join(self.current_path.split("/")[0:-1]) 
			self.api_client.file_move(self.current_path + "/" + src_file,
					to_file_path + "/" + src_file)

		# If it's not a directory, just do a rename 
		else: 
			self.api_client.file_move(self.current_path + "/" + src_file, 
					self.current_path + "/" + target)
					
	""" Make a directory """
	def mkdir(self, dir_path): 
		self.api_client.file_create_folder(self.current_path + "/" + dir_path)

	""" Remove a file/directory entry """
	def rm(self, path): 
		if not self.in_current_dir(path):
			self.e_path(path)
		self.api_client.file_delete(self.current_path + "/" + path)

	""" Copy local file to Dropbox """
	def put(self, src_file, new_file_name): 
		if not self.in_current_dir(src_file):
			self.e_path(src_file)
		from_file = open(expanduser(src_file), "rb") 
		self.api_client.put_file(self.current_path + "/" + new_file_name, from_file) 

	""" Get a file from Dropbox 

		This command returns a descriptor to a temporary file containing
		the contents of the file to get. 
	"""
	def get(self, src_file): 
		temp = tempfile.TemporaryFile()
		f = self.api_client.get_file(self.current_path + "/" + src_file)

		if not f: 
			print "Error: " + src_file + " does not exist in Dropbox."
			return False 

		temp.write(f.read())
		return temp.seek(0)

	""" Error messages """
	def e_path(self, path): 
		print "Error: " + path + " does not exist in current directory."
		return False 


def main():
	db = DropboxClient()
	db.ls()
	db.pwd()
	db.cd("secret-fil")
	db.ls()
	db.pwd()
	



	#db.mv("new-dog.txt", "new-folder1")
	#db.ls()
	#db.cd("new-folder1")
	#print "\n"
	#db.ls()

if __name__ == '__main__':
    main()

