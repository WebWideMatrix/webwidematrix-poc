

randomNumber = function(from, to) {
    return Math.floor(Math.random() * (to - from)) + (from + 1);
};


todayDateForDisplay = function() {
    return new Date().toLocaleDateString();
};

formatDate = function(d) {
    return moment(d).format("YYYY-MMM-DD");
};
