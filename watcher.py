#!/usr/bin/python3
import datetime
import threading
import time
import itertools
import PySimpleGUI as sg
import requests
import PIL
from PIL import Image
import io
import time
from requests.auth import HTTPBasicAuth

#TekVizion Watcher v0.1 - currently working on v0.2
#url = "http://10.1.53.83/screencapture"

"""
    TekVizion Image Grabber
    This program uses running multiple threads  in a PySimpleGUI environment, where the threads are used as timer threads
    that send events to the main window thread to be able to get the image from the server, and then display it in the window
    without having to save the image to a file on disk.The GUI window runs as the primary, main thread
    Other parts of the program  are implemented as threads that dispatch events to do work in the main window based on timers setby the user
    during configuration.  
    Base on the requirements for this tool:
    simple request to get an image from a server address 
    user basic digest auth with user name password
    wait timer between fetching images from the server 
    the wait time is using a thread event to prevent the GUI from being responsive 
    
    All input data after the user submit the program as locked since the update while the program is running is not 
    a part of the requirements, and not implemented, to give the user a better user experince the submit button will change color and it is
    disabled while the program is running until the user Exit and restrat the program.  
     
"""


def time_as_int():
    return int(round(time.time() * 100))

#Display Image Method called after a timer thread send an event
def display_image_in_window(image_obj, window):

    img = PIL.Image.open(io.BytesIO(image_obj))
    bio = io.BytesIO()
    img.thumbnail((500, 500))
    img.save(bio, format="PNG")
    img_data = bio.getvalue()
    img_box = sg.Image(data=img_data)
    window["-IMAGE-"].update(data=bio.getvalue())


# This Method called after a timer thread send an event to get an image from a configured URL or server address
def get_image_via_url_and_display(myConfig, window):
    if (myConfig.server != ''):
        #url = "https://source.unsplash.com/640x480"
        url = "http://10.1.53.83/screencapture"

    #time1 before sending the get request to the server
    time1 = datetime.datetime.now() #get current time before request
    get_time = ('getImageViaUrlAndDisplay: get image start time = ' + time1.strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3])
    #response = requests.get(url, stream=True)
    response = None

    #url = myConfigData.server
    #the server address, user name and paswoard from the GUI
    mheaders={
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
        'Accept-Language': 'en-GB,en-US,en;q=0.8'
        }
    response = requests.get(
            myConfig.server,
            auth=HTTPBasicAuth(myConfig.userName, myConfig.password),
            headers=mheaders,
            stream=True)
    sg.cprint(get_time, text_color='white', background_color='blue')

    #time2 after we received a response from the server
    time2 = datetime.datetime.now()
    current_time = ('getImageViaUrlAndDisplay: after get image  time = ' + time2.strftime(
        "%Y-%m-%d-%H-%M-%S.%f")[:-3])

    #time to get the image was
    timeToGetImage = time2 - time1

    sg.cprint(current_time, text_color='white', background_color='blue')
    sg.cprint(timeToGetImage, text_color='white', background_color='blue')

    image_obj = response.content; ##
    sg.cprint(response.text, text_color='yellow', background_color='black')
    sg.cprint(response.status_code, text_color='white', background_color='brown')
    display_image_in_window(image_obj, window) ##


def update_timer_in_gui(window, start_time):
    print("updateTimerInGui()")
    #get a date string with milliseconds (3 decimal places behind seconds)
    #current_time = ('updateTimerInGui time =' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3])
    #sg.cprint(current_time, text_color='white', background_color='black')


def worker_thread1(thread_name, run_freq, window):
    """
    A worker thread that communicates with the GUI
    These threads can call functions that block without affecting the GUI (a good thing)
    Note that this function is the code started as each thread. All threads are identical in this way
    :param thread_name: Text name used  for displaying info
    :param run_freq: How often the thread should run in milliseconds
    :param window: window this thread will be conversing with
    :type window: sg.Window
    :return:
    """
    print('Starting GetImageThread  - {} that runs every {} s'.format(thread_name, run_freq))
    for i in itertools.count():  # loop forever, keeping count in i as it loops
        # time.sleep(run_freq / 1000)  # sleep for a while
        time.sleep(run_freq)  # sleep for a while
        # put a message into queue for GUI
        window.write_event_value(thread_name, f'count = {i}')


