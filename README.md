Shoebox
=======

The aim of this project is to build an encrypted, remote file system by 
utilizing multiple cloud storage services. Files will be encrypted using 
a one-time pad/key, a technique in which plaintext is paired with a random 
key of equal length. Each bit of the plaintext is encrypted by combining 
it with the corresponding bit from the key to produce the ciphertext. 

Installation
============

To install locally, install virtualenv and run the following commands 

```sh
venv && source venv/bin/activate
pip -r install requirements.txt
flask initdb
flask run
```
