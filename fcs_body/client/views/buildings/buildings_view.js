
Template.buildingsGrid.helpers({
    bldgKey: function() {
        var bldgKey = getBldgKey(Session.get("currentBldg"));
        if (bldgKey) {
            return bldgKey;
        }
        else {
            // if there's no bldg, just show the address
            return Session.get("currentAddress");
        }
    }
});

function openExternalURL(externalUrl) {
    if (externalUrl) {
        var target = '_top';
        if (externalUrl.length > 4 && externalUrl.substr(0, 4) == "http")
            target = '_blank';
        window.open(externalUrl, target);
    }
}

var bldgRenderFunc = {
    'twitter-social-post': function(d) {
        return d.payload.text;
    },
    'daily-feed': function(d) {
        return d.key;
    },
    'user': function(d) {
        return d.payload.screenName;
    }
};

Template.buildingsGrid.events({
    "mousedown .bldg": function(event) {
        var externalUrl = $(event.currentTarget).attr("href");
        openExternalURL(externalUrl);
    },
    "click .navigate-up": function() {
        var currentAddress = Session.get("currentAddress");
        var parts = currentAddress.split("-");
        parts.pop();
        // if it's a flr, get out to the containing bldg
        if (parts[parts.length - 1][0] == "l") {
            parts.pop();
        }
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
        SQUARE_HEIGHT = 10,
        MAX_ZOOM_OUT = 0.8,
        MAX_ZOOM_IN = 60;


    var self = this;
    var dom = {};

    var _zoom = function(_translate, _scale) {
        dom.svg.attr("transform", "translate(" + _translate + ")scale(" + _scale + ")");
    };

    var zoom = function() {
        _zoom(d3.event.translate, d3.event.scale);
    };

    var zoomBehavior = d3.behavior.zoom().scaleExtent([MAX_ZOOM_OUT, MAX_ZOOM_IN]).on("zoom", zoom);

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
            var query = {};
            if (Session.get("currentBldg") != Session.get("currentAddress")) {
                // if we're in a flr, don't render the containing bldg
                query = {flr: Session.get("currentAddress")};
            }
            // add g elements for all bldgs
            dom.bldgs = dom.svg.selectAll('.bldg')
                .data(Buildings.find(query).fetch())
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

            // draw the bldg frame
            dom.bldgs
                .append('rect')
                .attr({
                    x: function (d) {
                        return xScale(d.x * SQUARE_WIDTH)
                    },
                    y: function (d) {
                        return yScale(d.y * SQUARE_HEIGHT)
                    },
                    width: xScale(SQUARE_WIDTH),
                    height: yScale(SQUARE_HEIGHT),
                    stroke: 'grey',
                    "stroke-width": 0.01,
                    fill: function (d) {
                        if (d.contentType)
                            return "white";
                    }
                });

            // add the bldg content
            dom.bldgs
                .append("foreignObject")
                .attr({
                    width: xScale(SQUARE_WIDTH),
                    height: yScale(SQUARE_WIDTH),
                    x: function (d) {
                        return xScale(d.x * SQUARE_WIDTH)
                    },
                    y: function (d) {
                        return yScale(d.y * SQUARE_HEIGHT)
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
                    return bldgRenderFunc[d.contentType](d);
                });

            // if given a bldg address, zoom on it
            if (Session.get("currentAddress") && Session.get("currentAddress") == Session.get("currentBldg")) {
                var parts = Session.get("currentBldg").split("-");
                var part = parts[parts.length - 1];
                var coords = part.substring(2, part.length - 1);
                var x_y = coords.split(",");
                var x = xScale(x_y[0] * SQUARE_WIDTH),
                    y = yScale(x_y[1] * SQUARE_WIDTH);
                // if possible, show some offset
                var X_OFFSET = 10,
                    Y_OFFSET = 5;
                if (x > xScale(X_OFFSET)) x -= xScale(X_OFFSET);
                if (y > yScale(Y_OFFSET)) y -=  yScale(Y_OFFSET);
                var scale = MAX_ZOOM_IN;
                zoomBehavior.scale(scale);
                var translate_vector = [-(x * scale), -(y * scale)];
                zoomBehavior.translate(translate_vector);
                _zoom(translate_vector, scale);
            }
        });
    }

};