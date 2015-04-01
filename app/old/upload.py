#!/usr/bin/python
import ConfigParser
import dropbox
import httplib2
import pprint
import os 
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

# Read credentials from the config file 
parse = ConfigParser.ConfigParser()
parse.read('../config/app.ini')
dropbox_id		= parse.get('creds', 'dropbox.id')
dropbox_secret	= parse.get('creds', 'dropbox.secret')
gd_id		= parse.get('creds', 'drive.id')
gd_secret	= parse.get('creds', 'drive.secret')

# Read in the file to upload 
file_name = raw_input("Enter the name of the file to upload to drive and dropbox: ").strip()

################################################
# GOOGLE DRIVE  
################################################

"""
# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.file' 

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Run through the OAuth flow and retrieve credentials
gd_flow = OAuth2WebServerFlow(gd_id, gd_secret, OAUTH_SCOPE, redirect_uri=REDIRECT_URI)
gd_authorize_url = gd_flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + gd_authorize_url
gd_code = raw_input('Enter verification code: ').strip()
credentials = gd_flow.step2_exchange(gd_code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

gd_service = build('drive', 'v2', http=http)

# Insert a file
media_body = MediaFileUpload(file_name, mimetype='text/plain', resumable=True)
body = {
		  'title': file_name,
		    'description': 'A test document',
			  'mimeType': 'text/plain'
			  }
file = gd_service.files().insert(body=body, media_body=media_body).execute()
pprint.pprint(file)
"""


################################################
# DROPBOX 
################################################

access_token = "k6VdpVxf8QEAAAAAAAABe9s-cC-vm5NtlvcfBu53yParxIxK073xU5NjaA9goH92"

"""
db_flow = dropbox.client.DropboxOAuth2FlowNoRedirect(dropbox_id, dropbox_secret)

# Generate an authorization URL
# Have the user sign in and authorize this token. 
# In a real world app, you want to automatically send the user to an authorization
# URL and pass a callback URL so the user is automatically redirected to your app
# after pressing a button
db_authorize_url = db_flow.start()
print '1. Go to: ' + db_authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
db_code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code 
access_token, user_id = db_flow.finish(db_code)
print access_token
"""
# Test access to the Core API - this should show info about the user's 
# linked account
db_client = dropbox.client.DropboxClient(access_token)
print 'linked account: ', db_client.account_info() 

# Uploading a file 
db_file = open(file_name, 'rb')
db_response = db_client.put_file("/" + file_name, db_file)
print "uploaded:", db_response


