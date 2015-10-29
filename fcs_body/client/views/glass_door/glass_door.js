
Template.glassDoor.helpers({
    today: function() {
        return formatDate(new Date());
    }
});

var tryOpenDay = function(n) {
    if (n > 30) {
        $("#error").text("No data yet, please try again soon..");
    }
    else {
        var key = daysAgo(n);
        Meteor.call("getBldgAddressByKey", key, function (err, data) {
                if (err) {
                    // TODO handle errors, such as no bldg
                    console.log(err);
                }
                if (data) {
                    // TODO use router
                    redirectTo(data + "-l0");
                }
                else {
                    n++;
                    Meteor.setTimeout(function() { tryOpenDay(n) }, 100);
                }
            });
    }
};

var tryOpenToday = function() {
    // assuming the user is logged in
    var profileName = Meteor.user().profile.screenName;
    var key = buildUserCurrentBldgCacheKey(profileName);
    var addr = Redis.get(key);

    redirectTo(addr, "/current/");
};

Template.glassDoor.events({
    "click .enter-button": function() {
//        tryOpenDay(0);
        tryOpenToday();
    }
});
