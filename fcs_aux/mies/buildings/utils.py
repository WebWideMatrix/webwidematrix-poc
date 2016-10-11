import contextlib
from math import sqrt

import time


def get_flr(addr):
    parts = addr.split("-")
    if parts[-1][0] == "b":
        parts.pop()
        addr = "-".join(parts)
    return addr


def get_flr_level(flr_addr):
    parts = flr_addr.split("-")
    level_str = parts[-1][1:]
    return int(level_str)


def get_bldg(addr):
    """
    TODO rename coz the name may be misleading
    return the part of the address representing
    the current bldg, i.e., removes the flr if existing
    :param addr:
    :return:
    """
    parts = addr.split("-")
    if parts[-1][0] == "l":
        parts.pop()
        addr = "-".join(parts)
    return addr


def get_containing_bldg_address(addr):
    parts = addr.split("-")
    parts.pop()
    # if it's a flr, get out to the containing bldg
    if parts[-1][0] == "l":
        parts.pop()
    return "-".join(parts)


def extract_bldg_coordinates(bldg_addr):
    parts = bldg_addr.split("-")
    if len(parts) <= 1:
        # ground level, no coordinates
        return None
    part = parts[-1]
    if part[0] != "b":
        bldg_addr = get_bldg(bldg_addr)
        parts = bldg_addr.split("-")
        part = parts[-1]
    coords = part[2:-1].split(",")
    return int(coords[0]), int(coords[1])


def replace_bldg_coordinates(bldg_addr, x, y):
    parts = bldg_addr.split("-")
    if len(parts) <= 1:
        # ground level, no coordinates
        return bldg_addr
    flr = ""
    if parts[-1][0] != "b":
        flr = parts.pop()
    parts.pop()
    part = "b({x},{y})".format(x=x, y=y)
    parts.append(part)
    if flr:
        parts.append(flr)
    return "-".join(parts)


def replace_flr_level(bldg_addr, flr_level):
    parts = bldg_addr.split("-")
    if len(parts) <= 2:
        # ground level, no coordinates
        return bldg_addr
    bldg = ""
    if parts[-1][0] == "b":
        bldg = parts.pop()
    parts.pop()
    part = "l{flr}".format(flr=flr_level)
    parts.append(part)
    if bldg:
        parts.append(bldg)
    return "-".join(parts)


def get_bldg_containers(bldg_addr, include_flrs=True):
    containers = []
    parts = bldg_addr.split("-")
    while len(parts) > 1:
        parts.pop()
        if not include_flrs and parts[-1][0] == "l":
            parts.pop()
        containers.append("-".join(parts))
    return containers


def calculate_distance(addr1, addr2):
    x1, y1 = extract_bldg_coordinates(addr1)
    x2, y2 = extract_bldg_coordinates(addr2)
    if not all([x is not None for x in (x1, y1, x2, y2)]):
        return 0
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)


@contextlib.contextmanager
def time_print(logging, task_name):
    t = time.time()
    try:
        yield
    finally:
        logging.debug("{} took {} seconds".format(task_name, time.time() - t))
