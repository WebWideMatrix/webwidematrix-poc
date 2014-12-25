


getTodaysFeedAddress = function() {
    var today = formatDate(new Date());
//    var targetFlr = getCurrentUserBldgAddress() + "-l0";
//    console.log(targetFlr);
    var todaysBldg = Buildings.findOne({
//        flr: targetFlr,
        key: today
    });
    if (todaysBldg) {
        console.log(todaysBldg);
        return todaysBldg.address;
    }
    else {
        return null;
    }
};
