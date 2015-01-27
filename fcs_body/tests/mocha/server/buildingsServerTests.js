if (!(typeof MochaWeb === 'undefined')) {
    MochaWeb.testOnly(function () {
        describe("bldgs creation", function () {
            function createSomeBldg() {
                var flr = "g-b(111,222)-l" + (new Date().getTime()),
                    key = "4john",
                    payload = {
                        "name": "John",
                        "age": 43
                    };
                var wrappedCreateBldg = Async.wrap(createBldg);
                var bldgId = wrappedCreateBldg(flr, key, null, USER_CONTENT_TYPE, payload);
                return {flr: flr, bldgId: bldgId};
            }

            it("should create a bldg", function () {
                var __ret = createSomeBldg();
                var flr = __ret.flr;
                var bldgId = __ret.bldgId;
                chai.assert(bldgId.length > 4);
                var count = Buildings.find({flr: flr}).count();
                chai.assert.equal(count, 1);

            });

            it("should get a bldg's key by its address", function () {
                var __ret = createSomeBldg();
                var flr = __ret.flr;
                var bldgId = __ret.bldgId;
                var bldg = Buildings.findOne({_id: bldgId});
                var bldgAddr = bldg.address,
                    expected = bldg.key;
                var got = getBldgKey(bldgAddr);
                chai.assert.equal(got, expected);
            });


        });


    });
}
