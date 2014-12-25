
Template.glassDoor.helpers({
    today: function() {
        return formatDate(new Date());
    },
    userAddress: function() {
        return getCurrentUserBldgAddress() + "-l0";
    }
});


Template.glassDoor.events({

});