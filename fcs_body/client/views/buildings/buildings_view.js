Template.buildingsView.helpers({
    "allBldgs": function () {
        return Buildings.find();    // TODO limit fields
    }
});

Template.buildingsGrid.events({
    "mousedown .node": function(event) {
        var externalUrl = $(event.currentTarget).attr("href");
        if (externalUrl) {
            var target = '_top';
            if (externalUrl.length > 4 && externalUrl.substr(0, 4) == "http")
                target = '_blank';
            window.open(externalUrl, target);
        }
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
    dom.svg = d3.select("#display").append("svg")
        .attr("width", BOUNDING_WIDTH)
        .attr("height", BOUNDING_HEIGHT)
        .append("g")
        .call(d3.behavior.zoom().scaleExtent([0.8, 60]).on("zoom", zoom))
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
            var bldgs = Buildings.find();
            var squares = [];
            bldgs.forEach(function (b) {
                squares.push(b);
            });

            dom.nodes = dom.svg.selectAll('.node')
                .data(squares)
                .enter()
                .append("g")
                .attr("class", "node")
                .attr("xlink:href", function(d) {
                    if (d.payload.external_url) {
                        return d.payload.external_url;
                    }
                    else {
                        // if no external link, link to the 1st flr of the blsg
                        return "/buildings/" + d.address + "-l0";
                    }
                });

            dom.nodes
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

            dom.nodes
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

        });
    }
    function zoom() {
        dom.svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
};