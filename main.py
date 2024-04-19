from tkinter import filedialog, Tk, Label, Button, Entry, PhotoImage, Toplevel, Checkbutton, IntVar
from pynput.keyboard import Listener, Key, Controller
from pynput.mouse import Listener as mouseListener
from time import time, strftime, gmtime, sleep
import os
from threading import Thread, Timer

# utilities
def filter(event):
    key_str = None
    if hasattr(event, 'char') and event.char is not None:
         key_str = event.char
    else :
        key_str = str(event).replace("Key.", "")

    # print('filtering event: ', key_str)
    match key_str:
        case "shift_r":
            key_str = "shift"
        case "ctrl_l":
            key_str = "ctrl"
        case "ctrl_r":
            key_str = "ctrl"
        case "alt_l":
            key_str = "alt"
        case "alt_gr":
            key_str = "alt"
        case "\x11":  # Ctrl + Q
            key_str = "q"
        case "\x17":  # Ctrl + W
            key_str = "w"
        case "\x05":  # Ctrl + E
            key_str = "e"
        case "\x12":  # Ctrl + R
            key_str = "r"
        case "\x14":  # Ctrl + T
            key_str = "t"
        case "\x19":  # Ctrl + Y
            key_str = "y"
        case "\x15":  # Ctrl + U
            key_str = "u"
        case "\t":  # Ctrl + I
            key_str = "i"
        case "\x0f":  # Ctrl + O
            key_str = "o"
        case "\x10":  # Ctrl + P
            key_str = "p"
        case "\x01":  # Ctrl + A
            key_str = "a"
        case "\x13":  # Ctrl + S
            key_str = "s"
        case "\x04":  # Ctrl + D
            key_str = "d"
        case "\x06":  # Ctrl + F
            key_str = "f"
        case "\x07":  # Ctrl + G
            key_str = "g"
        case "\x08":  # Ctrl + H
            key_str = "h"
        case "\n":  # Ctrl + J
            key_str = "j"
        case "\x0b":  # Ctrl + K
            key_str = "k"
        case "\x0c":  # Ctrl + L
            key_str = "l"
        case "\x1a":  # Ctrl + Z
            key_str = "z"
        case "\x18":  # Ctrl + X
            key_str = "x"
        case "\x03":  # Ctrl + C
            key_str = "c"
        case "\x16":  # Ctrl + V
            key_str = "v"
        case "\x02":  # Ctrl + B
            key_str = "b"
        case "\x0e":  # Ctrl + N
            key_str = "n"
        case "\r":  # Ctrl + M
            key_str = "m"
        case "\x1b":  # Ctrl + [
            key_str = "["
        case "\x1d":  # Ctrl + ]
            key_str = "]"
        case "\x1c":  # Ctrl + \
            key_str = "\\"
        case "<186>":  # Ctrl + ;
            key_str = ";"
        case "<222>":  # Ctrl + '
            key_str = "'"
        case "<188>":  # Ctrl + ,
            key_str = ","
        case "<190>":  # Ctrl + .
            key_str = "."
        case "<191>":  # Ctrl + /
            key_str = "/"
        case "<189>":  # Ctrl + -
            key_str = "-"
        case "<187>":  # Ctrl + =
            key_str = "="

    # print('filtered event: ', key_str)
    return key_str  


def unfilter(event):
    key_str = event
    if len(key_str) > 1:
        key_str = "Key." + key_str
    return key_str  

def retreive_data():
    if os.path.exists("keystrokes_recorder_data/settings.txt"):
        with open('keystrokes_recorder_data/settings.txt', 'r') as file:
            settings_content = file.read()
            settings_dict = eval(settings_content)
            return settings_dict
    else :
        return None

def getFileName():
    data = retreive_data()
    if data is None:
        return
    path = data['output_folder']
    if path == "None":
        return
    
    if not os.path.exists(path):
        os.makedirs(path)

    files = os.listdir(path)
    target_files = []
    for file in files :
        if file.endswith(".txt") and file.startswith("keylog_"):
            target_files.append(file) 
    
    file_name = f"keylog_{len(target_files)}.txt"
    return file_name

