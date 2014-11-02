Router.configure({
        layoutTemplate: 'layout',
        loadingTemplate: 'loading',

        onBeforeAction: function () {
            // all properties available in the route function
            // are also available here such as this.params

            if (!Meteor.userId()) {
                // if the user is not logged in, render the Login template
                this.render('About');
            } else {
                // otherwise don't hold up the rest of hooks or our route/action function
                // from running
                this.next();
            }
        }
    }
);
Router.map(function () {
    this.route('glassDoor', {
        path: '/'
    });


    Router.route('/buildings/:flr', function () {
        this.subscribe('Buildings', this.params.flr).wait();

        if (this.ready()) {
            this.render('buildingsView');
        } else {
            this.render('Loading');
        }
    });

//    this.route('buildingsView', {
//        path: '/buildings/:address',
//        path: '/buildings'
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
//    });
});
