#!/usr/bin/env python

import cmd
import locale
import os
import pprint
import shlex
import sys
import optparse 
import tempfile
from StringIO import StringIO
from dropbox import client, rest, session

# Import from local files 
from db_app import DropboxClient
from gd_app import GDriveClient
from otp import OneTimePad

class ShoeboxShell(cmd.Cmd): 

	intro = "Welcome to Shoebox! \nFor more information, enter `help` to list all avaliable commands"
	green = '\033[1;32m'
	blue = '\033[1;36m'
	native = '\033[m'
	commands = ["cd", "help", "ls", "mv", "pwd", "mkdir", "rm", "rmdir"]
	e_args = "Error: Incorrect number of arguments"

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.current_path = ''
		self.prompt = self.green + "shoebox> " + self.native 
		self.db = DropboxClient()
		self.gd = GDriveClient()

		# self.api_client = client.DropboxClient(self.ACCESS_TOKEN)

	# TODO: if there is an argument after ls then ls that directory 
	def do_ls(self, args):
		"""
		list directory contents

		Examples:
		shoebox> ls [dir]
		"""
		self.db.ls()

	def do_pwd(self, args): 
		"""return the current directory path"""
		print "/shoebox" + self.current_path

	# TODO: fix errors of cd into a direcotry that is not there 
	def do_cd(self, args):
		"""change current working directory"""
		if len(args) != 1: 
			self.stdout.write(self.e_args + "\n")

		path = args[0] 

		# TODO: Error checking if the directory does not exist/not a directory 
		self.db.cd(path)
		self.gd.cd(path)

	def do_rm(self, args): 
		""" 
		remove directory entries
		"""
		if self.db.is_dir(path): 
			confirm = raw_input("Deleting this directory will also remove all file contents. Proceed? (y/n)").strip()
			if confirm == 'y':
				self.db.rm(path)
				self.gd.rm(path)

	
	def do_rmdir(self, args): 

		# prompt the user to confirm deleting directory 
		confirm = raw_input("Deleting this directory will also remove all file contents. Proceed? (y/n)").strip()
		if confirm.lower() == "y":
			db.rm(f)

	def do_mv(self, args): 
		# Don't do more than 2 args 
		if len(args) != 2: 
			self.stdout.write(self.e_args + "\n")

		src_file = args[0]
		tar = args[1]

   # def do_cat(self, args): 
		#src_file = args[0]
	#@command()
	#def do_cat(self, path):
		#"""display the contents of a file"""
		#f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + path)
		#self.stdout.write(f.read())
		#self.stdout.write("\n")

	def do_mkdir(self, args): 
		"""make directories"""
		print "hello what up"

	def do_help(self, args): 
		for command in self.commands: 
			f = getattr(self, "do_" + command)
			if f.__doc__: 
				self.stdout.write('%s: %s\n' % (command, f.__doc__))

	# command line stuff 
	def do_exit(self):
		return True

	def emptyline(self):
		pass

	def do_EOF(self, line):
		self.stdout.write('\n')
		return True

	def parseline(self, line):
		parts = shlex.split(line)
		if len(parts) == 0:
			return None, None, line
		else:
			#print parts 
			#print line 
			return parts[0], parts[1:], line
		
"""
python shoebox_client.py shell
python shoebox_client.py upload 
python shoebox_client.py download 
"""
def arg_handler(shoebox): 
	all_commands = ["upload", "download", "shell", "show"]

	usage = (
		"\n\n"
		"Bring up a minimal shell to browse/manipulate uploaded files: \n"
		"	python shoebox.py shell\n"
		"Upload a file: \n"
		"	python shoebox.py upload file\n"
		"	python shoebox.py upload dir\n"
		"Download a file: \n"
		"	python shoebox.py download file\n"
		)
	
	parser = optparse.OptionParser(usage=usage)
	options, args = parser.parse_args()

	# Parse the arguments. If no command was specified, then return help 
	args = list(sys.argv)
	if len(args) == 1:
		args = args + [ '--help' ]
	options, args = parser.parse_args(args)

	# Check that the command is present 
	# TODO: Not print the usage everytime you submit a bad command 
	command = args[1].lower()
	if command not in all_commands: 
		parser.error("invalid command")

	# TODO: update this now that show command is added 
	#if command != "shell" and len(args) < 3: 
		#parser.error("did not specify files to " + command)

	# List of all files to be uploaded/downloaded 
	all_files = args[2:]
	pt	= "dog.txt"
	key = pt + ".key"
	ct	= pt + ".ct"

	""" 
	Takes a file (Ex. cat.txt, cat)
	Generate a one time pad for that file -> name it file.key
	Encrypt the file to get the ciphertext -> file.ct 
	Create an instance of Dropbox and Drive
	Upload the the key to dropbox and the cipher to drive 
	Delete the local file, key, and ciphertext 

	Takes a file (Ex. cat.txt)
	Create a temporary file that will hold the one time pad 
	Create a temporary file that will hold the results of the encryption 
	"""
	otp = OneTimePad()
	db = DropboxClient()
	gd = GDriveClient()
	if command == "upload": 
		#TODO: Check if that is a valid file in the CURRENT DIRECTORY
		#TODO: Change this so that the padfile that is creatd is a temporary file 

		temp_key, temp_ct = otp.encrypt(pt, key)
	
		db.put(temp_key.name, pt)
		gd.put(temp_ct.name, pt)

		db.ls()
		gd.ls()

		temp_key.close()
		temp_ct.close()
	elif command == "download": 
		# Get temporary files containing key and ct values of pt 
		temp_key = db.get(pt)
		temp_ct = gd.get(pt)

		temp_pt = otp.decrypt(temp_key, temp_ct)
		#print temp_pt.read()
		
		temp_key.close()
		temp_ct.close()
		temp_pt.close()
	elif command == "show": 
		db.show()
	else: 
		shoebox.cmdloop()

def main():
	shoebox = ShoeboxShell()
	arg_handler(shoebox)

if __name__ == '__main__':
    main()







"""
# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
#APP_KEY = 'lzcu44jy24j1gob'  # GuidoFullAccessApp
#APP_SECRET = 'tdwkh38omie0e26'

def command(login_required=True):
    # a decorator for handling authentication and exceptions
    def decorate(f):
        def wrapper(self, args):
            if login_required and self.api_client is None:
                self.stdout.write("Please 'login' to execute this command\n")
                return

            try:
                return f(self, *args)
            except TypeError, e:
                self.stdout.write(str(e) + '\n')
            except rest.ErrorResponse, e:
                msg = e.user_error_msg or str(e)
                self.stdout.write('Error: %s\n' % msg)

        wrapper.__doc__ = f.__doc__
        return wrapper
    return decorate
"""

