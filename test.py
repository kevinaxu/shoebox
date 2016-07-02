import json 
from pprint import pprint

def main():
    with open('file.json') as data_file: 
        json_blob = json.load(data_file)

    #for i in xrange(len(json_blob)):
        #if json_blob[i]["path"] == "/animals/cat/images/cat001.jpg":
            #print "popping: "
            #print i 
            #json_blob.pop(i)
            #break


    # add a file to the animals dir
    #pprint(json_blob['data'][0])
    pprint(json_blob)

if __name__ == '__main__':
    main()
