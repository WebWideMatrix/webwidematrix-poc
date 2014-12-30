Template.buildingsView.helpers({
    "allBldgs": function () {
        return Buildings.find();    // TODO limit fields
    }
});


Template.buildingsGrid.rendered = function () {
    var WIDTH = 1200,
        HEIGHT = 400,
        BOUNDING_WIDTH = 1220,
        BOUNDING_HEIGHT = 420,
        SQUARE_WIDTH = 10,
        SQUARE_HEIGHT = 10;


    var self = this;

    var dom = {};
    dom.svg = d3.select("#display").append("svg")
        .attr("width", BOUNDING_WIDTH)
        .attr("height", BOUNDING_HEIGHT)
        .append("g")
        .call(d3.behavior.zoom().scaleExtent([1, 60]).on("zoom", zoom))
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
                .attr("class", "node");

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
                    }
                })
                .append("xhtml:body").append("xhtml:p")
                .style({
                    "color": "navy",
                    "font-size": "0.6px"
                })
                .html(function (d) {
                    console.log(d);
                    if (d.contentType)
                        return d.payload.text;
                    else
                        return ""
                });

        });
    }
    function zoom() {
        dom.svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
};