def destroy_and_open(setting_prompt):
    setting_prompt.destroy()
    open_settings()

def setting_prompt():
    setting_prompt = Toplevel()
    setting_prompt.title("Wait!!")
    setting_prompt.geometry("850x200")
    setting_prompt.maxsize(850,200)
    setting_prompt.minsize(850,200)
    setting_prompt.config(bg='#3F403F')

    text = Label(setting_prompt, font='Arial 10', bg='#3F403F', fg="white", text="Before starting, please configure your settings!")
    text1 = Label(setting_prompt, font='Arial 10', bg='#3F403F', fg="white", text="1. Make sure you set the output folder in which your keylogs will be saved.")
    text2 = Label(setting_prompt, font='Arial 10', bg='#3F403F', fg="white", text="2. set the fps limiter to avoid redundant data (for consistency, set it to the fps you will record your video in eg. 60fps, 120fps, etc)") 
    text3 = Label(setting_prompt, font='Arial 10', bg='#3F403F', fg="white", text="3. specify keybind for starting recording from your recorder so we can start recording video for you while also recording keylogs simulationously")
    text4 = Label(setting_prompt, font='Arial 10', bg='#3F403F', fg="white", text="4. give a shortcut for starting the keylog recorder so you can start recording with shortcut keys while playing your games!")
    text.grid(row=0, pady=5, padx=15)
    text1.grid(row=1, pady=5, padx=15)
    text2.grid(row=2, pady=5, padx=15)
    text3.grid(row=3, pady=5, padx=15)
    text4.grid(row=4, pady=5, padx=15)
    setting_prompt.protocol("WM_DELETE_WINDOW", lambda: destroy_and_open(setting_prompt))

def parseInt(string, allowfloat = False):
    # Initialize an empty string to store the numeric part
    numeric_part = ''
    
    # Iterate through the characters of the string
    for char in string:
        if allowfloat == True:
            if char.isdigit() or char == ".":
                numeric_part += char
        else :
            if char.isdigit():
                numeric_part += char

    if numeric_part:
        if allowfloat == True:
            return float(numeric_part)
        else :
            return int(numeric_part)
    else:
        return ''

shortcut_label = None
record_shortcut_label = None
fps_entry = None
output_dir_label = None
delay_entry = None
def saveSettings():
    if not os.path.exists("keystrokes_recorder_data"):
        os.mkdir('keystrokes_recorder_data')
    
    fps = parseInt(fps_entry.get())
    delay = parseInt(delay_entry.get(), allowfloat=True)
    settings = {
        "shortcut_to_start" : shortcut_label.cget("text"),
        "record_shortcut" : record_shortcut_label.cget("text"),
        "fps" : fps,
        "output_folder" : output_dir_label.cget("text"),
        "delay" : delay
    }

    with open('keystrokes_recorder_data/settings.txt', 'w') as file:
        # Write something to the file if needed
        file.write(str(settings))

#shortcut system
label = None
button = None
previousText = None
keyHistory = []

def addKey(label,button, key):
    if len(keyHistory) > 0:
        if key not in keyHistory:
            keyHistory.append(key)
    else :
        keyHistory.append(key)

    # print(keyHistory)
    if not label or not button:
        return
    button.config(text="Confirm",command=confirm)

    shortcut = "" 
    for index in keyHistory:
        if index == keyHistory[-1]:
            shortcut += index
            break 
        shortcut += f"{index}+"
    label.config(text=shortcut)

def removeKey(label, button, key):
    if key not in keyHistory:
        if key == key.upper():
            key = key.lower()
        else : 
            key = key.upper()
        if key not in keyHistory:
            return
    index = keyHistory.index(key)  # Trying to find the key
    keyHistory.pop(index)
    # print(keyHistory)
    
    # if not label or not button:
    #     return
    # shortcut = "" 
    # for index in keyHistory:
    #     if index == keyHistory[-1]:
    #         shortcut += index
    #         break 
    #     shortcut += f"{index}+"
    # label.config(text=shortcut)

    # if not keyHistory:
    #     label.config(text="None")
    #     stopKeyShortcut()

