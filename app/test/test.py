import os
import sys
import app
# from app.gd_app import GDriveClient

# from app.db_app import DropboxClient
#class CloudFileTest(): 
	#def __init__(self):
		#self.temp = "what up" 

def main():
	app = DropboxClient()
	# app.cd("folder1")
	app.ls()
	# app.mv("db-test-file.txt", "temp-folder")

if __name__ == '__main__':
    main()


