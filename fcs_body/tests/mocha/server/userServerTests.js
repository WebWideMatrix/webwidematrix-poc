if (!(typeof MochaWeb === 'undefined')){
    MochaWeb.testOnly(function(){
        describe("user creation", function(){
            it("should get user's details", function(){
                var user = {
                        services: {
                            twitter: {
                                lang: 'en',
                                profile_image_url: 'http://some.pic/url',
                                screenName: 'user123'
                            }
                        }
                    },
                    expected = {
                        language: 'en',
                        picture: 'http://some.pic/url',
                        screenName: 'user123'
                    };
                var got = getUserDetails({}, user);
                chai.assert.equal(got.length, expected.length);
                for (var x in expected) {
                    if (expected.hasOwnProperty(x)) {
                        chai.assert.equal(got[x], expected[x]);
                    }
                }
                for (var x in got) {
                    if (got.hasOwnProperty(x)) {
                        chai.assert.equal(got[x], expected[x]);
                    }
                }
            });

            it("should generate initial user name", function() {
                var names = [];
                var profileName = {screenName: "joe"};
                for (var i = 0; i < 100; i++) {
                    names.push(initialResidentName(profileName, i));
                }
                chai.assert.equal(names[0], "1a joe");
                chai.assert.equal(names[1], "1b joe");
                chai.assert.equal(names[10], "1k joe");
                chai.assert.equal(names[30], "2e joe");
                chai.assert.equal(names[50], "2y joe");
                chai.assert.equal(names[80], "4c joe");

            });
        });
    });
}
