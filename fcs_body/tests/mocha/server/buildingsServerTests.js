if (!(typeof MochaWeb === 'undefined')){
  MochaWeb.testOnly(function(){
    describe("bldgs creation", function(){
      it("should create a bldg", function(done){
          var flr = "g",
              payload = {
                  "name": "John",
                  "age": 43
              };
          chai.assert.equal(1, 1);
          createBldg(flr, null, USER_CONTENT_TYPE, payload, function(err, res) {
              chai.assert.equal(1, 2);
              done();
          });

      });
    });


  });
}
