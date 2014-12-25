
Meteor.publish("userData", function () {
    return Meteor.users.find({_id: this.userId},
        {fields: {'bldg': 1, 'profile': 1}});
});

Meteor.publish("buildings", function (flr) {
    if (!flr) {
        var userAddress = getCurrentUserBldgAddress();
        flr = userAddress + "-l0";
    }
    return Buildings.find({flr: flr});
});
