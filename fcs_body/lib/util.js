

randomNumber = function(from, to) {
    return Math.floor(Math.random() * (to - from)) + (from + 1);
};


todayDateForDisplay = function() {
    return new Date().toLocaleDateString();
};

formatDate = function(d) {
    var MONTH_NAME = {
        0: "Jan",
        1: "Feb",
        2: "Mar",
        3: "Apr",
        4: "May",
        5: "Jun",
        6: "Jul",
        7: "Aug",
        8: "Sep",
        9: "Oct",
        10: "Nov",
        11: "Dec"
    };
    return d.getFullYear() + "-" + MONTH_NAME[d.getMonth()] + "-" + d.getDate();
};
