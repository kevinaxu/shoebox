import os

def main(): 

	# Create an encrypted dmg of size 10mb with the name shoebox
	# with type sparsebundle. Prompt for password from stdin 
	create_dmg = "hdiutil create -megabytes 10 -encryption -stdinpass -type SPARSEBUNDLE -fs HFS+ -volname shoebox shoebox"
	os.system(create_dmg)

	# mount and decrypt the dmg 
	mount_dmg = "hdiutil attach -stdinpass -mountroot PATH shoebox.sparsebundle"
	os.system(mount_dmg)

	# detach 
	detach_dmg = "hdiutil detach /Volumes/shoebox"
	os.system(detach_dmg)
	
if __name__ == '__main__':
    main()
