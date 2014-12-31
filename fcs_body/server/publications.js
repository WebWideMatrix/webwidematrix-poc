
Meteor.publish("userData", function () {
    return Meteor.users.find({_id: this.userId},
        {fields: {'bldg': 1, 'profile': 1}});
});

Meteor.publish("buildings", function (addr) {
    if (!addr) {
        var userAddress = getCurrentUserBldgAddress();
        addr = userAddress + "-l0";
    }
    else {
        var parts = addr.split("-");
        if (parts[parts.length - 1].substring(0, 1) == "b") {
            // looking at a bldg, so publish all bldgs in its flr
            parts.pop();
            addr = parts.join("-");
        }
    }
    return Buildings.find({flr: addr});
});
