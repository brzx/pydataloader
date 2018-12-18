
import shutil, zipfile, os, time

def delFile(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))

if __name__ == "__main__":
    home = os.path.abspath(os.curdir)
    try:
        delFile("library")
        os.rmdir("library")
    except WindowsError as ex:
        print(ex)
    os.mkdir("library")
    
    shutil.copyfile("library.zip","library\library.zip")
    os.chdir("library")
    fo = zipfile.ZipFile("library.zip")
    fo.extractall()
    fo.close()
    time.sleep(0.5)
    library = (os.path.abspath(os.curdir))
    os.remove("library.zip")
    
    pubsub = library + "\\wx\\lib\\pubsub"
    delFile(pubsub)
    shutil.copyfile(home+"\\pubsub.zip", pubsub+"\\pubsub.zip")
    os.chdir(pubsub)
    
    pubsubFile = zipfile.ZipFile("pubsub.zip")
    pubsubFile.extractall()
    pubsubFile.close()
    time.sleep(0.5)
    os.remove("pubsub.zip")
    
    os.chdir(home)
    shutil.make_archive("output\\library", "zip", library)