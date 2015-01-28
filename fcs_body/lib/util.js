FIXED_DATE_FORMAT = "YYYY-MMM-DD";

randomNumber = function(from, to) {
    return Math.floor(Math.random() * (to - from)) + (from + 1);
};


todayDateForDisplay = function() {
    return new Date().toLocaleDateString();
};

formatDate = function(d) {
    return moment(d).format(FIXED_DATE_FORMAT);
};

daysAgo = function(n) {
    return moment().subtract(n, 'days').format(FIXED_DATE_FORMAT);
};
