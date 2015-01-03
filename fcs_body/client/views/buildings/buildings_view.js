Template.buildingsGrid.helpers({
    bldgKey: function() {
        var bldgAddr = getBldg(Session.get("currentAddress"));
        console.log(bldgAddr);
        var bldg = Buildings.findOne({address: bldgAddr});
        if (bldg) {
            return bldg.key;
        }
        else {
            return Session.get("currentAddress");
        }
    }
});

Template.buildingsGrid.events({
    "mousedown .bldg": function(event) {
        var externalUrl = $(event.currentTarget).attr("href");
        if (externalUrl) {
            var target = '_top';
            if (externalUrl.length > 4 && externalUrl.substr(0, 4) == "http")
                target = '_blank';
            window.open(externalUrl, target);
        }
    },
    "click .navigate-up": function() {
        var currentAddress = Session.get("currentAddress");
        var parts = currentAddress.split("-");
        parts.pop();
        var newAddress = parts.join("-");
        window.open("/buildings/" + newAddress, "_top");
    }
});

Template.buildingsGrid.rendered = function () {
    var WIDTH = 1200,
        HEIGHT = 600,
        BOUNDING_WIDTH = 1220,
        BOUNDING_HEIGHT = 620,
        SQUARE_WIDTH = 10,
        SQUARE_HEIGHT = 10;


    var self = this;

    var dom = {};
    var zoomBehavior = d3.behavior.zoom().scaleExtent([0.8, 60]).on("zoom", zoom);
    dom.svg = d3.select("#display").append("svg")
        .attr("width", BOUNDING_WIDTH)
        .attr("height", BOUNDING_HEIGHT)
        .append("g")
        .call(zoomBehavior)
        .append("g");

    dom.svg.append("rect")
        .attr("class", "overlay")
        .attr("width", BOUNDING_WIDTH)
        .attr("height", BOUNDING_HEIGHT)
        .attr("fill", "lightblue");


    var xScale = d3.scale.linear().domain([0, FLOOR_W * SQUARE_WIDTH]).range([0, WIDTH]);
    var yScale = d3.scale.linear().domain([0, FLOOR_H * SQUARE_HEIGHT]).range([0, HEIGHT]);

    if (!self.handle) {
        self.handle = Meteor.autorun(function () {
            dom.bldgs = dom.svg.selectAll('.bldg')
                .data(Buildings.find().fetch())
                .enter()
                .append("g")
                .attr("class", "bldg")
                .attr("xlink:href", function(d) {
                    if (d.payload.external_url) {
                        return d.payload.external_url;
                    }
                    else {
                        // if no external link, link to the 1st flr of the blsg
                        return "/buildings/" + d.address + "-l0";
                    }
                });

            dom.bldgs
                .append('rect')
                .attr({
                    x: function (d) {
                        return xScale(d.x * SQUARE_WIDTH)
                    },
                    y: function (d) {
                        return yScale(d.y * SQUARE_WIDTH)
                    },
                    width: xScale(SQUARE_WIDTH),
                    height: yScale(SQUARE_WIDTH),
                    stroke: 'grey',
                    "stroke-width": 0.05,
                    fill: function (d) {
                        if (d.contentType)
                            return "white";
                    }
                });

            dom.bldgs
                .append("foreignObject")
                .attr({
                    width: xScale(SQUARE_WIDTH),
                    height: yScale(SQUARE_WIDTH),
                    x: function (d) {
                        return xScale(d.x * SQUARE_WIDTH)
                    },
                    y: function (d) {
                        return yScale(d.y * SQUARE_WIDTH)
                    },
                    fill: 'none'
                })
                .append("xhtml:body").append("xhtml:p")
                .style({
                    "color": function (d) {
                        // different color for posts with links
                        // TODO this ain't generic
                        if (d.payload.urls && d.payload.urls.length)
                            return "blue";
                        else
                            return "navy";
                    },
                    "font-size": "0.6px"
                })
                .html(function (d) {
                    if (d.contentType == 'twitter-social-post') {
                        return d.payload.text;
                    }
                    else if (d.contentType == 'daily-feed') {
                        return d.key;
                    }
                    else if (d.contentType == 'user') {
                        return d.payload.screenName;
                    }
                });

//            if (Session.get("currentAddress")) {
//                var addr = Session.get("currentAddress");
//                var bldgAddr = getBldg(addr);
//                if (bldgAddr == addr) {
//                    // given a bldg address, so zoom on it
//                    var parts = bldgAddr.split("-");
//
//                    var part = parts[parts.length - 1];
//                    var coords = part.substring(2, part.length - 1);
//                    console.log("Zooming on " + coords);
//                    var x_y = coords.split(",");
//                    console.log(x_y);
//                    var x = x_y[0],
//                        y = x_y[1];
//                    zoomBehavior.center([xScale(x) + (xScale(SQUARE_WIDTH) / 2), yScale(y) + (yScale(SQUARE_WIDTH) / 2)])
//                }
//            }
        });
    }
    function zoom() {
        dom.svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
};