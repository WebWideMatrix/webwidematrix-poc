

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
