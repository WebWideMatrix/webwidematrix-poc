
openExternalURL = function(externalUrl) {
    if (externalUrl) {
        var target = '_top';
        if (externalUrl.length > 4 && externalUrl.substr(0, 4) == "http")
            target = '_blank';
        window.open(externalUrl, target);
    }
};

redirectTo = function(newAddress, prefix) {
    if (!prefix) {
        prefix = "/buildings/";
    }
    window.open(prefix + newAddress, "_top");
};

function renderBldgWithTextAndPicture(d, text, pic) {
    var html = "";
    if (Session.get("currentAddress") == d.address) {
        html += "<p " +
            "style=\"color: gray; " +
            "background-color: white; " +
            "height: 10px; \">" + text + "</p>";
    }
    else {
        var bldg = Session.get("bldgContent");
        if (bldg) {
            text = bldg.raw;
        }
        html = "<img src=\"" + pic + "\" " +
            "alt=\"" + text + "\" " +
            "style=\"color: blue; " +
            "background-color: white; " +
            "height: 10px; \"/>";
    }
    return html;
}

bldgRenderFunc = {
    'twitter-social-post': function(d) {
        var text = d.summary.text;
        var html = "<p " +
            "style=\"color: #" + d.summary.user.profile_text_color + "; " +
            "background-color: #" + d.summary.user.profile_background_color + "; " +
            "height: 10px; \">" + text + "</p>";
        return html;
    },
    'article-text': function(d) {
        var text = d.summary.display_url;
        var pic = d.picture;
        if (d.summary && d.summary.metadata && d.summary.metadata.image_url)
            pic = d.summary.metadata.image_url;
        if (d.summary && d.summary.metadata && d.summary.metadata.title)
            text = d.summary.metadata.title;
        return renderBldgWithTextAndPicture(d, text, pic);
    },
    'concept': function(d) {
        var text = d.summary.concept;
        var pic = d.summary.picture;
        return renderBldgWithTextAndPicture(d, text, pic);
    },
    'daily-feed': function(d) {
        var html = "<table style='border-color: red; height: 5px;' " +
            "width='5px;'>";
        html += "<tr><td bgcolor='red' style='color: white; " +
            "text-align: center; vertical-align: middle; " +
            "height: 2px; font-weight: bold; font-size: 1px;'>" +
            d.key.substring(5, 8) + "</td></tr>";
        html += "<tr><td bgcolor='white' style='width: 100%; " +
            "text-align: center; font-weight: bold; font-size: 2px;'>" +
            d.key.substring(9, 11) + "</td></tr>";
        html += "</table>";
        return html;
    },
    'user': function(d) {
        var html = "<div style=\"height: 6px; width: 6px;\">";
        html += "<img src=\"" + d.summary.picture + "\" width=6px " +
            "height=6px title=\"" + d.key + "\">";
        html += "</div>";
        return html;
    }
};

Template.buildingsGrid.helpers({
    bldgKey: function() {
        var bldg = getBldg(Session.get("currentAddress"));
        Session.set("currentBldg", bldg);

        var bldgKey = getBldgKey(bldg);
        if (bldgKey) {
            return bldgKey;
        }
        else {
            // if there's no bldg, just show the address
            return Session.get("currentAddress");
        }
    },
    flrsStats: function() {
        var bldgAddr = getBldg(Session.get("currentAddress"));
        var bldg = loadBldg(bldgAddr);
        var stats = "Stats (" + bldgAddr + "): ";
        if (bldg.flr_0_stats) {
            stats += bldg.flr_0_stats.residents + " residents, ";
            stats += bldg.flr_0_stats.unprocessed_bldgs + " unprocessed_bldgs, ";
            stats += bldg.flr_0_stats.being_processed_bldgs + " being-processed_bldgs, ";
            stats += bldg.flr_0_stats.processed_bldgs + " processed_bldgs";
        }
        return stats;
    }
});

