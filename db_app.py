import os 
from os.path import basename, expanduser
import tempfile
from dropbox import client

# TODO: error handling!
class DropboxClient(): 

    def __init__(self, access_token):
        self.api_client = client.DropboxClient(access_token)

    """ Copy local file to Dropbox """
    def put(self, src_file, new_file_name): 
        from_file = open(expanduser(src_file), "rb") 
        return self.api_client.put_file(new_file_name, from_file) 

    """ Remove a file/directory entry """
    def rm(self, file_name): 
        self.api_client.file_delete(file_name)

    """ List the contents of the current directory """
    def ls(self): 
        client_path = self.api_client.metadata('/')
        files = []
        if 'contents' in client_path:
            for f in client_path['contents']:
                files.append(basename(f['path']))
        return files

    """ Get a file from Dropbox 
        This command returns a descriptor to a temporary file containing
        the contents of the file to get. 
    """
    def get(self, src_file): 
        temp = tempfile.TemporaryFile()
        f = self.api_client.get_file(src_file)
        if not f: 
            print "Error: " + src_file + " does not exist in Dropbox."
            return False 
        temp.write(f.read())
        return temp.seek(0)

def main():
    access_token = 'k6VdpVxf8QEAAAAAAAAF4YjTB_5p_Hro0pAn0xhBLLdhRPoWy_zW26vejEHEnXS6'
    db = DropboxClient(access_token)
    #db.ls()
    print db.api_client.metadata('/')
    #db.rm('new_file')

if __name__ == '__main__':
    main()

