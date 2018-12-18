
import shutil, zipfile, os, time

if __name__ == "__main__":
    shutil.copyfile("index.html","dist\index.html")
    shutil.copyfile("logging.json","dist\logging.json")
    shutil.copyfile("Issue List.txt","dist\Issue List.txt")
    