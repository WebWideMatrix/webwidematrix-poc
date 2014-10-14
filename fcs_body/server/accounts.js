Accounts.onCreateUser(function (options, user) {

    console.log(JSON.stringify(options));

    user.createdAt = new Date();

    user.profile = getUserDetails(user);

    var userPayload = _.pick(user.profile,
        "name",
        "email",
        "url",
        "picture",
        "blog",
        "location",
        "avatar_url"
    );

    var bldg = createBldg(INITIAL_FLOOR, null, USER_CONTENT_TYPE, userPayload);
    var rsdt = createRsdt(bldg);

    user.bldg = {
        _id: bldg._id,
        address: bldg.address
    };
    user.residents = [rsdt._id];

    return user;
});


var getUserDetails = function(options, user) {
    var profile = options.profile || {};
    if (user.services.twitter) {
        profile = getUserDetailsFromTwitter(user);
    }
    return profile;
};

var getUserDetailsFromTwitter = function(user) {
    var accessToken = user.services.twitter.accessToken,
        result,
        profile;

    result = Meteor.http.get("https://api.twitter.com/1.1/account/verify_credentials.json", {
        params: {
            access_token: accessToken
        }
    });

    console.log('twitter: ' + result.data);

    if (result.error)
        throw result.error;

    profile = _.pick(result.data,
        "login",
        "name",
        "avatar_url",
        "picture",
        "url",
        "company",
        "blog",
        "location",
        "email");

    return profile;
};