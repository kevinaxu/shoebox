Shoebox
=======

The aim of this project is to build an encrypted, remote file system by 
utilizing multiple cloud storage services. Files will be encrypted using 
a one-time pad/key, a technique in which plaintext is paired with a random 
key of equal length. Each bit of the plaintext is encrypted by combining 
it with the corresponding bit from the key to produce the ciphertext. 

Installation
============

Dropbox
-------

Follow along with the Dropbox tutorial to register a new app and install the 
python SDK: 
https://www.dropbox.com/developers/core/start/python

Name your app "shoebox-initials", where initials are the initials of your name. 

Google Drive
------------

Follow along with the Google Drive quickstart guide to create a project and 
enable the Drive API: 
https://developers.google.com/drive/web/quickstart/quickstart-python

Install pydrive using pip: 
	> pip install PyDrive

Install pip if it's not already installed on your system. 