def key_shortcut(paramlabel, parambutton):
    global label, button, previousText
    if label or button:
        return
    previousText = parambutton.cget("text")
    parambutton.config(text="detecting buttons...")
    label = paramlabel
    button = parambutton  

def stopKeyShortcut():
    global label, button, previousText, shortcut_label, shortcut_button
    copy_label = label
    copy_button = button
    button.config(text=previousText, command=lambda: key_shortcut(copy_label, copy_button))
    label = None
    button = None 
    previousText = None

def confirm():
    stopKeyShortcut()
    saveSettings()

settings_window = None
def saveSettingsAndUnfocus(event=None):
    saveSettings()
    settings_window.focus_set() 

#output folder selection
output_dir_label = None
def open_folder_dialog():
    selected_folder = filedialog.askdirectory()  # Open file explorer to choose a folder
    if selected_folder:  # Check if a folder was selected
        output_dir_label.config(text=selected_folder)  # Update the label with the selected folder path
        saveSettings()
        # also store the folder in the data file

# functions handling event listeners
# last_log_time = 0
last_log_event = [1, 2]
def log_event(event_type, event):
    global start_time, output_file_name, last_log_event
    
    data = retreive_data()
    if start_time is None or output_file_name is None or data is None:
        return
    
    path = data['output_folder']
    fps = data['fps']
    if path == "None" or fps == "":
        return
    
    # time_interval = 1/fps
    # current_time = time()
    # timediff = current_time - last_log_time

    # if timediff < time_interval:
        # return

    if not os.path.exists(path):
        os.makedirs(path)

    if last_log_event[0] != event_type or last_log_event[1] != event:
        # last_log_time = current_time
        second_elapsed = time() - start_time
        frames_elapsed = int(second_elapsed * fps) % fps
        timestamp = strftime('%H:%M:%S', gmtime(second_elapsed))
        if(timestamp == "00:00:00"):
            return
        timestamp_with_frame = f"{timestamp}:{frames_elapsed}"
        log_entry = f"{timestamp_with_frame} - {event_type}: {event}\n"
        with open(os.path.join(path, output_file_name), 'a') as file:
            file.write(log_entry)
        last_log_event = [event_type, event] 

releaseHistory = []
def refresh():
    global releaseHistory
    if len(releaseHistory) > 0:
        for key in releaseHistory:
            removeKey(label, button, key)
        releaseHistory = []

simulating_keys = False
def onclick(event):
    # print('unfiltered event', event)
    key_str = filter(event)
    # print('filtered event', key_str)
    if simulating_keys == True:
        return
    refresh()
    global start_time, output_file, keyHistory
    addKey(label, button, key_str)
    if keylog:
        log_event("keydown", key_str)
    data = retreive_data()
    if not data:
        return
    shortcut_to_start = data['shortcut_to_start']
    if shortcut_to_start:
        shortcut_to_start = shortcut_to_start.split("+")
        if sorted(keyHistory) == sorted(shortcut_to_start):
            toggleRecord()        

def onrelease(event):
    global keyHistory, releaseHistory
    key_str = filter(event)
    if simulating_keys == True:
        data = retreive_data()
        shortcut_to_start = data['shortcut_to_start'].split("+")
        match = False
        for key in shortcut_to_start:
            if key == key_str and key_str not in releaseHistory:
                match = True
        if match == True:
            releaseHistory.append(key_str)
        record_shortcut = data['record_shortcut'].split("+")
        if releaseHistory == record_shortcut:
            releaseHistory = []
        return
    
    removeKey(label, button, key_str)

    if keylog:
        log_event("keyup", key_str)

last_log_time = 0
def onmove(x, y):
    global last_log_time
    if not keylog:
        return
    
    data = retreive_data()
    if not data:
        return
    fps = data['fps']

    time_interval = 1/fps
    current_time = time()
    timediff = current_time - last_log_time

    if timediff < time_interval:
        return

    log_event("mousemove", f"x:{x}, y:{y}")
    last_log_time = current_time
    pass

def onscroll(x, y, dx, dy):
    if dy == 1:
        log_event("mouseScrollUp", dy)
    if dy == -1:
        log_event("mouseScrollDown", dy)

