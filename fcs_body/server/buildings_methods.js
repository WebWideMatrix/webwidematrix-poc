

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
    },

    "getBldgContent": function (addr) {
        console.log("Answering call to method getBldgContent");
        if (!addr) return {};
        console.log("Sending content of bldg at " + addr);
        var result = Redis.matching(addr);
        console.log(result);
        return result;
    }

});
