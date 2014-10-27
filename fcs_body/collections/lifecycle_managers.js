LifecycleManagers = new Meteor.Collection('lifecycle_managers');


createLifecycleManager = function(bldg, dataPipe) {


    var _createLifecycleManager = function() {
        return {
            type: "DailyFeedDispatcher",
            bldg: bldg._id,
            dataPipe: dataPipe._id,
            schedule: {
                minutes: 0,
                hours: 0
            }
        }
    };

    return LifecycleManagers.insert(_createLifecycleManager());

};
