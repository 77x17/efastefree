import cv2
import time
import subprocess
from PIL import Image
  
run     = True
N_EXIT  = 7
N_ARROW = 2


def run_command(command):
    subprocess.run(command, shell=True, text=True)


def take_screenshot(width = 1080, height = 1920):
    run_command("adb shell screencap /sdcard/Pictures/screenshot.raw && adb pull /sdcard/Pictures/screenshot.raw")
    
    bytespp = 4

    with open('screenshot.raw', 'rb') as file:
        raw_data = file.read(width * height * bytespp)

    img_bytes = bytearray(raw_data)

    img = Image.frombytes('RGBA', (width, height), bytes(img_bytes), 'raw')

    img.save('screenshot.png', 'PNG')


def findLocation(input_png, click = True):
    img_rgb  = cv2.imread('screenshot.png')
    template = cv2.imread(input_png)

    img_rgb  = cv2.resize(img_rgb, (0, 0), fx=0.5, fy=0.5)
    template = cv2.resize(template, (0, 0), fx=0.5, fy=0.5)

    res       = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
 
    if max_val >= threshold:
        x, y = max_loc

        if click:            
            run_command(f"adb shell input tap {2 * x + template.shape[0]} {2 * y + template.shape[1]}")
            #print(2 * x + template.shape[0], 2 * y + template.shape[1])
            
        return True

    return False


def efast_efree():
    time.sleep(1)
    take_screenshot()

    #print("go")
    if findLocation("go.png"):
        take_screenshot()

    #print("ok")
    if findLocation("ok.png", False):
        if findLocation("limit.png"):
            global run
            run = False

        findLocation("ok.png")

        take_screenshot()
        
        return

    #print("equation")
    while findLocation("equation.png"):
        take_screenshot()

    #print("------------------------------------\nads")
    
    for i in range(1, N_ARROW + 1):
        if findLocation(f"arrow_{i}.png"):
            time.sleep(1)
            take_screenshot()

    for i in range(1, N_EXIT + 1):
        if findLocation(f"exit_{i}.png"):
            time.sleep(1)
            take_screenshot()

    take_screenshot(1920, 1080)

    for i in range(1, N_ARROW + 1):
        if findLocation(f"arrow_{i}.png"):
            time.sleep(1)
            take_screenshot()

    for i in range(1, N_EXIT + 1):
        if findLocation(f"exit_{i}.png"):
            time.sleep(1)
            take_screenshot(1920, 1080)


if __name__ == '__main__':
    print("Begin at: {}".format(time.strftime("%H:%M:%S", time.localtime())))
    take_screenshot()
    
    cnt = 0
    while True:
        run = True
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")

        while run:
            efast_efree()

        run_command("adb shell am force-stop com.efast.efree")
        
        run_command("adb shell am start -n com.termux/.app.TermuxActivity")
        
        cnt = cnt + 1
        print("------------------------")
        print("Running count =", cnt)
        print("Stop at: {}".format(time.strftime("%H:%M:%S", time.localtime())))
        print("Sleep time.........")
        print("------------------------")
        time.sleep(3600)
