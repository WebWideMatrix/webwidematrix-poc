
Template.glassDoor.helpers({
    today: function() {
        return formatDate(new Date());
    }
});


Template.glassDoor.events({
    "click .enter-button": function() {
        var key = formatDate(new Date());
        Meteor.call("getBldgAddressByKey", key, function(err, data) {
            if (err) {
                // TODO handle errors, such as no bldg
                console.log(err);
            }
            if (data) {
                // TODO use router
                redirectTo(data + "-l0");
            }
            else {
                $("#error").text("No data yet, please try again soon..");
            }
        });
    }
});
