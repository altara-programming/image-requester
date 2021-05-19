import io
import os

import PySimpleGUI as sg
import glob
from PIL import Image, ImageTk
import downLoadImageHelper
import displayImagesPage
import  time
import threading
from threading import Thread, Event
import logging
import datetime
import concurrent.futures

event = Event()

sg.theme('SystemDefault')

BLUE = '#2196f2'
MOCOLOR ='#E84C3D'
RED = '#FF0000'
DARK_GRAY = '#212021'
LIGHT_GRAY = '#e0e0e0'
#BLUE_BUTTON_COLOR = '#FFFFFF on #2196f2'
RED_BUTTON_COLOR = '#FFFFFF on #E84C3D'
GREEN_BUTTON_COLOR ='#FFFFFF on #00c851'
LIGHT_GRAY_BUTTON_COLOR = f'#212021 on #e0e0e0'
DARK_GRAY_BUTTON_COLOR = '#e0e0e0 on #212021'



class MyThreadWithArgs(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.target = target
        self.arg = args
        self.kwargs = kwargs


        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        if (len(self.args) > 1 ):
            logging.debug('wait_for_event_timeout starting %s', self.target.__name__)
            self.target(self.args[0], self.args[1])
        else:
            logging.debug('wait_for_event_timeout starting %s', self.target)
            self.target(self.args[0])

        return




def wait_for_event(e):
    """Wait for the event to be set before doing anything"""

    logging.debug("event wait state %d seconds and then timeout :Time now is  %s ", e.is_set(), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    event_is_set = False
    event_timeout_counter = 0;
    while True:
        #logging.debug('wait_for_event: WAITING FOR EVENTS event flag %d ', e.wait())
        event_is_set = e.wait()
        logging.debug('DONE wait_for_event event set: %d', event_is_set)

        if (not event_is_set):
            event_timeout_counter  +=1
            logging.debug("event wait state %d seconds and then timeout :Time now is  %s ", e.is_set(), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

        #if(e.is_set()):
            #logging.debug('DONE========Wait for it  wait_for_event event set: %d, waiting for event timeout %d', event_is_set, event_timeout_counter)

        else:
            time.sleep(1)
            #logging.debug(' wait_for_event is now ready again set: %d', e.is_set())


def wait_for_event_timeout(e, t):
    """Wait t seconds and then timeout"""
    logging.debug("Wait %d seconds and then timeout :Time now is  %s ", t, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    while True:
        logging.debug('wait_for_event_timeout Wait fot t  timeout t is %f ', t)
        event_is_set = e.wait(t)
        time.sleep(1)
        if(event_is_set):
            logging.debug("wait_for_event_timeout Timer elapsed time now is %s )", datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
            e.clear()
            #logging.debug("Event was set to true() earlier, moving ahead with the thread")
            event_is_set = False
            continue;
        else:
            e.set()
            logging.debug("wait_for_event_timeout event wait state %d seconds and then timeout :Time now is  %s ", e.is_set(), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)


class configData():
    def __init__(self):
        self.server = ''
        self.userName = ''
        self.password = ''
        self.waitTime = ''
        self.startTime = ''
        self.stopTime = ''
        self.storeDir = ''

    def getConfigData(self):
        return self

    def setConfigData(self, server, user, pwd, wt, srt=None, sot=None, dir='' ):
        self.server = server
        self.userName = user
        self.password = pwd
        self.waitTime = wt
        self.startTime = srt
        self.stopTime = sot
        self.storeDir = dir


def parse_folder(path):
    images = glob.glob(f'{path}/*.jpg') + glob.glob(f'{path}/*.png')
    return images
def load_image(path, window):
    try:
        image = Image.open(path)
        image.thumbnail((400, 400))
        photo_img = ImageTk.PhotoImage(image)
        window["image"].update(data=photo_img)
    except:
        print(f"Unable to open {path}!")

size = (250, 20)

#def getImagesAndDisplay(dir):
def getImagesAndDisplay(configData):
    url=''
    #imageInfo = downLoadImageHelper.downLoadImage(url,dir)
    imageInfo = downLoadImageHelper.downLoadImage(configData)
    print( "IMAGE INVOT ")


file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("All files (*.*)", "*.*")]

def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def dirFileHDLR(path):

    # Get the folder containin:g the images from the user
    # folder = sg.popup_get_folder('Image folder to open', default_path='')
    folder = path
    if not folder:
        sg.popup_cancel('Cancelling Request please wait ', button_color=MOCOLOR)
        raise SystemExit()

    # PIL supported image types
    img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

    # get list of files in folder
    flist0 = os.listdir(folder)

    # create sub list of image files (no sub folders, no wrong file types)
    fnames = [f for f in flist0 if os.path.isfile(
        os.path.join(folder, f)) and f.lower().endswith(img_types)]

    num_files = len(fnames)                # number of images found
    if num_files == 0:
        sg.popup('No files in folder')
        raise SystemExit()

    del flist0                             # no longer needed

    # make these 2 elements outside the layout as we want to "update" them later
    # initialize to the first file in the list
    filename = os.path.join(folder, fnames[0])  # name of first file in list
    #image_elem = sg.Image(data=get_img_data(filename, first=True))
    #filename_display_elem = sg.Text(filename, size=(80, 3))
    #file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))
    return filename, fnames, num_files, folder

def getLatestDownloadedFile(dirpath,mWindow):
    newest = ''
    path = dirpath

    if path == '':
        print("empty or invalid path was selected %s", path)
        return


    try:
        os.chdir(path)
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    except:
        print ("dir or file not valid", path)

    images = parse_folder(dirpath)
    if (len(images) > 1 ):

        list_of_files = glob.glob(dir) # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getmtime)
        print(latest_file)
        fPath = images[0]
    else:
        #no file tp display
        fPath=''

    if fPath != '':

        image = Image.open(fPath)
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        #mWindow["-IMAGE-"].update(data=bio.getvalue())
        mWindow["-IMAGE-"].update(data=bio.getvalue())
        load_image(dirpath, mWindow)
    return fPath

def modify_window(mWindow):
    while True:
        if event.is_set():
            break
        time.sleep(1)

def refreshImageFiles(dir, mWindow):
    print("refreshImageFiles")
    getLatestDownloadedFile(dir, mWindow)
    time.sleep(1)
def updateMyConfigyData(mWindow, myConfig):
    myConfig.server = mWindow["-SERVER-"].get()
    myConfig.userName = mWindow["-NAME-"].get()
    myConfig.password = mWindow["-PASSWORD-"].get()
    myConfig.waitTime = mWindow["-REFERESH-"].get()
    myConfig.storeDir = mWindow["-DIR-"].get()

    print("myConfig Data is [{}{}{}{}]".format(myConfig.server, myConfig.userName,myConfig.password,  myConfig.waitTime))
    #myConfig.stopTime = mWindow["-SERVER-"].get()
    #myConfig.storeDir = mWindow["-SERVER-"].get()

def main():
    #store all input data is our config class object
    myConfig = configData()

    mDirPath = ''
    #LOGO = b'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'
    LOGO = b'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'
    #image_filename ='./assets/images/logo.png'


    column1 = [[sg.Text("Gabber Version 0.1", font=("Helvetica", 15), text_color="#FF0000",justification="center")]]
    layout1 = [
        [sg.Image(key="-IMAGE-")],
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), key="-FILE-"),
            #sg.FileBrowse(file_types=file_types),
            sg.Button("Load Image", button_color=MOCOLOR),
            sg.FolderBrowse(button_color=MOCOLOR)
        ],
    ]
    elements = [
        [sg.Image(data=LOGO)],
        [sg.Column(column1, size=size)],
        [sg.Text('Grabber v.0.1', background_color=MOCOLOR, text_color='white', k='-TITLEBAR-',  size=(115, 1), justification='center')],
        [sg.Text('Server Address', size=(20, 1)), sg.InputText(key='-SERVER-' ,size=(40, 1))],
        [sg.Text('User Name', size=(20, 1)), sg.InputText(key='-NAME-',size=(40, 1))],
        [sg.Text('Password', size=(20, 1)), sg.InputText(key='-PASSWORD-',password_char='*', size=(40, 1))],
        [sg.Text('Frequency in Seconds', size=(20, 1)), sg.InputText(key='-REFERESH-', size=(4, 1))],
        [
            sg.Text('Image Directory', size=(20, 1)),
            sg.InputText(key='-DIR-', size=(40, 1)),
            sg.FolderBrowse(button_color=MOCOLOR),
        ],
        [sg.Button('Submit', button_color=MOCOLOR), sg.Button('Cancel', button_color=MOCOLOR), sg.Exit(button_color=MOCOLOR)],
        [sg.Text('_' * 80)],
        [sg.Image(key="image")],
        [
            sg.Button("Open Image Viewer", button_color=MOCOLOR)
        ]

    ]
    layOut = elements + layout1
    mWindow = sg.Window("Grabber Viewer", layOut, size=(675, 775), resizable=1)

    images = []
    location = 0
    mDirPath = ''
    i = 0

     #logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)
    tEvent = threading.Event()


    isMyThreadsRunning = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(thread_function, range(4))

    while True:

        if(tEvent.isSet()):
            print("============================GET IMAGE GOES HERE  ")
            print("============================GET IMAGE GOES HERE  ")
            tEvent.clear()

        event, values = mWindow.read()
        print(event, values)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "file":
            images = parse_folder(values["file"])
            if images:
                load_image(images[0], mWindow)
        if event == "Next" and images:
            if location == len(images) - 1:
                location = 0
            else:
                location += 1
            load_image(images[location], mWindow)
        if event == "Prev" and images:
            if location == 0:
                location = len(images) - 1
            else:
                location -= 1
            load_image(images[location], mWindow)
        if event  == "Submit":
            updateMyConfigyData(mWindow, myConfig)
            if (myConfig.server == ''):
                #for testing
                myConfig.server = "https://source.unsplash.com/640x480"
                mWindow["-SERVER-"].update(myConfig.server)

            if (myConfig.waitTime == ''):
                myConfig.waitTime = '10'
                mWindow["-REFERESH-"].update(myConfig.waitTime)

            if (myConfig.storeDir == ''):
                myConfig.storeDir = '/Users/mialtaraireh/Desktop/junk_images/' #/Users/mohammadaltaraireh/Desktop/images/'
                mWindow["-DIR-"].update(myConfig.storeDir)
            if not isMyThreadsRunning:

                print('Hit Submit')
                mDirPath = mWindow["-DIR-"].get()
                t1 = threading.Thread(target=getImagesAndDisplay, args=(myConfig,))
                t2 = threading.Thread(target=refreshImageFiles, args=(myConfig,mWindow))
                t1.start()
                t2.start()

                twait1 = MyThreadWithArgs(name='twait1',target=wait_for_event_timeout,args=(tEvent, int(myConfig.waitTime)), kwargs={'c':'C', 'd':'D'})
                twait2 = MyThreadWithArgs(name='twait2',target=wait_for_event, args=(tEvent,),kwargs={'a':'A', 'b':'B'})
                #getImagesAndDisplay(window)

                twait1.start()
                twait2.start()
                isMyThreadsRunning = True

            else:
                getLatestDownloadedFile(mDirPath, mWindow)
                isMyThreadsRunning = False
                print("Threads are already running, Exit and Restart")

        if event == "-DIR-":
            # make these 2 elements outside the layout as we want to "update" them later
            # initialize to the first file in the list
            mDirPath = values["-DIR"]
            filename, fnames, num_files, folder =  dirFileHDLR(mDirPath)
            #filename = './assets/images/logo.png' # name of first file in list
            #fnames = ['./assets/images/logo.png','./assets/images/logo.png']

        if event == "Open Image Viewer":
            print("-DIR- is ")
            displayImagesPage.displayHandler(mDirPath)

        if event == "Load Image":
            print("Load image was pressed")
            mfile = mWindow["-FILE-"].get()

            if (mfile == ''):
                #Alex TBD error no file was upladed , send a box message to the user to load a file
                continue

            print("Trying to Display file ", mfile)
            image = Image.open(mfile)
            image.thumbnail((400, 400))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            mWindow["-IMAGE-"].update(data=bio.getvalue())
            #load_image(mfile, mWindow)



#window.close()

if __name__ == "__main__":
    main()


