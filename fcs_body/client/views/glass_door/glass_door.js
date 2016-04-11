
Template.glassDoor.helpers({
    today: function() {
        return formatDate(new Date());
    }
});

var tryOpenToday = function() {
    // assuming the user is logged in
    var userId = Meteor.userId();
    var key = buildUserCurrentBldgCacheKey(userId);
    var addr = Redis.get(key);

//    redirectTo(addr + "-l0", "/current/");    unfortunately, redis-livedata has issues,
//                                              so we're not using the work cache for UI
    redirectTo(addr + "-l0");
};

Template.glassDoor.events({
    "click .enter-button": function() {
        tryOpenToday();
    }
});
