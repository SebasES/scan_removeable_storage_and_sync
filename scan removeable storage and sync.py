import os, string, win32api,time, sys
from dirsync import sync
import ctypes
import threading

#LOGGING-----------------------------------
te = open('MicroSD_Readout_log_' + time.strftime("%Y_%m_%d_%Hh_%Mm") + '.txt','w')  # File where you need to keep the logs

class Unbuffered:
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
       te.write(data)    # Write the data of stdout here to a text file as well
sys.stdout=Unbuffered(sys.stdout)


#FUNCTIONS & CLASSES---------------------------------

# Define a function for the thread
def SD_copyjob(sourcedir, targetdir):
   sync(sourcedir, targetdir, 'sync', verbose=True, modtime=True)

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxA(0, text, title, style)

def get_used_drive_letters():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    letters = [d[0] for d in drives]
    return letters

def flushdir(dir, time_offset_sec):
    now = time.time()
    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        if os.stat(fullpath).st_mtime < (now - time_offset_sec):
            if os.path.isfile(fullpath):
                os.remove(fullpath)
            elif os.path.isdir(fullpath):
                flushdir(fullpath,time_offset_sec)


#-----------VARIABLES---------------------           
target_directory_name=''
source_directory_name=''
root_dir = os.getcwd()
msg_temp=''
flush_delay=2419200
SD_CARD=[]
threads = []
#-----------------------------------------MAIN-------------------------------------------------------------------------

print 'USB-Readout: looking for connected SD-Cards............. \n'

while 1==1:
    """print 'search for directories: '"""
    directories=[]
    for f in os.listdir(root_dir):
        if os.path.isfile(os.path.join(root_dir, f)):
            1==1
        else:
            directories.append(f)

    """print 'search for drives: '"""
    drives= []
    labels=[]
    inserted_drives=get_used_drive_letters()
    for i in inserted_drives:
        i=''.join(map(str, i))+':/'
        try:
            label=win32api.GetVolumeInformation(i)[0]
        except:
            label='Not_Available'
        labels.append(label)
        drives.append(i)

    index=[i for i, item in enumerate(labels) if item in directories]
        
    if not index:
            print '------------No MicroSD found------------------'
            Mbox('USB-Readout', 'There wasnt any SD-Card matching to a AU# found:\n\nA)Please re-instert them into the USB and check if they appear in the File-Explorer\n\nB)Make sure there is a Folder created with the AU# on the Blackvue-Harddrive '+ root_dir + '\n\nC)Make sure the SD-Card is labeled (File-Explorer) with the AU#', 1)
    else:
        for i in index:
                drive_letter=''.join(map(str, drives[i]))
                label=''.join(map(str, labels[i]))
                print '----------------------Micro SD found on ' + drive_letter + '  labeled as ' + label + '\n'

        for i in index:
                drive_letter=''.join(map(str, drives[i]))
                label=''.join(map(str, labels[i]))
                msg_temp = msg_temp + label + '\n'
        Mbox('USB-Readout','Following SD-Cards were found:\n\n'+msg_temp+'\nIs that correct? (If not hit cancel and make sure all SD-Cards were detected in the File-Explorer and restart program)', 1)

        for i in index:
                drive_letter=''.join(map(str, drives[i]))
                label=''.join(map(str, labels[i]))
                target_directory_name = '/' + time.strftime("%Y_%m_%d_%Hh_%Mm")
                targetdir =root_dir + '/' + label + target_directory_name
                sourcedir = drive_letter + source_directory_name
                if not os.path.isdir(targetdir):
                   os.makedirs(targetdir)
                print 'copying from: ' + sourcedir
                if not os.path.isdir(sourcedir):
                   Mbox('USB-Readout','NO SOURCE DIRECTORY FOUND - Make sure SD-Card contains a Record Folder that contains data: ' + sourcedir, 1)
                print 'copying to: ' + targetdir
                t = threading.Thread(target=SD_copyjob,args=(sourcedir, targetdir))
                """threads.append(t)"""
                t.start()

    """t.start()"""
    """t.join()"""
    """print 'DONE - REMOVE CARDS \n'
    
    input("Press enter to close program")"""
    break
 
    
