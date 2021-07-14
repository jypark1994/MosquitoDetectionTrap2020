import cv2
import os
import numpy as np
import copy
import serial
import time

def fitImagingArea(img, thr=240, target_size=2000):

    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_th = cv2.threshold(img_bw, thr, 255 , cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(img_th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    max_idx = 0

    for idx, c in enumerate(cnts):
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            max_idx = idx

    max_ctr = cnts[max_idx]

    eps = 0.1*cv2.arcLength(max_ctr, True)

    apx = cv2.approxPolyDP(max_ctr, eps, True)

    original_transform = np.float32(apx)
    target_transform = np.float32([[0,0],[0,target_size],[target_size,target_size],[target_size,0]])

    tf_matrix = cv2.getPerspectiveTransform(original_transform, target_transform)
    img_transformed = cv2.warpPerspective(img, tf_matrix, (target_size,target_size))

    return img_transformed

target_folder = './Captured'

os.makedirs(target_folder, exist_ok=True)

# Show camera properties
print("- Available Devices")
os.system("v4l2-ctl -d /dev/video0 --list-devices")
print("- Available Parameters")
os.system("v4l2-ctl -d /dev/video0 --list-ctrls")

# # Set camera parameters
os.system("v4l2-ctl --set-ctrl=white_balance_red_component=130") # 130
os.system("v4l2-ctl --set-ctrl=white_balance_blue_component=160") # 160
os.system("v4l2-ctl --set-ctrl=gain=90") # 64
os.system("v4l2-ctl --set-ctrl=exposure_absolute=90") # 45
# (gain, exp) = (64, 45), (80, 80)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise IOError("Cannot open camera")

cam_width, cam_height = (4896, 3672) # Full: (4896, 3672), Crop: (3840, 2160)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
area = cam_height/2

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 1024,1024)

ser = serial.Serial("/dev/ttyACM0", 9600)
while not ser.readable():
    print("Awaiting Serial Connection ...")
    
time.sleep(3)

ser.write('sl'.encode()) # Run top fan


# ---- Camera Calibration ---- #
# x_offset = 490
# y_offset = 760
# scale = 0.6

# def img_transfer(img, height ,width, x_offset, y_offset, scale):

#     area = int((h//2) * scale)
#     img_crop = copy.deepcopy(img[ h//2 - area - y_offset : h//2 + area - y_offset, \
#                         w//2 - area + x_offset : w//2 + area + x_offset, \
#                         :])

#     return img_crop

while True:
    ret, frame = cap.read() 
    
    cv2.imshow("image", frame)

    cmd = cv2.waitKey(1)

    if cmd == 73 or cmd == 105: # 'I'nput mosquitoes
        ser.write("b".encode())

    elif cmd == 70 or cmd == 102: # 'D'rop mosquitoes
        ser.write("d".encode())
        time.sleep(3)
        print("Drop mosquitoes done.")


    elif cmd == 83 or cmd == 115: # 'S'hoot mosquitoes
        print("Read the frame")
#         frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        time_stamp = time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time()))
        image_name = f"mark2_{time_stamp}_original.jpg"
        image_name_cropped = f"mark2_{time_stamp}_cropped.jpg"
        path = os.path.join(target_folder, image_name)

        crop_frame = fitImagingArea(frame)
        cv2.imwrite(path, frame)
        cv2.imwrite(image_name_cropped, crop_frame)
        print(f"Image saved to {image_name}")
    elif cmd == 85 or cmd == 117:
        print("Turn Left")
        ser.write("u".encode())
        time.sleep(3)
    elif cmd == 79 or cmd == 111:
        print("Turn Right")
        ser.write("o".encode())
        time.sleep(3)
    elif cmd == 69 or cmd == 101: # Escape Key
        ser.write("e".encode())
        cv2.destroyAllWindows()
        cap.release()
        ser.close()
        exit()
