Accounts.onCreateUser(function (options, user) {

    console.log(JSON.stringify(options));

    user.createdAt = new Date();

    user.profile = getUserDetails(options, user);
    console.log(JSON.stringify(user));

    var tokens = {
        accessToken: user.services.twitter.accessToken,
        accessTokenSecret: user.services.twitter.accessTokenSecret
    };

    var bldg = createBldg(INITIAL_FLOOR, null, USER_CONTENT_TYPE, user.profile);
    var dataPipe = createDataPipe(tokens);
    var lifecycleManager = createLifecycleManager(bldg, dataPipe);
//    var rsdt = createRsdt(bldg);

    user.bldg = {
        _id: bldg._id,
        address: bldg.address
    };
    user.dataPipes = [dataPipe._id];
    user.lifecycleManagers = [lifecycleManager._id];
//    user.residents = [rsdt._id];

    return user;
});


var getUserDetails = function(options, user) {
    var profile = options.profile || {};
    if (user.services.twitter) {
        profile = getUserDetailsFromTwitter(profile, user);
    }
    return profile;
};

var getUserDetailsFromTwitter = function(profile, user) {
    console.log(user.services.twitter);
    profile.language = user.services.twitter.lang;
    profile.picture = user.services.twitter.profile_image_url;
    profile.screenName = user.services.twitter.screenName;

    return profile;
};