import tempfile
from os.path import basename
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from apiclient.http import MediaFileUpload

class GDriveClient(): 

	def __init__(self):

		# Abbreviate API calls 
		self.gauth = GoogleAuth()
		self.service = GoogleAuth().service

		self.g_apps_folder = "application/vnd.google-apps.folder"
		self.colors = {'green': '\033[1;32m', 'blue': '\033[1;36m', 'native': '\033[m'}

		# TODO: Write a function that will do this automatically 
		self.shoebox_id = "0ByFRov07IwByX25CRWZ6Qi1jbzQ"

		# Keep track of the directory structure 
		self.current_path_name = ''
		self.current_path_id = ''

		# Load credentials from the config file 
		self.creds = "../config/mycreds.txt"
		self.load_credentials()

	"""
	Look for credentials in config folder
	Authenticate if they're not there, and save to file for later verification
	"""
	def load_credentials(self): 
		self.gauth.LoadCredentialsFile(self.creds)
		if self.gauth.credentials is None:
			self.gauth.LocalWebserverAuth()
		elif self.gauth.access_token_expired:
			self.gauth.Refresh()
		else:
			self.gauth.Authorize()
		self.gauth.SaveCredentialsFile(self.creds)

	""" List the contents of the current directory """
	def ls(self): 
		page_token = None
		folder_id = self.get_current_dir_id()

		while True:
			param = {}
			param['q'] = "trashed=false"
			if page_token:
				param['pageToken'] = page_token
			children = self.service.children().list(folderId=folder_id, **param).execute()

			for child in children.get('items', []):
				c_id = child['id']
				
				child_name = self.get_filename_from_id(c_id)
				child_file = self.service.files().get(fileId=c_id).execute()
				if child_file['mimeType'] == self.g_apps_folder: 
					#print self.colors['blue'] + child_name + " " + c_id + self.colors['native']
					print self.colors['blue'] + child_name + self.colors['native']
				else: 
					#print child_name + " " + c_id
					print child_name

			page_token = children.get('nextPageToken')
			if not page_token:
				break

	""" Return the working directory name """
	# TODO: Change the shoebox to whatever the user named the project dir
	def pwd(self): 
		print "/shoebox" + self.current_path_name
		print "/" + self.shoebox_id + self.current_path_id

	""" Change directory to path """
	def cd(self, path): 
		if path == "..": 
			if self.current_path_name == '': 
				pass
			self.current_path_name = "/".join(self.current_path_name.split("/")[0:-1])
			self.current_path_id = "/".join(self.current_path_id.split("/")[0:-1])
		else: 
			folder_id = self.get_id_from_filename(path)
			if folder_id: 
				self.current_path_name += "/" + path 
				self.current_path_id += "/" + folder_id
			# THROW AN ACTUAL ERROR 
			#else: 
				#print "Not a folder"

	""" Move/rename a file or directory 

		Cases (assume src_file exists):
			Target doesn't exist, then just do a rename
			Target exists and is a file, then ERROR
			Target exists and is a dir, then do a move 
	"""
	def mv(self, src_file, target): 

		# Get the ID of the src_file and the target 
		src_file_id = self.get_id_from_filename(src_file)
		if not src_file_id: 
			print "Error: Source file does not exist"
			return False 

		target_id = self.get_id_from_filename(target)
		curr_dir_id = self.get_current_dir_id()

		if target_id: 

			target_dir = self.service.files().get(fileId=target_id).execute()
			if target_dir['mimeType'] == self.g_apps_folder:

				self.service.parents().delete(fileId=src_file_id, parentId=curr_dir_id).execute()
				body = {'id': target_id}
				self.service.parents().insert(fileId=src_file_id, body=body).execute()
				# print "Moved " + src_file + " to " + target
			#else: 
				#print "Error. File already exists"

			print target_id 
		elif target == "../": 
			print 1 
			#Delete the old parent id of the src file 
			self.service.parents().delete(fileId=src_file_id, parentId=curr_dir_id).execute()

			parent_id = basename("/".join(self.current_path_id.split("/")[0:-1]))
			if not parent_id: 
				parent_id = self.shoebox_id 
				
			body = {'id': parent_id}
			self.service.parents().insert(fileId=src_file_id, body=body).execute()
			print "Moved " + src_file + " to " + self.get_filename_from_id(parent_id)
		else: 

			print 3 
			# To rename a file, first retrieve and then update the content 
			result = self.service.files().get(fileId=src_file_id).execute()
			result['title'] = target
			updated_metadata = self.service.files().update(fileId=src_file_id, body=result).execute()
			if not updated_metadata: 
				print "update failed"
			else: 
				print "update success"

	""" Make a directory """
	def mkdir(self, folder_name): 
		body = {'title': folder_name, 
				'mimeType': self.g_apps_folder, 
				'parents': [{'id': self.get_current_dir_id()}]
				}
		self.service.files().insert(body=body).execute() 

	""" Remove a file/directory entry """
	def rm(self, src_file):
		file_id = self.get_id_from_filename(src_file)
		self.service.files().delete(fileId=file_id).execute()

	""" Copy local file to Google Drive """
	def put(self, src_file, new_file_name):
		media_body = MediaFileUpload(src_file, mimetype="text/plain", resumable=True)
		body = {'title': new_file_name,
				'mimeType': 'text/plain',
				'parents': [{'id': self.shoebox_id}]
				}
		folder = self.service.files().insert(body=body, media_body=media_body).execute() 
	
	""" Get a file from Google Drive

		This command returns a descriptor to a temporary file containing
		the contents of the file to get. 
	"""
	def get(self, src_file): 
		file_id = self.get_id_from_filename(src_file)
		contents = self.service.files().get_media(fileId=file_id).execute()

		temp = tempfile.TemporaryFile()
		temp.write(contents) 
		return temp.seek(0)

	""" Find the id of the file in the current directory """
	def get_id_from_filename(self, file_name): 

		parent_id = self.get_current_dir_id()

		q = {'q': "title='%s' and '%s' in parents and trashed=false" % (file_name, parent_id)}
		result = self.service.files().list(fields="items(id, title)", **q).execute()
		
		if result['items']: 
			return result['items'][0]['id']
		else: 
			return False 

	""" Return the name of the file in the current dir with the given id """
	def get_filename_from_id(self, file_id):
		file_obj = self.service.files().get(fields="items(title)", fileId=file_id).execute()
		return file_obj['title']
	
	""" Get the id of the current directory """
	def get_current_dir_id(self): 
		if self.current_path_name == '': 
			return self.shoebox_id
		else: 
			return basename(self.current_path_id)


def main():
	gd = GDriveClient()

	gd.ls()
	gd.cd("folder1")
	print "\n"
	gd.ls()
	gd.cd("folder3")
	print "\n"
	gd.ls()

	gd.mv("folder4", "../")
	gd.cd("..")
	print "\n"
	gd.ls()
	

if __name__ == '__main__':
    main()

"""
old shit 
"""
