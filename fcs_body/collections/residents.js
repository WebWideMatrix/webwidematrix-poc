Residents = new Meteor.Collection('residents');


createRsdt = function(bldg, callback) {

    var _createRsdt = function() {
        return {
            type: "ContentVisualizer",
            bldg: bldg._id,
            processing: false,
            acceleration: null,
            velocity: null,
            location: bldg.address,
            energy: DEFAULT_ENERGY,
            status: "active"
        };
    };

    Residents.insert(_createRsdt(), callback);
};
