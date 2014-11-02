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
        });
    });
}
