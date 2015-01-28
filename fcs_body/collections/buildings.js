Buildings = new Meteor.Collection('buildings');

//
// DB involving functions
//

createBldg = function(flr, key, near, contentType, payload, callback) {
    var x = 0,
        y = 0,
        address = buildBldgAddress(flr, x, y),
        nearLookupsCount = 0,
        proximity = PROXIMITY,
        foundSpot = false;

    var findSpot = function() {
        if (near) {
            nearLookupsCount++;
            // have we almost exhausted the near by spots?
            if (nearLookupsCount > Math.pow((2 * proximity), 2)) {
                // if so, extend the lookup area
                proximity *= 2;
            }
            x = randomNumber(near.x - proximity, near.x + proximity);
            y = randomNumber(near.y - proximity, near.y + proximity);
        }
        else {
            x = randomNumber(0, FLOOR_W);
            y = randomNumber(0, FLOOR_H);
        }
        address = buildBldgAddress(flr, x, y);
        var existing = Buildings.findOne({address: address});
        return !existing;
    };

    var _createBldg = function() {
        return {
            address: address,
            flr: flr,
            x: x,
            y: y,
            createdAt: new Date(),
            contentType: contentType,
            payload: payload,
            processed: false,
            occupied: false,
            occupiedBy: null
        };
    };

    while (!foundSpot) {
        foundSpot = findSpot();
    }

    Buildings.insert(_createBldg(), callback);
};

getBldgKey = function(bldgAddr) {
    var bldg = Buildings.findOne({address: bldgAddr});
    if (bldg) {
        return bldg.key;
    }
    else {
        return null;
    }
};

//
//  Non-DB functions
//

buildBldgAddress = function(flr, x, y) {
    return flr + "-b(" + x + "," + y + ")";
};

getFlr = function(addr) {
    var parts = addr.split("-");
    if (parts[parts.length - 1].substring(0, 1) == "b") {
        parts.pop();
        addr = parts.join("-");
    }
    return addr;
};

getBldg = function(addr) {
    var parts = addr.split("-");
    if (parts[parts.length - 1].substring(0, 1) == "l") {
        parts.pop();
        addr = parts.join("-");
    }
    return addr;
};

getContainingBldgAddress = function(addr) {
    var parts = addr.split("-");
    parts.pop();
    // if it's a flr, get out to the containing bldg
    if (parts[parts.length - 1][0] == "l") {
        parts.pop();
    }
    return parts.join("-");
};

extractBldgCoordinates = function(bldgAddr) {
    var parts = bldgAddr.split("-");
    if (parts.length <= 1) {
        // ground level, no coordinated
        return null;
    }
    var part = parts[parts.length - 1];
    if (part[0] != "b") {
        bldgAddr = getBldg(bldgAddr);
        parts = bldgAddr.split("-");
        part = parts[parts.length - 1];
    }
    var coords = part.substring(2, part.length - 1).split(",");
    return [parseInt(coords[0]), parseInt(coords[1])];
};

getBldgLink = function(d) {
    if (d.payload.external_url) {
        return d.payload.external_url;
    }
    else {
        // if no external link, link to the 1st flr of the bldg
        return "/buildings/" + d.address + "-l0";
    }
};
