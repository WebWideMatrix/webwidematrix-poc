Router.configure({
        layoutTemplate: 'layout',
        loadingTemplate: 'loading',
    }
);

Router.onBeforeAction(function() {
    if (!Meteor.userId()) {
        // if the user is not logged in, render the Login template
        this.render('About');
    } else {
        // otherwise don't hold up the rest of hooks or our route/action function
        // from running
        this.next();
    }
});


Router.route('/', function () {
        this.subscribe('userData').wait();
        this.subscribe('userCurrentBldg').wait();

        if (this.ready()) {
            this.render('glassDoor');
        } else {
            this.render('Loading');
        }
}, {name: "home"});

Router.route('/buildings/:addr', function () {
        this.subscribe('buildings', this.params.addr).wait();
        this.subscribe('residents', this.params.addr).wait();

        Session.set("viewingCurrentBuildings", false);
        Session.set("currentAddress", this.params.addr);

        console.log(this.params.addr);
        if (this.params.addr) {
            var bldg = getBldg(this.params.addr);
            console.log(bldg);
            if (bldg == this.params.addr) {
                console.log("Calling method: getBldgContent");
                // We're drilling into a bldg - get it's content
                Meteor.call("getBldgContent", this.params.addr, function (error, result) {
                    console.log("No way: got bldg content!!!!!");
                    console.log(error);
                    console.log(result);
                    Session.set("bldgContent", result);
                });
            }
        }


        if (this.ready()) {
            this.render('buildingsView');
        } else {
            this.render('Loading');
        }
}, {name: "buildings"});

//Router.route('/current/:addr', function() {
//        this.subscribe('current', this.params.addr).wait();
//        this.subscribe('residents', this.params.addr).wait();
//
//        Session.set("viewingCurrentBuildings", true);
//        Session.set("currentAddress", this.params.addr);
//
//        if (this.ready()) {
//            this.render('buildingsView');
//        } else {
//            this.render('Loading');
//        }
//});
