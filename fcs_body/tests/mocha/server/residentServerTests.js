if (!(typeof MochaWeb === 'undefined')){
    MochaWeb.testOnly(function(){
        describe("resident creation", function(){
            it("should create a resident", function(){
                var bldg = {
                    _id: "abc",
                    flr: "g-b(1,2)-l0",
                    address: "g-b(1,2)-l0-b(5,6)"
                };
                var wrappedCreateRsdt = Async.wrap(createRsdt);
                var rsdtId = wrappedCreateRsdt(bldg);
                chai.assert(rsdtId.length > 4);
            });
        });
    });
}
