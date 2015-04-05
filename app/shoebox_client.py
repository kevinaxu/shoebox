import sys
import os 
from os.path import abspath, join, isfile 
from db_app import DropboxClient
from gd_app import GDriveClient
from shell import ShoeboxShell
from otp import OneTimePad

def main():
	usage = (
		"Usage:\n\n"
		"Bring up a minimal shell to browse/manipulate uploaded files: \n"
		"	python shoebox.py shell\n"
		"Display the remote Shoebox directory tree: \n"
		"	python shoebox.py show\n"
		"Upload a file: \n"
		"	python shoebox.py upload file\n"
		"	python shoebox.py upload dir\n"
		"Download a file: \n"
		"	python shoebox.py download file"
		)
	
	all_commands = ["upload", "download", "shell", "show"]

	# Parse the arguments. If no command was specified, then return help 
	args = list(sys.argv)
	if len(args) != 2:
		print "Error: Invalid number of arguments\n"
		print usage 

	command = args[1].lower()
	if command not in all_commands: 
		print "Error: Invalid command\n"
		print usage 

	if command == "upload": 

		# Print out all files in the uploads folder 
		sbox_path = abspath(join(os.getcwd(), os.pardir))
		uploads = sbox_path + "/uploads"
		files_to_upload = [f for f in os.listdir(uploads) if isfile(join(uploads, f))]
		for f in files_to_upload:
			print uploads + "/" + f 
			# sbox_upload(uploads + "/" + f)

	elif command == "download": 
		sbox_download(pt)
	elif command == "show": 
		DropboxClient().show()
	else: 
		ShoeboxShell().cmdloop()


#TODO: Check if that is a valid file in the CURRENT DIRECTORY
"""	Upload a file to Shoebox 

	This function calls the generate_padfile function in the otp class to
	generate a one time pad with the same length as the plaintext file. 
	It then encrypts the plaintext using the pad to create the ciphertext. 
	
	The key is then pushed to Dropbox, while the ciphertext is pushed
	to Google Drive. All intermediate data is stored as named temporary files,
	which are automatically deleted on close. 
"""
def sbox_upload(file_name):
	
	(db, gd, otp) = create_classes()
	temp_key, temp_ct = otp.encrypt(file_name)

	db.put(temp_key.name, pt)
	gd.put(temp_ct.name, pt)

	db.ls()
	gd.ls()

	temp_key.close()
	temp_ct.close()


""" Download a file from Shoebox. 

	The function gets the file's key and ciphertext from Dropbox and 
	Google Drive and stores the contents in temporary files. These files
	are decrypted and saved in the encrypted file disk. 

	NOTE: This doesn't save anything right now 
"""
def sbox_download(file_name):
	(db, gd, otp) = create_classes()

	temp_key = db.get(file_name)
	temp_ct = gd.get(file_name)
	temp_pt = otp.decrypt(temp_key, temp_ct)
	#print temp_pt.read()
	
	temp_key.close()
	temp_ct.close()
	temp_pt.close()

def create_classes(): 
	return (DropboxClient(), GDriveClient(), OneTimePad())

if __name__ == '__main__':
    main()
