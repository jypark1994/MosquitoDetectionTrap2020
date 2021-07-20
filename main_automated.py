import cv2
import os
import numpy as np
import copy
import serial
import time
import argparse
import sys
import subprocess
import atexit



parser = argparse.ArgumentParser()
parser.add_argument('--interval', '-i', type=int, default=60)
parser.add_argument('--location', '-l', type=str, default="test")
args = parser.parse_args()

date = time.strftime("%Y%m%d",time.localtime(time.time()))
time_stamp = time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time()))
image_root = f"images/{date}_{args.location}"
os.makedirs(image_root, exist_ok=True)
sys.stdout = open(f"{image_root}/log_{date}.txt", "a")

@atexit.register
def goodbye():
    print(f"\n\n========== Finished working at {time_stamp} ==========\n\n")

print(f"\n\n========== Start logging at {time_stamp} ==========\n\n")

def fitImagingArea(img, thr=240, target_size=2000):

    img_bw = cv2.cvtColor(copy.deepcopy(img), cv2.COLOR_BGR2GRAY)
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
    try:
        tf_matrix = cv2.getPerspectiveTransform(original_transform, target_transform)
        img_transformed = cv2.warpPerspective(img, tf_matrix, (target_size,target_size))
        return img_transformed
    except:
        print("Error occured in cv2.getPerspectiveTransform")
        print("Shape of original transform", original_transform.shape)
        print("Shape of target transform", target_transform.shape)
        assert "="*20
        return None
    

    


# Show camera properties
print("- Available Devices")
print(subprocess.check_output("v4l2-ctl -d /dev/video0 --list-devices",shell=True).decode('utf-8'))
print("- Available Parameters")
print(subprocess.check_output("v4l2-ctl -d /dev/video0 --list-ctrls",shell=True).decode('utf-8'))

# # Set camera parameters
print(subprocess.check_output("v4l2-ctl --set-ctrl=white_balance_red_component=130",shell=True).decode('utf-8')) # 130
print(subprocess.check_output("v4l2-ctl --set-ctrl=white_balance_blue_component=160",shell=True).decode('utf-8')) # 160
print(subprocess.check_output("v4l2-ctl --set-ctrl=gain=90",shell=True).decode('utf-8')) # 64
print(subprocess.check_output("v4l2-ctl --set-ctrl=exposure_absolute=90",shell=True).decode('utf-8')) # 45
# (gain, exp) = (64, 45), (80, 80)

# cv2.namedWindow('image',cv2.WINDOW_NORMAL)
# cv2.resizeWindow('image', 1024,1024)

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

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        raise IOError("Cannot open camera")

    cam_width, cam_height = (4896, 3672) # Full: (4896, 3672), Crop: (3840, 2160)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    
    ser.write("b".encode()) # Indution
    print(f"== Waiting for mosquitoes ({args.interval}[sec])")
    time.sleep(args.interval) # Wait for [Interval] seconds

    print("== Taking an image ==")
    ret, frame = cap.read()
    time.sleep(5)

    if (np.shape(frame) == ()):
        print("Failed to receive an image from camera")
        ser.write("b".encode()) # Indution
        time.sleep(5)
        del frame
        continue
    
    # cv2.imshow("image", frame)
#   frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    time_stamp = time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time()))
    image_name_cropped = f"mark2_{time_stamp}_cropped.jpg"
    image_name_origin = f"mark2_{time_stamp}_original.jpg"
    path_crop = os.path.join(image_root, image_name_cropped)
    path_origin = os.path.join(image_root, image_name_origin)
    

    crop_frame = fitImagingArea(frame)

    if crop_frame.any() == None:
        continue
        
    cv2.imwrite(path_crop, crop_frame)
    cv2.imwrite(path_origin, frame)

    print(f"Image saved to {path_origin}")
    time.sleep(2)
    # Drop mosquitoes
    ser.write("d".encode())
    time.sleep(2)
    print("Drop mosquitoes done.")

    ser.write("b".encode()) # Stop
    
    del frame, crop_frame, cap
