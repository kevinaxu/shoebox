import cmd
import shlex
from db_app import DropboxClient
from gd_app import GDriveClient
from otp import OneTimePad

class ShoeboxShell(cmd.Cmd): 

	intro = "Welcome to Shoebox! \nFor more information, enter `help` to list all avaliable commands"
	commands = ["cd", "help", "ls", "mv", "pwd", "mkdir", "rm", "rmdir"]
	e_args = "Error: Incorrect number of arguments"

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.current_path = ''
		self.colors = {'green': '\033[1;32m', 'blue': '\033[1;36m', 'native': '\033[m'}
		self.prompt = self.colors['green'] + "shoebox> " + self.colors['native']

		# Initialize classes 
		self.db = DropboxClient()
		self.gd = GDriveClient()
		self.otp = OneTimePad()

	# TODO: if there is an argument after ls then ls that directory 
	def do_ls(self, args):
		"""list directory contents"""
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

		self.db.cd(path)
		self.gd.cd(path)

	def do_rm(self, args): 
		""" remove directory entries"""
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
		"""move a file or directory"""
		# Don't do more than 2 args 
		if len(args) != 2: 
			self.stdout.write(self.e_args + "\n")

		src_file = args[0]
		tar = args[1]

	def do_cat(self, args): 
		"""view a file"""
		# TODO: Error checking 
		src_file = args[0]

		# Get temporary files containing key and ct values of pt 
		temp_key = db.get(src_file)
		temp_ct = gd.get(src_file)

		temp_pt = otp.decrypt(temp_key, temp_ct)
		print temp_pt.read()
		
		temp_key.close()
		temp_ct.close()
		temp_pt.close()

	def do_mkdir(self, args): 
		"""create a directory"""
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
		
def main():
	ShoeboxShell().cmdloop()

if __name__ == '__main__':
    main()


"""
# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
#APP_KEY = 'lzcu44jy24j1gob'  # GuidoFullAccessApp
#APP_SECRET = 'tdwkh38omie0e26'
"""
