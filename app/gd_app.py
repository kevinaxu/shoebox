import os 
import tempfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from apiclient import errors 
from apiclient import http
from apiclient.http import MediaFileUpload

class GDriveClient(): 

	g_apps_folder = "application/vnd.google-apps.folder"
	colors = {'green': '\033[1;32m', 
			'blue': '\033[1;36m', 
			'native': '\033[m'
			}

	def __init__(self):

		# Do all authentication stuff in initialization 
		self.gauth = GoogleAuth()
		self.load_credentials()

		self.drive = GoogleDrive(self.gauth)

		# TODO: Write a method that will save this automatically for new user 
		# Or store this in a config file somewhere...? 
		self.shoebox_id = "0ByFRov07IwByX25CRWZ6Qi1jbzQ"
		self.current_path_name = ''
		self.current_path_id = ''
		self.current_dir_id = ''

	def load_credentials(self): 
		#  Try to load saved client credentials
		self.gauth.LoadCredentialsFile("mycreds.txt")
		if self.gauth.credentials is None:
			# Authenticate if they're not there
			self.gauth.LocalWebserverAuth()
		elif self.gauth.access_token_expired:
			# Refresh them if expired
			self.gauth.Refresh()
		else:
			# Initialize the saved creds
			self.gauth.Authorize()
		# Save the current credentials to a file
		self.gauth.SaveCredentialsFile("mycreds.txt")

	# Auto-iterate through all files in a specific directory 
	# In the current directory? 
	# TODO: Change from using pydrive? 
	def ls(self): 
		page_token = None
		folder_id = self.get_current_dir_id()

		while True:
			try:
				param = {}
				param['q'] = "trashed=false"
				if page_token:
					param['pageToken'] = page_token
				children = self.gauth.service.children().list(folderId=folder_id, **param).execute()

				for child in children.get('items', []):
					# print 'File Id: %s' % child['id']
					# TODO: if this is the only place where get filename is used delete 
					child_name = self.get_filename_from_id(child['id'])
					child_file = self.gauth.service.files().get(fileId=child['id']).execute()
					if child_file['mimeType'] == self.g_apps_folder: 
						print self.colors['blue'] + child_name + self.colors['native']
					else: 
						print child_name

					# print 'File title: %s' % child_name
				page_token = children.get('nextPageToken')
				if not page_token:
					break
			except errors.HttpError, error:
				print 'An error occurred: %s' % error
				break

	def pwd(self): 
		print "/shoebox" + self.current_path_name
		print "/" + self.shoebox_id + self.current_path_id
	
	# TODO: delete this if the only place this is used is in ls 
	def is_dir(self, f): 
		if f['mimeType'] == self.g_apps_folder: 
			return True
		else: 
			return False

	# cd, mv, mkdir, rm, rmdir 
	# path is the actual name of the folder 
	def cd(self, path): 
		if path == "..": 
			if self.current_path_name == '': 
				pass
			# Don't change directory if we're already at root 
			self.current_path_name = "/".join(self.current_path_name.split("/")[0:-1])
			self.current_path_id = "/".join(self.current_path_id.split("/")[0:-1])
		else: 
			folder_id = self.get_id_from_filename(path)
			if folder_id: 
				self.current_path_name += "/" + path 
				self.current_path_id += "/" + folder_id
			else: 
				# THROW AN ACTUAL ERROR 
				print "Not a folder"

	# Make a directory with [folder_name] in the current directory 
	# def mkdir(self, folder_name, parent_id=None): 
	def mkdir(self, folder_name): 
		body = {'title': folder_name, 
				'mimeType': self.g_apps_folder, 
				'parents': [{'id': self.current_dir_id}]
				}
		folder = self.gauth.service.files().insert(body=body).execute() 

	"""
		rename a file
		rename a directory
		move a file to a directory
		move a directory to a directory 

		input: 
			src_file: name of a file/dir
			target: name of a file/dir 
	"""
	def mv(self, src_file, target): 

		# To rename a file, first retrieve and then update the content 
		file_id = self.get_id_from_filename(src_file)
		f_resource = self.gauth.service.files().get(fileId=file_id).execute()
		f_resource['title'] = target
		updated_metadata = self.gauth.service.files().update(fileId=file_id, body=f_resource).execute()
		if not updated_metadata: 
			print "update failed"
		else: 
			print "update success"

	# Find the id of the file/directory in the current directory 
	# Do a query where the parent is 
	def get_id_from_filename(self, file_name): 

		parent_id = self.get_current_dir_id()

		q_str = {'q': "title='%s' and '%s' in parents" 
				% (file_name, parent_id)}
		return_fields = "items(id, title, parents)"
		f_metadata = self.gauth.service.files().list(fields=return_fields, **q_str).execute()
		
		if f_metadata['items']: 
			return f_metadata['items'][0]['id']
		else: 
			return False 

	# TODO: Limit the amount of metadata returned from 
	def get_filename_from_id(self, file_id):
			file_obj = self.gauth.service.files().get(fileId=file_id).execute()
			return file_obj['title']
	
	def get_current_dir_id(self): 
		if self.current_path_name == '': 
			return self.shoebox_id
		else: 
			return os.path.basename(self.current_path_id)

	def put(self, src_file, new_file_name):
		media_body = MediaFileUpload(src_file, mimetype="text/plain", resumable=True)
		body = {'title': new_file_name,
				'mimeType': 'text/plain',
				'parents': [{'id': self.shoebox_id}]
				}
		folder = self.gauth.service.files().insert(body=body, media_body=media_body).execute() 

	"""Print a file's content.

	Args:
		service: Drive API service instance.
		file_id: ID of the file.

	Returns:
		File's content if successful, None otherwise.
	"""
	def print_file_content(self):
		file_id = "0ByFRov07IwBySGhBMFZ5cHlEdVU"
		try:
			print self.gauth.service.files().get_media(fileId=file_id).execute()
		except errors.HttpError, error:
			print 'An error occurred: %s' % error
	
	def get(self, src_file): 

		# Get the file contents and write them to the temporary file 
		file_id = "0ByFRov07IwByd3E4NV80alhGMzg"
		file_contents = self.gauth.service.files().get_media(fileId=file_id).execute()

		temp = tempfile.TemporaryFile()
		temp.write(file_contents) 
		temp.seek(0)
		return temp 


def main():
	gd = GDriveClient()
	gd.ls()
	gd.mv("new-new-folder", "old-folder")
	print "\n"
	gd.ls()


if __name__ == '__main__':
    main()


"""
textfile = drive.CreateFile()
textfile.SetContentFile('test-creds.txt')
textfile.Upload()
print textfile

drive.CreateFile({'id':textfile['id']}).GetContentFile('test-creds-dl.txt')

shoebox_id = "0ByFRov07IwByX25CRWZ6Qi1jbzQ"
file_id = "0ByFRov07IwByRlAtODJpVTY1Vnc"
curr_dir = shoebox_id
dest_dir = {'id': "0ByFRov07IwByeVJza1VjZlpQczQ"}

# Create a directory in a specific folder 
folder_name = "new-new-folder"
folder_id = create_dir(gauth.service, folder_name, shoebox_id)
print folder_id 


f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": shoebox_id}]})
f.SetContentFile("mycreds.txt")
f.Upload()

# Move a file to another folder 
def move_file(service, file_id, current_dir_id, dest_dir_id): 
	dest_dir = {'id': dest_dir_id}
	try: 
		# Delete the old parent id 
		service.parents().delete(fileId=file_id, parentId=curr_dir).execute()

		# Insert the new parent id 
		service.parents().insert(fileId=file_id, body=dest_dir).execute()
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

"""

