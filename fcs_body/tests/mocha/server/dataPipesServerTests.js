if (!(typeof MochaWeb === 'undefined')){
    MochaWeb.testOnly(function(){
        describe("data-pipe creation", function(){
            it("should create a data-pipe", function(){
                var tokens = {
                    "access": "767657",
                    "secret": "fakesecret"
                };
                var wrappedCreateDataPipe = Async.wrap(createDataPipe);
                var dataPipeId = wrappedCreateDataPipe(tokens);
                chai.assert(dataPipeId.length > 4);
            });
        });
    });
}
