
Template.buildingsView.helpers({
    "allBldgs": function() {
        return Buildings.find();    // TODO limit fields
    }
});


Template.buildingsGrid.rendered = function() {
    var SQUARE_WIDTH = 10;

    var self = this;
	var zoom = d3.behavior.zoom()
		.scaleExtent([0.5, 10])
		.on("zoom", zoomed);

	function zoomed() {
		d3.select("#map_viewport").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
	}

    var scale = d3.scale.linear().domain([0, 100*SQUARE_WIDTH]).range([0, 600]);
    var svg = d3.select('body').select('#grid').call(zoom);
    if (!self.handle) {
        self.handle = Meteor.autorun(function () {
            var bldgs = Buildings.find();
            var bldgsDict = {};
            bldgs.forEach(function(b) {
                bldgsDict[b.x + "," + b.y] = b;
            });

            var squares = [];
            for (var j = 0; j < 100; j++) {
                for (var i = 0; i < 100; i++) {
                    var k = i + "," + j;
                    if (bldgsDict[k]) {
                        squares.push(bldgsDict[k]);
                    }
                    else {
                        squares.push({x: i, y: j});
                    }
                }
            }
            console.log(bldgsDict);
            console.log(squares);
            d3.select('.bldgs').selectAll('rect').remove();
            d3.select('.bldgs').selectAll('rect').data(squares)
                .enter()
                .append('rect')
                .attr('x', function(d) {return scale(d.x * SQUARE_WIDTH)})
                .attr('y', function(d) {return scale(d.y * SQUARE_WIDTH)})
                .attr('width', scale(SQUARE_WIDTH))
                .attr('height', scale(SQUARE_WIDTH))
                .attr("stroke", function(d) {
                    if (d.contentType)
                        return "black";
                    else
                        return "grey";
                })
                .attr("stroke-width", 1)
                .attr("fill", function(d) {
                    if (d.contentType)
                        return "blue";
                    else
                        return "white";
                });

        });
    }
};