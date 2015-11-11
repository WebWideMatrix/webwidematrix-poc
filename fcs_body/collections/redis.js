Redis = new Meteor.RedisCollection("redis");


Redis.allow({
  exec: function (userId, command, args) {
    if (! _.contains(['get', 'matching'], command))
      return false;
    var keyDecomposed = args[0].split('-');
    if (command === 'matching' && keyDecomposed.length >= 4)
      return true;
    if (command === 'get' && keyDecomposed.length >= 2 && keyDecomposed[0] === 'g')
      return true;
    return false;
  }
});
