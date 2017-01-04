import usb.core
import usb.util
import sys
import time

class UsbFinder(object):

    devs = {}
    USB_REMOVED = -1
    USB_NOT_CHANGED = 0
    USB_ADDED = 1

    def __init__(self):

        self.devs = self.list_usbs()

    def list_usbs(self):

        devs = usb.core.find(find_all=True)

        usb_drives = {}
        for dev in devs:
            for cfg in dev:
                for intf in cfg:
                    if dev.bDeviceClass == 0 and intf.bInterfaceClass == 8:
                        usb_drives[(dev.idVendor, dev.idProduct)] = dev

        return usb_drives

    def usb_changed(self):

        usb_drives = self.list_usbs()
        if len(usb_drives) > len(self.devs):
            self.devs = usb_drives
            return self.USB_ADDED
        elif len(usb_drives) < len(self.devs):
            self.devs = usb_drives
            return self.USB_REMOVED

        self.devs = usb_drives
        return self.USB_NOT_CHANGED