def worker_thread2(thread_name, run_freq, window):
    """
    A worker thread that communicates with the GUI
    These threads can call functions that block without affecting the GUI (a good thing)
    Note that this function is the code started as each thread. All threads are identical in this way
    :param thread_name: Text name used  for displaying info
    :param run_freq: How often the thread should run in milliseconds
    :param window: window this thread will be conversing with
    :type window: sg.Window
    :return:
    """
    print('Starting DisplayImageThread- {} that runs every {} ms'.format(thread_name, run_freq))
    for i in itertools.count():  # loop forever, keeping count in i as it loops
        # time.sleep(run_freq / 1000)  # sleep for a while
        time.sleep(run_freq)  # sleep for a while
        # put a message into queue for GUI
        window.write_event_value(thread_name, f'count = {i}')


class configData():
    def __init__(self):
        self.server = ''
        self.userName = ''
        self.password = ''
        self.waitTime = '0'

    def getConfigData(self):
        return self

    def setConfigData(self, server, user, pwd, wt, srt=None, sot=None, dir=''):
        self.server = server
        self.userName = user
        self.password = pwd
        self.waitTime = wt


def update_my_config_data(mWindow, myConfig):
    myConfig.server = mWindow["-SERVER-"].get()
    myConfig.userName = mWindow["-NAME-"].get()
    myConfig.password = mWindow["-PASSWORD-"].get()
    myConfig.waitTime = mWindow["-REFERESH-"].get()

    if (myConfig.server == '') or (myConfig.waitTime == '') or (myConfig.userName == '') or (myConfig.password == ''):
        return False
        print("myConfig Data is [server {}---- userName {}---- password {}---- waitTime {}]".format(myConfig.server,
                                                                                                    myConfig.userName,
                                                                                                    myConfig.password,
                                                                                                    myConfig.waitTime))
    return True


background = '#374B6D'
sg.SetOptions(background_color=background,
              element_background_color=background,
              text_element_background_color=background,
              # window_location=(0, 0),
              margins=(10, 10),
              text_color='Black',
              input_text_color='Black',
              button_color=('Black', 'gainsboro'))

''' 
startWorkers starts 2 threads with the timer wait time from the GUI or user input, and after the timer fires these thread workers
send an event to the main GUI program to get the image, and then display it by updating the elements in the UI using window[-key-].update()
'''
def startWorkers(sg, window, getImageTimer):
    # -- Create a Queue to communicate with GUI --
    # queue used to communicate between the gui and the threads
    # -- Start worker threads, each taking a different amount of time
    threading.Thread(target=worker_thread1, args=('GetImageThread', getImageTimer, window,), daemon=True).start()
    threading.Thread(target=worker_thread2, args=('DisplayImageThread', getImageTimer + .01, window,),
                     daemon=True).start()

    # -- Start the GUI passing in the Queue to print the thread message in the main MultiLine window--
    sg.cprint_set_output_destination(window, '-ML-')

    window['-ML-'].update(visible=False) #can make false to hide threadlog
    colors = {'GetImageThread': ('white', 'red'), 'DisplayImageThread': ('white', 'green')}


