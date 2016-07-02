import os
import sys 
import tempfile
import ConfigParser

class OneTimePad(): 

    def __init__(self):
        # Read settings from config file 
        parse = ConfigParser.ConfigParser()
        parse.read("config/app.ini")

        self.block_size = int(parse.get("settings", "otp.block_size"))
        self.prng       = parse.get("settings", "otp.prng")

    """
    Given a filename, return the filesize
    """
    def get_filesize(self, fd):
        fd.seek(0, 2)
        n = fd.tell()
        fd.seek(0, 0)
        return n 

    """
    Encrypt takes the name of the plaintext file to encrypt 
    and the name of the ciphertext. It creates a padfile, 
    processes them to get the resulting ciphertext. 
    The padfile and ciphertext in the form of temporary, named
    file descriptors, are returned as a tuple. 
    """
    def encrypt(self, temp_plain_file):
        temp_plain_file.seek(0)

        # TODO: only need to pass in file size here 
        temp_key = self.generate_padfile(temp_plain_file)
        temp_ct = self.process(temp_plain_file, temp_key)
        return (temp_key, temp_ct)

    """
    Given a filename, return a temporary named padfile. 
    This padfile will be a non-readable binary file. 
    """
    def generate_padfile(self, plain_file): 

        temp_key = tempfile.NamedTemporaryFile()
        size = self.get_filesize(plain_file)
        block_size = self.block_size 

        while size > 0: 
            rand_fd = open(self.prng, 'r')
            block = rand_fd.read(min(block_size, size))
            temp_key.write(block)
            size = size - len(block)

        temp_key.seek(0)
        return temp_key 

        
    """
    Decrypt behavior is a little bit strange. 
    Takes multiple open temporary files 
    """
    def decrypt(self, plain_file, key, ciphertext): 
        return self.process(ciphertext, key)

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
    def process(self, in_file, pad_file): 
        temp_out_file = tempfile.NamedTemporaryFile()
        while True: 
            block_size = self.block_size
            #print "block size: " + self.block_size
            #print "2 block size: " + block_size
            data = in_file.read(self.block_size)
            if not data: 
                break
            pad = pad_file.read(len(data))
            encoded = ''.join([chr(ord(a) ^ ord(b)) for a, b in zip(data, pad)])
            temp_out_file.write(encoded)
        temp_out_file.seek(0)
        pad_file.seek(0)
        return temp_out_file

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
