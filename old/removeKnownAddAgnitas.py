# coding=utf-8
from urllib2 import Request, urlopen, URLError
import json
def main() :
    print ("öffne emails.csv...");
    with open ("tagsorted.txt", "r") as myfile:
        lines=myfile.readlines();
    print ("erfolgreich!");
    finalStr = ""
    print("suche unbekannter Domains initialisierung");
    print(len(lines))
    for i in range(0,len(lines)) :
        finalStr += lines[i][:-1].lower().replace(" \"], ","\"], ") + "\r\n";
        print lines[i]
    print ("erfolgreich");
    print ("schreibe in results.csv");
    obj = open("results.txt", 'wb');
    obj.write(finalStr);
    obj.close;
    print("erfolgreich");
    x = raw_input("press enter to close application");
        
    
if __name__ == '__main__':
    main()