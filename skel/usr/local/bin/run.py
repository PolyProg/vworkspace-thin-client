#!/usr/bin/env python3

import logging
import os
from subprocess import call, check_call, check_output, DEVNULL, CalledProcessError
import sys
import time


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"

logger = logging.getLogger(__name__)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;{}m"
BOLD_SEQ = "\033[1m"


class ColoredFormatter(logging.Formatter):
    AVAILABLE_COLORS = {
        name: COLOR_SEQ.format(index + 30)
        for index, name in enumerate(["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"])
        }

    DEFAULT_LEVEL_COLORS = {
        'WARNING': "YELLOW",
        'INFO': "WHITE",
        'DEBUG': "CYAN",
        'ERROR': "RED"
    }

    def __init__(self, fmt, datefmt=None, level_colors=None):
        fmt = fmt.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
        for color, seq in self.AVAILABLE_COLORS.items():
            fmt = fmt.replace("${}".format(color), seq)

        super().__init__(fmt, datefmt, "{")

        if level_colors is None:
            level_colors = self.DEFAULT_LEVEL_COLORS

        self.level_colors = level_colors

    def format(self, record):
        fmt = self._fmt.replace("$LEVEL", self.AVAILABLE_COLORS[self.level_colors[record.levelname]])
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()
        return fmt.format(**record.__dict__)


def setup_logging():
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = ColoredFormatter("[$BLACK{asctime}$RESET] $LEVEL{message}$RESET", '%H:%M:%S')
    handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def check_env_sanity():
    missing = [val for val in ["ACCESS_POINT", "ROOT_PASSWORD", "WIFI_PASSWORD"] if not os.environ.get(val)]

    if missing:
        logger.error("These environment variables are missing. Is your `/etc/setup.env` correct ?")

        for m in missing:
            logger.error("\t{}".format(m))

        logger.error("Environment not sane, aborting.")
        input("Press any key to continue")
        exit(1)


def set_root_password():
    check_call("echo root:{} | chpasswd --encrypted".format(os.environ.get("ROOT_PASSWORD")), shell=True)


def check_wifi_availability():
    logger.info("Checking wifi availability ...")

    available_wifis = []
    output = check_output(["nmcli", "device", "show"]).decode().split("\n\n")
    for entry in output:
        network = entry.split("\n")

        for line in network:
            if line.startswith("GENERAL.TYPE") and "wifi" in line:
                available_wifis.append(network[0].split(" ")[-1])

    if available_wifis:
        logger.info("Found following interfaces supporting wifi : {}".format(",".join(available_wifis)))
        logger.info("It is very likely your laptop will work when at EPFL")
    else:
        logger.error("No interface with wifi support was found. Please contact a staff member.")
        exit(1)


def check_laptop_is_charging():
    logger.info("Checking whether a power source is plugged in ...")
    while True:
        info = check_output(["acpi", "-b"]).decode()

        if "Discharging" in info:
            logger.warning("Your laptop is discharging. You should plug it in")

            while True:
                res = input("Do you want to recheck if your laptop is charging ? [Y/n]").lower()
                if res == "y" or res == "":
                    break
                elif res == "n":
                    return
                else:
                    print("Invalid answer. Got {}".format(res))
        else:
            break


def check_connected_to_internet():
    logger.info("Checking internet connection ...")

    for i in range(10):
        try:
            check_call(["nmcli", "device", "wifi", "connect", os.environ.get("ACCESS_POINT"), "password", os.environ.get("WIFI_PASSWORD")])
        except CalledProcessError:
            logger.warning("[{}/10] error connecting to wifi, waiting a bit to discover SSID".format(i))
            time.sleep(5)
        else:
            break
    else:
        logger.error("Could not connect to wifi")
        check_wifi_availability()


def main():
    setup_logging()
    logger.info("System up, launching setup")
    check_env_sanity()
    set_root_password()
    check_connected_to_internet()
    check_laptop_is_charging()
    input("Press any key to continue")
    call('su liveuser -c "xinit"', shell=True)


if __name__ == '__main__':
    main()
