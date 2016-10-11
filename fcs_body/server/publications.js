
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
    var fields = {
        fields: {
            "payload": 0
        }
    };
    return Buildings.find(query, fields);
});

Meteor.publish("residents", function (addr) {
    var flrAddr = getFlr(addr);
    var query = {
        flr: flrAddr
    };
    return Residents.find(query);
});


// REDIS

Meteor.publish('current', function (addr) {
  if (!addr) return [];
  //  FIXME: validate not asking for too much - always publish just 1 flr
  return Redis.matching(addr + '*');
});

Meteor.publish('userCurrentBldg', function () {
  if (!this.userId) return [];
  var key = buildUserCurrentBldgCacheKey(this.userId);
  return Redis.matching(key);
});
