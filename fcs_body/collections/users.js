getCurrentUserBldgAddress = function () {
    var userBldg = Meteor.user().bldg;
    return userBldg.address;
};
