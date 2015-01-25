
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
            // TODO use router
            redirectTo("/buildings/" + data + "-l0", "_top");
        });
    }
});
