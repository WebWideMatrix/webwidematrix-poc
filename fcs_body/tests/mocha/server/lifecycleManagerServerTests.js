if (!(typeof MochaWeb === 'undefined')){
    MochaWeb.testOnly(function(){
        describe("lifecycle manager creation", function(){
            it("should create a lifecycle manager", function(){
                var bldgId = "abc",
                    dataPipeId = "123";
                var wrappedCreateLifecycleManager = Async.wrap(createLifecycleManager);
                var lifecycleManagerId = wrappedCreateLifecycleManager(bldgId, dataPipeId);
                chai.assert(lifecycleManagerId.length > 4);
            });
        });
    });
}