Template.buildingsGrid.events({
    "click .bldg": function(event) {
        var externalUrl = $(event.currentTarget).attr("href");
        var newAddress = $(event.currentTarget).attr("address");
        if (Session.get("currentAddress") == newAddress) {
            openExternalURL(externalUrl);
        }
        else {
            redirectTo(newAddress);
        }
    },
    "click .rsdt": function(event) {
        var name = $(event.currentTarget).attr("name");
        alert(name + " says hey!")
    },

    "click .navigate-out-of": function() {
        var newAddress = getContainingBldgAddress(Session.get("currentAddress"));
        redirectTo(newAddress);
    },
    "click .navigate-up": function() {
        var newAddress = getOneFlrUp(Session.get("currentAddress"));
        redirectTo(newAddress);
    },
    "click .navigate-down": function() {
        var newAddress = getOneFlrDown(Session.get("currentAddress"));
        redirectTo(newAddress);
    },
    "click .navigate-into": function() {
        var currentAddress = Session.get("currentAddress");
        var newAddress = getOneFlrDown(getFlr(currentAddress));
        var bldg = getBldg(currentAddress);
        if (currentAddress == bldg) {
            newAddress += "?filterByOutput=" + currentAddress;
            redirectTo(newAddress);
        }
        else {
            alert("Please select a building to drill-into");
        }
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

    var getBuildings = function() {
        var inAFloor = Session.get("currentBldg") != Session.get("currentAddress");
        if (Session.get("viewingCurrentBuildings")) {
            var pattern = Session.get("currentAddress");
            if (inAFloor) {
                // if we're in a flr, don't render the containing bldg
                pattern = pattern + "-";
            }
            return Redis.matching(pattern).fetch();
        }
        else {
            var query = {};
            if (inAFloor) {
                // if we're in a flr, don't render the containing bldg
                query = {flr: Session.get("currentAddress")};
            }
            return Buildings.find(query).fetch();
        }
    };

    var getResidents = function() {
        return Residents.find().fetch();
    };

    function matchesOutputFilter(d) {
        return _.contains(d.outputs, Session.get("filterByOutput"));
    }

    if (!self.handle) {
        self.handle = Meteor.autorun(function () {
            // add g elements for all bldgs
            dom.bldgs = dom.svg.selectAll('.bldg')
                .data(getBuildings())
                .enter()
                .append("g")
                .attr("class", "bldg")
                .attr("xlink:href", getBldgLink)
                .attr("address", function(d) {
                    return d.address
                });

            // draw the bldg frame
            dom.bldgs
                .append('rect')
                .attr({
                    x: function (d) {
                        //console.log("XX");
                        //console.log(d);
                        return xScale(d.x * SQUARE_WIDTH)
                    },
                    y: function (d) {
                        return yScale(d.y * SQUARE_HEIGHT)
                    },
                    width: xScale(SQUARE_WIDTH),
                    height: yScale(SQUARE_HEIGHT),
                    stroke: function(d) {
                        if (d.processed)
                            if (matchesOutputFilter(d))
                                return 'red';
                            else
                                return 'green';
                        else
                            return 'grey';
                    },
                    "stroke-width": function(d) {
                        if (d.processed)
                            if (matchesOutputFilter(d))
                                return 5;
                            else
                                return 0.5;
                        else
                            return 0.01;
                    },
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
                .append("xhtml:p")
                .style({
                    "font-size": "1px"
                })
                .html(function (d) {
                    if (d.contentType)
                        return bldgRenderFunc[d.contentType](d);
                    else
                        return "<p>?</p>";
                });

            // if given a bldg address, zoom on it
            if (Session.get("currentAddress") && Session.get("currentAddress") == Session.get("currentBldg")) {
                var coords = extractBldgCoordinates(Session.get("currentBldg"));
                if (coords) {
                    var x = xScale(coords[0] * SQUARE_WIDTH),
                        y = yScale(coords[1] * SQUARE_WIDTH);
                    // if possible, show some offset
                    var X_OFFSET = xScale(10),
                        Y_OFFSET = yScale(5);
                    if (x > X_OFFSET) x -= X_OFFSET;
                    if (y > Y_OFFSET) y -= Y_OFFSET;
                    // apply the zoom
                    var translateVector = [-(x * MAX_ZOOM_IN), -(y * MAX_ZOOM_IN)];
                    zoomBehavior.scale(MAX_ZOOM_IN);
                    zoomBehavior.translate(translateVector);
                    _zoom(translateVector, MAX_ZOOM_IN);
                }
            }


            // let's show also the residents
            dom.residents = dom.svg.selectAll('.rsdt')
                .data(getResidents())
                .enter()
                .append("g")
                .attr("class", "rsdt")
                .attr("name", function(d) {
                    return d.name;
                });

            // draw the residents frame
            dom.residents
                .append('circle')
                .attr({
                    cx: function (d) {
                        var loc = extractBldgCoordinates(d.location);
                        return xScale(loc[0] * SQUARE_WIDTH + SQUARE_WIDTH / 2)
                    },
                    cy: function (d) {
                        var loc = extractBldgCoordinates(d.location);
                        return yScale(loc[1] * SQUARE_HEIGHT + SQUARE_HEIGHT / 2)
                    },
                    r: xScale(SQUARE_WIDTH),
                    stroke: 'grey',
                    "stroke-width": 0.01,
                    fill: function(d) {
                        if (d.processing)
                            return 'yellow';
                        else
                            return 'blue';
                    },
                    "fill-opacity": 0.2
                });
        });
    }

};