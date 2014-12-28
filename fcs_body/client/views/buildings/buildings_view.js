
Template.buildingsView.helpers({
    "allBldgs": function() {
        return Buildings.find();    // TODO limit fields
    }
});


Template.buildingsGrid.rendered = function() {
    var WIDTH = 1200,
        HEIGHT = 400,
        SQUARE_WIDTH = 10,
        SQUARE_HEIGHT = 10;


    var self = this;


    var svg = d3.select("#display").append("svg")
        .attr("width", WIDTH)
        .attr("height", HEIGHT)
        .append("g")
        .call(d3.behavior.zoom().scaleExtent([1, 8]).on("zoom", zoom))
        .append("g");

    svg.append("rect")
        .attr("class", "overlay")
        .attr("width", WIDTH)
        .attr("height", HEIGHT);



    var xScale = d3.scale.linear().domain([0, FLOOR_W*SQUARE_WIDTH]).range([0, WIDTH]);
    var yScale = d3.scale.linear().domain([0, FLOOR_H*SQUARE_HEIGHT]).range([0, HEIGHT]);

    if (!self.handle) {
        self.handle = Meteor.autorun(function () {
            var bldgs = Buildings.find();
            var bldgsDict = {};
            bldgs.forEach(function(b) {
                bldgsDict[b.x + "," + b.y] = b;
            });

            var squares = [];
            for (var row = 0; row < FLOOR_H; row++) {
                for (var col = 0; col < FLOOR_W; col++) {
                    var k = col + "," + row;
                    if (bldgsDict[k]) {
                        squares.push(bldgsDict[k]);
                    }
                    else {
                        squares.push({x: col, y: row});
                    }
                }
            }

            svg.selectAll('rect').remove();
            svg.selectAll('rect')
                .data(squares)
                .enter().append('rect')
                .attr('x', function(d) {return xScale(d.x * SQUARE_WIDTH)})
                .attr('y', function(d) {return yScale(d.y * SQUARE_WIDTH)})
                .attr('width', xScale(SQUARE_WIDTH))
                .attr('height', yScale(SQUARE_WIDTH))
                .attr("stroke", function(d) {
                    if (d.contentType)
                        return "black";
                    else
                        return "white";
                })
                .attr("stroke-width", 0.1)
                .attr("fill", function(d) {
                    if (d.contentType)
                        return "blue";
                    else
                        return "white";
                });

        });
    }
    function zoom() {
        svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
};