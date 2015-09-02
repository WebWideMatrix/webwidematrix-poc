Residents = new Meteor.Collection('residents');


createRsdt = function(name, bldg, callback) {

    var _createRsdt = function() {
        return {
            name: name,
            type: "ContentVisualizer",
            bldg: bldg._id,
            processing: false,
            acceleration: null,
            velocity: null,
            location: bldg.address,
            energy: DEFAULT_ENERGY,
            status: "active",
            movesWithoutSmell: 0
        };
    };

    Residents.insert(_createRsdt(), callback);
};
