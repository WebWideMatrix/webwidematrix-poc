Accounts.onCreateUser(function (options, user) {

    var INITIAL_RESIDENTS_PER_USER = 10;

    console.log(JSON.stringify(options));

    user.createdAt = new Date();

    user.profile = getUserDetails(options, user);

    var tokens = {
        accessToken: user.services.twitter.accessToken,
        accessTokenSecret: user.services.twitter.accessTokenSecret
    };

    var wrappedCreateBldg = Async.wrap(createBldg);
    var bldgId = wrappedCreateBldg(INITIAL_FLOOR, user.profile.screenName, null,
        USER_CONTENT_TYPE, user.profile);
    var bldg = Buildings.findOne({_id: bldgId});

    var wrappedCreateDataPipe = Async.wrap(createDataPipe);
    var dataPipeId = wrappedCreateDataPipe(tokens);
    var wrappedCreateLifecycleManager = Async.wrap(createLifecycleManager);
    var lifecycleManagerId = wrappedCreateLifecycleManager(bldgId, dataPipeId);
    var wrappedCreateRsdt = Async.wrap(createRsdt);
    var residents = [];
    for (var i = 0; i < INITIAL_RESIDENTS_PER_USER; i++) {
        var rsdtId = wrappedCreateRsdt(initialResidentName(user.profile, i), bldg);
        residents.push(rsdtId);
    }

    user.bldg = {
        _id: bldgId,
        address: bldg.address
    };
    user.dataPipes = [dataPipeId];
    user.lifecycleManagers = [lifecycleManagerId];
    user.residents = residents;

    return user;
});


getUserDetails = function(options, user) {
    var profile = options.profile || {};
    if (user.services.twitter) {
        profile = getUserDetailsFromTwitter(profile, user);
    }
    return profile;
};

getUserDetailsFromTwitter = function(profile, user) {
    console.log(user.services.twitter);
    profile.language = user.services.twitter.lang;
    profile.picture = user.services.twitter.profile_image_url;
    profile.screenName = user.services.twitter.screenName;

    return profile;
};

initialResidentName = function(profile, i) {
    var chars = "abcdefghijklmnopqrstuvwxyz";
    return (Math.floor((i / chars.length)) + 1) + chars.charAt((i % chars.length)) + ' ' + profile.screenName;
};
