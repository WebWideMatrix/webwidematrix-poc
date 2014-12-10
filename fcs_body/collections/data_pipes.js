DataPipes = new Meteor.Collection('data_pipes');


createDataPipe = function(tokens, callback) {

    var _getSchedule = function() {
        // assuming a fixed 10 min interval for now
        var d = new Date();
        var m = d.getMinutes();
        return {
            minutes_offset: m % 10
        };
    };

    var _createDataPipe = function() {
        return {
            type: "PersonalTwitterFeed",
            status: "active",
            schedule: _getSchedule(),
            tokens: tokens,
            latestId: null,
            connectedBldg: null,
            frequency: null
        }
    };

    DataPipes.insert(_createDataPipe(), callback);
};
