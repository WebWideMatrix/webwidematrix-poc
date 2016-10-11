if (!(typeof MochaWeb === 'undefined')) {
    MochaWeb.testOnly(function () {
        describe("bldgs address", function () {
            it("should build a ground building address correctly", function () {
                var flr = "g",
                    x = 123,
                    y = 456;
                var got = buildBldgAddress(flr, x, y);
                var expected = "g-b(123,456)";
                chai.assert.equal(got, expected);
            });
            it("should build an upper level building address correctly", function () {
                var flr = "g-b(1,2)-l0",
                    x = 123,
                    y = 456;
                var got = buildBldgAddress(flr, x, y);
                var expected = "g-b(1,2)-l0-b(123,456)";
                chai.assert.equal(got, expected);
            });


            it("should get flr from address", function () {
                var addr = "g-b(1,2)-l0",
                    expected = addr;
                var got = getFlr(addr);
                chai.assert.equal(got, expected);
                addr += "-b(87,65)";
                got = getFlr(addr);
                chai.assert.equal(got, expected);
            });

            it("should get bldg from address", function () {
                var addr = "g-b(1,2)",
                    expected = addr;
                var got = getBldg(addr);
                chai.assert.equal(got, expected);
                addr += "-l0";
                got = getBldg(addr);
                chai.assert.equal(got, expected);
            });

            it("should get the containing bldg address", function () {
                var addr = "g-b(1,2)-l2",
                    expected = "g-b(1,2)";
                var got = getContainingBldgAddress(addr);
                chai.assert.equal(got, expected);
                addr += "-b(15,16)";
                got = getContainingBldgAddress(addr);
                chai.assert.equal(got, expected);
            });

            it("should extract a bldg's coordinates", function () {
                var addr = "g-b(1,2)",
                    expected = [1, 2];
                var got = extractBldgCoordinates(addr);
                chai.assert.equal(got.length, expected.length);
                chai.assert.equal(got[0], expected[0]);
                chai.assert.equal(got[1], expected[1]);
            });

            //it("should get a bldg's link", function () {
            //    var bldg = {
            //            address: "g-b(1,2)",
            //            key: "bldg1",
            //            payload: {
            //                external_url: "http://dada.org"
            //            }
            //        },
            //        expected = "http://dada.org";
            //    var got = getBldgLink(bldg);
            //    chai.assert.equal(got, expected);
            //    bldg = {
            //        address: "g-b(1,2)",
            //        key: "bldg1",
            //        payload: {
            //            text: "blah"
            //        }
            //    };
            //    expected = "/buildings/g-b(1,2)-l0";
            //    got = getBldgLink(bldg);
            //    chai.assert.equal(got, expected);
            //});

        });

    });


}