def grabber_main():
    """
    Starts and executes the GUI
    Reads data from a Queue and displays the data to the window
    Returns when the user exits / closes the window
        (that means it does NOT return until the user exits the window)
    :param gui_queue: Queue the GUI should read from
    :return:
    """

    current_time, paused_time, paused = 0, 0, False
    start_time = time_as_int()

    # store all input data is our config class object
    myConfig = configData()

    LOGO = b'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'
    size = (250, 20)
    HTTPRED = '#E84C3D'
    HTTPSBLUE = '#1434E6'

    column1 = [[sg.Text(" ", font=("Helvetica", 15), text_color="#1434E6",
                        justification="center")], ]
    elements = [
        [sg.Image(data=LOGO)],
        [sg.Column(column1, size=size)],
        [sg.T(' ', background_color=HTTPRED, text_color='white', k='-TITLEBAR-', size=(115, 1),
                 justification='center')
         ],
        #[sg.T("         "), sg.Radio('http://', "RADIO", text_color="white", default=True, key="-IN-")],
        #[sg.T("         "), sg.Radio('https://', "RADIO", text_color="white", default=False)],
        [sg.Text('Server Address: ', size=(20, 1), text_color="white") , sg.InputText(key='-SERVER-', size=(40, 1), do_not_clear=True)],
        [sg.Text('User Name: ', size=(20, 1), text_color="white"), sg.InputText(key='-NAME-', size=(40, 1), do_not_clear=True)],
        [sg.Text('Password: ', size=(20, 1), text_color="white"), sg.InputText(key='-PASSWORD-', password_char='*', size=(40, 1), do_not_clear=True)],
        [sg.Text('Refresh Rate: ', size=(20, 1), text_color="white"), sg.InputText(key='-REFERESH-', size=(4, 1), do_not_clear=True)],
        [sg.Button('Submit', k='-SUBMIT-', button_color=HTTPRED), sg.Exit(button_color=HTTPRED)],
        [sg.Text('_' * 80)],
    ]

    layout = [
        [sg.Text('Display Image Frame', visible=False)],
        [sg.Text('', size=(15, 1), key='-OUTPUT-')],
        [sg.Image(k='-IMAGE-', enable_events=True)],
        [sg.Multiline(size=(80, 20), key='-ML-', autoscroll=True, visible=False)],

    ]


    finalLayout = elements + layout

    window = sg.Window('TekVizion Watcher', finalLayout, size=(575, 675), resizable=1, keep_on_top=False,
                       finalize=True)

    sg.cprint_set_output_destination(window, '-ML-')

    def protocol_color():
        if sg.T(default = True):
            sg.T = HTTPRED
        if sg.T(default = False):
            sg.T = HTTPSBLUE

    #colors = {'GetImageThread': ('white', 'red'), 'DisplayImageThread': ('white', 'green')}


#--------------------- EVENT LOOP ---------------------
    while True:
        # wait for up to 100 ms for a GUI event
        event, values = window.read(timeout=100)
        current_time = time_as_int() - start_time

        # if the event is Exit we close the window and end the while loop
        if event in (sg.WIN_CLOSED, 'Exit'):
            break


        if event == 'DisplayImageThread':
            print("DisplayImageThread Thread sent us an event is DisplayImageThread")
            get_image_via_url_and_display(myConfig, window)

        if event == 'GetImageThread':
            print("GetImageThread Thread sent us an event is DisplayImageThread")
            update_timer_in_gui(window, start_time)

        if event == "Exit" or event == sg.WIN_CLOSED:
            print("GUI Window sent us an event is GetImageThread", event)
            break

        if event == "-SUBMIT-":
            print('Hit Submit')
            haveAllConfig = update_my_config_data(window, myConfig)

            #if the user entered all the configuration data haveAllConfig will be True and we can start the workers threads
            if (haveAllConfig):

                # Get the image get timer, make sure that there isnt an empty string '' on timers as that caus a type  casting error
                if (myConfig.waitTime == ''):
                    myConfig.waitTime = '0'

                getImageTimer = int(myConfig.waitTime)

                #now we can start the workers thread
                startWorkers(sg, window, getImageTimer)

                #Disable the submit button now, since the program is running.
                #window.FindElement('-SUBMIT-').Update(disabled=True, button_color='#b9b2b2')

            else:
                sg.SetOptions(  # window_location=(700, 400),
                    margins=(60, 20),
                    button_color=('Red', 'gainsboro'))
                sg.Popup('Missing Config Data', text_color = "white")  # Shows red error button

        # --------------- Loop through all messages coming in from threads ---------------
        #if event == 'GetImageThread' or event == 'DisplayImageThread':
            #sg.cprint(event, values[event], c=colors[event])

    # if user exits the window, then close the window and exit the GUI func
    window.close()


if __name__ == '__main__':
    grabber_main()
