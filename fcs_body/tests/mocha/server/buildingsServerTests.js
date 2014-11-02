if (!(typeof MochaWeb === 'undefined')) {
    MochaWeb.testOnly(function () {
        describe("bldgs creation", function () {
            it("should create a bldg", function () {
                var flr = "g-b(111,222)-l" + (new Date().getTime()),
                    payload = {
                        "name": "John",
                        "age": 43
                    };
                var wrappedCreateBldg = Async.wrap(createBldg);
                var bldgId = wrappedCreateBldg(flr, null, USER_CONTENT_TYPE, payload);
                chai.assert(bldgId.length > 4);
                var count = Buildings.find({flr: flr}).count();
                chai.assert.equal(count, 1);
            });
        });


    });
}
