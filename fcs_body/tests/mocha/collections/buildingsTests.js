if (!(typeof MochaWeb === 'undefined')){
  MochaWeb.testOnly(function(){
    describe("bldgs address", function(){
      it("should build a ground building address correctly", function(){
          var flr = "g",
              x = 123,
              y = 456;
          var got = buildBldgAddress(flr, x, y);
          var expected = "g-b(123,456)";
          chai.assert.equal(got, expected);
      });
      it("should build an upper level building address correctly", function(){
          var flr = "g-b(1,2)-l0",
              x = 123,
              y = 456;
          var got = buildBldgAddress(flr, x, y);
          var expected = "g-b(1,2)-l0-b(123,456)";
          chai.assert.equal(got, expected);
      });
    });


  });
}
