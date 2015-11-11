
// MONGO

Meteor.publish("userData", function () {
    return Meteor.users.find({_id: this.userId},
        {fields: {'bldg': 1, 'profile': 1}});
});

Meteor.publish("buildings", function (addr) {
    var flrAddr,
        bldgAddr;
    if (!addr) {
        bldgAddr = getCurrentUserBldgAddress();
        flrAddr = bldgAddr + "-l0";
    }
    else {
        flrAddr = getFlr(addr);
        bldgAddr = getBldg(addr);
    }
    // publish both flr & its container bldg
    var query = {
        $or: [
            {flr: flrAddr},
            {address: bldgAddr}
        ]
    };
    return Buildings.find(query);
});


// REDIS

Meteor.publish('current', function (addr) {
  if (!addr) return [];
  //  FIXME: validate not asking for too much - always publish just 1 flr
  return Redis.matching(addr + '*');
});

Meteor.publish('userCurrentBldg', function () {
  var user = Meteor.users.findOne({_id: this.userId});
  if (!user) return [];
  var key = buildUserCurrentBldgCacheKey(user.profile.screenName);
  return Redis.matching(key);
});
