Router.configure({
    layoutTemplate: 'layout',
    loadingTemplate: 'loading',
    waitOn: function () {
//        handle = Meteor.subscribeWithPagination('buildings', 100);
//        return handle;
    }
});
Router.map(function () {
    this.route('glassDoor', {
        path: '/'
    });

    this.route('buildingsView', {
//        path: '/buildings/:address',
        path: '/buildings'
//        data: function () {
            /*
            var parts = address.split(".");
            var suffix = parts[parts.length - 1];
            if (suffix === "" || suffix.startsWith("l")) {
                var level = address;
                return Buildings.find({level: level});
            }
            else if (suffix.startsWith("b(")) {
                return Buildings.findOne({address: address});
            }
            */
//            return Buildings.find();
//        }
    });
});
Router.onBeforeAction('loading');