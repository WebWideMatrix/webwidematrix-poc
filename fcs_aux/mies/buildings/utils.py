from math import sqrt


def get_flr(addr):
    parts = addr.split("-")
    if parts[-1][0] == "b":
        parts.pop()
        addr = "-".join(parts)
    return addr


def get_bldg(addr):
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
