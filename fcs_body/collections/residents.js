Residents = new Meteor.Collection('residents');


createRsdt = function(name, bldg, userId, userProfileName, callback) {

    var _createRsdt = function() {
        return {
            name: name,
            type: "ContentVisualizer",
            userId: userId,
            userProfileName: userProfileName,
            bldg: bldg._id,
            processing: false,
            acceleration: null,
            velocity: null,
            location: bldg.address,
            flr: bldg.flr,
            energy: DEFAULT_ENERGY,
            status: "active",
            movesWithoutSmell: 0
        };
    };

    Residents.insert(_createRsdt(), callback);
};