def onmouseclick(x, y, button, pressed):
    log_event("mouseClick", f"{str(button).removeprefix("Button.")}, {pressed}")

def eventListeners():
    # Register keydown and keyup callbacks
    with Listener(on_press=onclick, on_release=onrelease) as keyboard_listener:
        with mouseListener(on_move=onmove, on_click=onmouseclick, on_scroll=onscroll) as mouse_listener:
            keyboard_listener.join()
            mouse_listener.join()
 
thread = Thread(target=eventListeners, daemon=True)
thread.start()

# functions handling start/ stop of recordings
keyboard = Controller()
keylog = False
start_time = None
output_file_name = None
def start_logging(keylog_file_name):
    global start_time, output_file_name, keylog
    keylog = True
    start_time = time()
    output_file_name = keylog_file_name

def stop_logging():
    global start_time, output_file_name, keylog
    keylog = False
    start_time = None
    output_file_name = None

def simulate_keys(record):
    for key in record: 
        if len(key.split(".")) > 1:
            keycode = getattr(Key, key.split('.')[1])
        else :
            keycode = key[0]
        keyboard.press(keycode)
    
    for key in record: 
        if len(key.split(".")) > 1:
            keycode = getattr(Key, key.split('.')[1])
        else :
            keycode = key[0]
        keyboard.release(keycode)

def start_delayed():
    global simulating_keys
    simulating_keys = False
    file_name = getFileName()
    start_logging(file_name)
    playStop_button.config(image=stopicon)

def stop_delayed():
    global simulating_keys
    simulating_keys = False
    stop_logging()
    playStop_button.config(image=playicon)

recording = False
def start_record():
    global keylog, start_time, recording, simulating_keys
    settings_data = retreive_data()
    if not settings_data:
        setting_prompt()
        return
    output = settings_data['output_folder']
    record = settings_data['record_shortcut']
    fps = settings_data['fps']
    delay = settings_data['delay']
    if output == "None" or record == "None" or fps == "" or delay == "":
        setting_prompt()
        return
    record = record.split("+")
    for index, key in enumerate(record):
        record[index] = unfilter(key)

    simulating_keys = True
    simulate_keys(record)
    recording = True
    wait_for_keys_to_be_pressed = Timer(delay, start_delayed)
    wait_for_keys_to_be_pressed.start()
    
def stop_record():
    global recording, simulating_keys
    settings_data = retreive_data()
    if not settings_data:
        return
    record = settings_data['record_shortcut']
    if record == "None":
        return
    record = record.split("+")
    for index, key in enumerate(record):
        record[index] = unfilter(key)
    
    simulating_keys = True
    simulate_keys(record)
    recording = False
    wait_for_keys_to_be_pressed = Timer(1, stop_delayed)
    wait_for_keys_to_be_pressed.start()

def toggleRecord():
    if recording:
        stop_record()
    else:
        start_record()

# root config 
root = Tk()
root.title("keystrokes recorder")
root.geometry("450x250")
root.maxsize(450,250)
root.minsize(450,250)
root.config(bg='#3F403F')

playicon = PhotoImage(file='play-button-svgrepo-com.png').subsample(2)
stopicon = PhotoImage(file='stop-svgrepo-com.png').subsample(2)
settingsicon = PhotoImage(file='settings-svgrepo-com.png').subsample(2)

# creating button for play/pause
playStop_button = Button(root, command=toggleRecord, image=playicon, width=450/2, height=250, cursor='hand2')
playStop_button.grid(column=0, row=0)

