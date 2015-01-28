LifecycleManagers = new Meteor.Collection('lifecycle_managers');


createLifecycleManager = function(bldgId, dataPipeId, callback) {


    var _createLifecycleManager = function() {
        return {
            type: "DailyFeedDispatcher",
            bldg: bldgId,
            dataPipe: dataPipeId,
            schedule: {
                minutes: 0,
                hours: 0
            }
        }
    };

    LifecycleManagers.insert(_createLifecycleManager(), callback);
};
