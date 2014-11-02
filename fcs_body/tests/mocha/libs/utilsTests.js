if (!(typeof MochaWeb === 'undefined')) {
    MochaWeb.testOnly(function () {
        describe("small utils", function () {
            it("should return today's date for display", function () {
                var got = todayDateForDisplay();
                var expected = new Date().toLocaleDateString();
                chai.assert.equal(got, expected);
            });
            it("should return a random number", function () {
                var a = -5,
                    b = 10;
                for (var i = 0; i < 1000; i++) {
                    var got = randomNumber(a, b);
                    chai.assert(got >= a);
                    chai.assert(got <= b);
                }
            });
        });
    });
}
