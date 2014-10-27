DataPipes = new Meteor.Collection('data_pipes');

var DEFAULT_FETCH_INTERVAL = 10;


createDataPipe = function(tokens) {

    var _getSchedule = function() {
        var d = new Date();
        var m = d.getMinutes();
        return m % DEFAULT_FETCH_INTERVAL;
    };

    var _createDataPipe = function() {
        return {
            type: "PersonalTwitterFeed",
            schedule: _getSchedule(),
            tokens: tokens,
            latestId: null,
            connectedBldg: null
        }
    };

    return DataPipes.insert(_createDataPipe());

};
