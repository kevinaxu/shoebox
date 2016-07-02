import tempfile
import json
import httplib2
from apiclient import discovery, errors
from apiclient.http import MediaFileUpload
from oauth2client import client

class GDriveClient(): 

    def __init__(self, client_secrets):

        # Oauth stuff here 
        credentials = client.OAuth2Credentials.from_json(client_secrets)
        http_auth = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v2', http_auth)

        # TODO: this is a constant (and only gets used in two places)
        self.g_apps_folder = "application/vnd.google-apps.folder"

        # Initialize the application folder if doesn't exist 
        self.app_folder_name = 'shoebox-serenbe'
        self.parent_id = self.app_folder_exists()
        if not self.parent_id: 
            self.parent_id = self.init_shoebox()


    """ return parent id of app_folder if exists, False otherwise """
    def app_folder_exists(self): 
        q = {'q': "title='%s' and trashed=false" % (self.app_folder_name)}
        results = self.service.files().list(fields="items(id, title)", **q).execute()
        items = results.get('items', [])
        if items: 
            return items[0]['id']
        else: 
            return False

    """ creates the application folder that all files will be uploaded to"""
    def init_shoebox(self): 
        file_metadata = {
            'title' : 'shoebox-serenbe',
            'mimeType' : self.g_apps_folder
        }
        file = self.service.files().insert(body=file_metadata, fields='id').execute()
        return file.get('id')

    """ List the contents of the current directory """
    def ls(self): 
        result = []
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                files = self.service.children().list(folderId=self.parent_id, **param).execute()
                #files = self.service.files().list(**param).execute()
                print "printing files here\n"
                print files 

                result.extend(files['items'])
                page_token = files.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break
        return result

    """ Remove a file/directory entry """
    def rm(self, src_file):
        file_id = self.get_id_from_filename(src_file)
        self.service.files().delete(fileId=file_id).execute()

    """ Copy local file to Google Drive """
    def put(self, src_file, new_file_name):
        media_body = MediaFileUpload(src_file, mimetype="text/plain", resumable=True)
        body = {'title': new_file_name,
                'mimeType': 'text/plain',
                'parents': [{'id': self.parent_id}]
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


    def print_files(self): 
        results = self.service.files().list(maxResults=10).execute()
        items = results.get('items', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['title'], item['id']))

    """ Find the id of the file in the current directory """
    def get_id_from_filename(self, file_name): 

        parent_id = self.get_current_dir_id()

        q = {'q': "title='%s' and '%s' in parents and trashed=false" % (file_name, parent_id)}
        result = self.service.files().list(fields="items(id, title)", **q).execute()
        
        if result['items']: 
            return result['items'][0]['id']
        else: 
            return False 

    def mkdir(self, folder_name): 
        body = {'title': folder_name, 
                'mimeType': self.g_apps_folder, 
                'parents': [{'id': self.get_current_dir_id()}]
                }
        self.service.files().insert(body=body).execute() 

    """ Return the name of the file in the current dir with the given id """
    def get_filename_from_id(self, file_id):
        file_obj = self.service.files().get(fields="items(id, title)", fileId=file_id).execute()
        return file_ob
        #return file_obj['title']


def main():
    creds = '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/drive.file"], "token_expiry": "2016-06-22T04:31:36Z", "id_token": null, "access_token": "ya29.Ci8JA0rOBx8wZBqNR2vEB4eM2GrIPpVKFnoHSYiQh_vg65OlpmEx6HOK7q_c0R7qNw", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.Ci8JA0rOBx8wZBqNR2vEB4eM2GrIPpVKFnoHSYiQh_vg65OlpmEx6HOK7q_c0R7qNw", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/uZKRyZQCX_BtHhpnmM2_7TzFF05ZUOd_xhdl3birNaE"}, "client_id": "153627018216-kqg9ovhjhe5ncct4mugacg6touga03fs.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", "client_secret": "4LBUkuc2LJDBEicAAANsxKo6", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/uZKRyZQCX_BtHhpnmM2_7TzFF05ZUOd_xhdl3birNaE", "user_agent": null}'
    gd = GDriveClient(creds)
    #a = gd.get_filename_from_id('0BzhLT2JJSlzMVmpIQmQ4azcxdm8')
    #print "filename: " + a
    #gd.ls()
    #gd.put('/Users/kxu/Desktop/test_file.txt', 'new-test-file.txt')
    #def put(self, src_file, new_file_name):

if __name__ == '__main__':
    main()
