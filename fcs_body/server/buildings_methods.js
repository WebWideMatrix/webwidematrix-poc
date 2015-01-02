

Meteor.methods({
    "getBldgAddressByKey": function(key) {
        var userBldgAddress = getCurrentUserBldgAddress();
        var query = {
            flr: userBldgAddress + "-l0",
            key: key
        };
        var bldg = Buildings.findOne(query);
        if (bldg) {
            return bldg.address;
        }
        else {
            return null;
        }
    }
});
