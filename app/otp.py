import os
import sys 

class OneTimePad(): 

	def __init__(self):
		self.block_size = 65536
		self.prng = "/dev/urandom"

	# Given a filename, return the filesize
	def get_filesize(self, file_name):
		with open(file_name, 'r') as fd: 
			fd.seek(0, 2)
			n = fd.tell()
			fd.seek(0, 0)
			return n 

	# Given a file, create a padfile of the same length 
	# Padfile will be non-readable binary file. Not a plaintext file 
	def generate_padfile(self, plain_file, pad_file): 

		# Get the size of the plaintext file 
		size = self.get_filesize(plain_file)

		# Create the padfile 
		with open(pad_file, 'w') as otp: 

			# random = self.random
			block_size = self.block_size 
			while size > 0: 
				# Read random bytes from whatever the prng is 
				rand_fd = open(self.prng, 'r')
				block = rand_fd.read(min(block_size, size))
				otp.write(block)
				size = size - len(block)

	def encrypt(self, plain_file, pad_file, cipher_file): 
		with open(pad_file, 'r') as padfile: 
			with open(plain_file, 'r') as textfile:
				with open(cipher_file, 'w') as cipherfile: 
					self.process(textfile, cipherfile, padfile)

	#def encrypt(self, plain_file, pad_file, cipher_file): 
		#with open(pad_file, 'r') as padfile: 
			#with open(plain_file, 'r') as textfile:
				## Check fi the sizes are the same? 
				#with open(cipher_file, 'w') as cipherfile: 
					#self.process(textfile, cipherfile, padfile)
		
	"""
	Decrypt behavior is a little bit strange. 
	Takes multiple open temporary files 
	"""
	def decrypt(self, plain_file, key, ciphertext): 
		with open(plain_file, 'w') as textfile: 
			self.process(ciphertext, textfile, key)

	#def decrypt(self, plain_file, pad_file, cipher_file): 
		#with open(pad_file, 'r') as padfile: 
			#with open(cipher_file, 'r') as cipherfile: 
				#with open(plain_file, 'w') as textfile: 
					#self.process(cipherfile, textfile, padfile)

	# Takes three file descriptors. Reads from the input file and the pad file 
	# and writes to the output file 
	# 
	# HOW IT WORKS: 
	# zip takes the iterables a and b and then creates an iterator of tuples, 
	#	where the ith tuple contains the ith element of each arg a and b 
	# 
	# ord(i) converts a single character to its corresponding ASCII value 
	# chr(i) returns the string representing a character whose Unicode codepoint is i
	# 
	# Basically, each corresponding byte of the two files are converted into their 
	# ascii values, which are then bitwise XORed and converted back into string form. 
	# Each of these new bytes is appended to the final processed string and written to file. 
	def process(self, in_file, out_file, pad_file): 
		while True: 
			data = in_file.read(self.block_size)
			if not data: 
				break
			pad = pad_file.read(len(data))
			encoded = ''.join([chr(ord(a) ^ ord(b)) for a, b in zip(data, pad)])
			out_file.write(encoded)

def main():
	pt = "dog.txt"
	ct = "mycreds.cipher"
	key_file = "mycreds-padfile.txt"

	otp = OneTimePad()
	# otp.generate_padfile(pt, key_file)
	otp.encrypt(pt, key_file, ct)

	# otp.encrypt(pt, key_file, ct)
	# otp.decrypt("mycreds.decrypt", key_file, ct)

if __name__ == '__main__':
    main()