#SETTINGS
def open_settings():
    global settings_window, shortcut_label, record_shortcut_label, fps_entry, output_dir_label, delay_entry
    # root config 
    settings_window = Toplevel()
    settings_window.title("Settings")
    settings_window.geometry("1050x275")
    settings_window.config(bg='#3F403F')

    #widgets
    shortcut_label = Label(settings_window, text="None", font='Arial 10', bg='#3F403F', fg="white")
    shortcut_label.grid(row=0, column=0, padx=10, pady=10)
    shortcut_button = Button(settings_window, command=lambda: key_shortcut(shortcut_label, shortcut_button), width=20, text="Set Keybind for Quick Start", cursor='hand2')
    shortcut_button.grid(row=0, column=1, pady=10)

    record_shortcut_label = Label(settings_window, text="None", font='Arial 10', bg='#3F403F', fg="white")
    record_shortcut_label.grid(padx=10, pady=10)
    record_shortcut_button = Button(settings_window, command=lambda: key_shortcut(record_shortcut_label, record_shortcut_button), text="change shortcut to start recording from your recording software:", cursor='hand2', width=50)
    record_shortcut_button.grid(row=1, column=1, pady=10)
    
    #fps
    fps_label = Label(settings_window, text="Set Keylog Frame Rate Limit (keep it in sync with your recording software for consistency)", font='Arial 10', bg='#3F403F', fg="white")
    fps_label.grid(padx=10, pady=10)
    fps_entry = Entry(settings_window, width=5)
    fps_entry.grid(column=1, row=2,pady=10)
    fps_entry.bind("<Return>", saveSettingsAndUnfocus)
    
    tip = Label(settings_window, text="Brotip: close your recording software or remove the keybind for recording so that it does not accidently record!", font='Arial 10', bg='#3F403F', fg="#32746D")
    tip.grid(column=0, row=3, pady=10)

    output_dir_label = Label(settings_window, text=r"None", font='Arial 10', bg='#3F403F', fg="white", wraplength=300)
    output_dir_label.grid(row=4, column=0)
    output_Button = Button(settings_window, command=open_folder_dialog, text="Select Output Folder for keylog files", font='Arial 10', bg='white', cursor='hand2')
    output_Button.grid(row=4, column=1, pady=10)

    #delay
    delay_label = Label(settings_window, text="Adjust Recording Start Delay offset", font='Arial 10', bg='#3F403F', fg="white")
    delay_label.grid(padx=10, pady=10, row=5, column=0)
    delay_entry = Entry(settings_window, width=5)
    delay_entry.grid(column=1, row=5,pady=10)
    delay_entry.bind("<Return>", saveSettingsAndUnfocus)

    settings_data = retreive_data()
    if settings_data:
        shortcut_label.config(text=settings_data['shortcut_to_start'])
        record_shortcut_label.config(text=settings_data['record_shortcut'])
        fps_entry.insert(0, settings_data['fps'])
        output_dir_label.config(text=settings_data['output_folder'])
        delay_entry.insert(0, settings_data['delay'])

settings_button = Button(root, command=open_settings, image=settingsicon, width=450/2, height=250, cursor='hand2')
settings_button.grid(column=1, row=0)

# close functions
checkbox_var = IntVar(value=True)
def close():
    if checkbox_var.get() == 1 and recording:
        stop_record()
    root.destroy()

def cancel(close_prompt):
    close_prompt.destroy()

def close_prompt():
    close_prompt = Toplevel()
    close_prompt.title("Sure?")
    close_prompt.geometry("550x200")
    close_prompt.maxsize(550,200)
    close_prompt.minsize(550,200)
    close_prompt.config(bg='#3F403F')

    text = Label(close_prompt, font='Arial 10', bg='#3F403F', fg="white", text="Are you sure you want to close this program?")
    text1 = Label(close_prompt, font='Arial 10', bg='#3F403F', fg="white", text="This will stop the keylog recording and you will have to open this program again to record!")
    text2 = Button(close_prompt, font='Arial 10', bg='#3F403F', fg="white", text="Cancel", cursor="hand2", command=lambda: cancel(close_prompt)) 
    text3 = Button(close_prompt, font='Arial 10', bg='#3F403F', fg="white", text="Close", cursor="hand2", command=close)
    checkbox = Checkbutton(close_prompt, text="Stop video recording upon exit", variable=checkbox_var)

    text.pack(pady=5, padx=15)
    text1.pack(pady=5, padx=15)
    checkbox.pack(side="bottom", padx=10)
    text2.pack(pady=5, side="left", padx=150)
    text3.pack(pady=5, side="left", padx=0)

def on_closing():
    close_prompt()

root.protocol("WM_DELETE_WINDOW", on_closing)

# running the thing
root.mainloop()



