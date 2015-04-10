from mies.buildings.utils import extract_bldg_coordinates
from mies.mongoconfig import get_db


def occupy_bldg(resident, bldg):
    curr_location = resident["location"]
    x, y = extract_bldg_coordinates(curr_location)
    new_x, new_y = bldg["x"], bldg["y"]
    velocity = [new_x - x, new_y - y]
    db = get_db()
    db.residents.update(
        {"_id": resident["_id"]},
        {
            "$set":
            {
                "bldg": bldg["_id"],
                "location": bldg["address"],
                "velocity": velocity
            }
        })


def occupy_empty_address(resident, addr):
    curr_location = resident["location"]
    x, y = extract_bldg_coordinates(curr_location)
    new_x, new_y = extract_bldg_coordinates(addr)
    velocity = [new_x - x, new_y - y]
    db = get_db()
    db.residents.update(
        {"_id": resident["_id"]},
        {
            "$set":
            {
                "bldg": None,
                "location": addr,
                "velocity": velocity
            }
        })
