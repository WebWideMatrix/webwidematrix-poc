if (!(typeof MochaWeb === 'undefined')){
  MochaWeb.testOnly(function(){
    describe("small utils", function(){
      it("should return today's date for display", function(){
          var got = todayDateForDisplay();
          var expected = new Date().toLocaleDateString();
          chai.assert.equal(got, expected);
      });
    });
  });
}
