

Meteor.methods({
    "getBldgAddressByKey": function(key) {
        var userBldgAddress = getCurrentUserBldgAddress();
        var bldg = Buildings.findOne({
            flr: userBldgAddress + "-l0",
            key: key
        });
        if (bldg) {
            return bldg.address;
        }
        else {
            return null;
        }
    }
})
