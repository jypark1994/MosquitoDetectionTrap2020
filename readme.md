# Deep learning-based Automatic Mosquito Monitoring Trap

## Setting up external board
- Fetch `trap_control_arduino.ino` on your Arduino board.

## Setting up Jetson NX
- For working with high-bandwidth USB camera, add two lines below on `/boot/extlinux/extlinux.conf`.

```
usb_port_owner_info=2
usbcore.usbfs_memory_mb=1000
```

## Running in manual imaging mode

## Running in automatic imaging mode

`python3 main_automated -i {IMAGING_INTERVAL} -l {NOTATION}`

