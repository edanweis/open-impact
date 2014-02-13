var w = 480, h = 480, links = [], voronoiVertices = [], add = true;

var radius = 37;
if (radius > 55) {
	radius = 55
}
if (radius < 35) {
	radius = 35
}

var mCharge = radius * -8.5;

var numVertices = 2;
var maxVertices = 6;
var vertices = d3.range(numVertices).map(function(d) {
	return {
		x : d.x,
		y : d.y
	};
})
var prevEventScale = 1;
var zoom = d3.behavior.zoom().on("zoom", function(d, i) {
	if ((d3.event.scale < prevEventScale) && (vertices.length < maxVertices)) {
		vertices.push(function(d) {
			return {
				x : d.x,
				y : d.y
			};
		})
	} else if (vertices.length > 2) {
		vertices.pop();
	}
	force.nodes(vertices).start()
	prevEventScale = d3.event.scale;
});

var dragging =false;
var svg = d3.select("#chart").append("svg").attr("width", w).attr("height", h).call(zoom);

var force = self.force = d3.layout.force().charge(-120)
//            .friction(0.94)
.gravity(0.2).size([w, h]).on("tick", update);

force.nodes(vertices).start();

var circle = svg.selectAll("circle");
// how to add different colours to the first two?
var path = svg.selectAll("path");
var link = svg.selectAll("line");

RandomColor = function() {
	colors = ['#EF5055', '#29ABE2', '#FDE27A', '#068B73'];
	return colors[Math.floor(Math.random() * colors.length)];

	addatRandom();

}

// function varyHue(c){
// 	
	// if(c=="#EF5055")
	// setInterval( function() {
        // return
    // }, 1000 )
//     
// }

function addatRandom() {
}( function loop() {
	var rand = Math.round(Math.random() * (4000 - 1000)) + 1000;
	var randboolean = Math.round(Math.random());
	var items = [1, 2, 3]
	var randmultiplier = Math.floor(Math.random() * items.length)
	setTimeout(function() {
		if ((vertices.length < maxVertices - 1) && randboolean > 0) {
			for ( i = 0; i < randmultiplier; i++) {
				vertices.push(function(d) {
					return {
						x : d.x,
						y : d.y
					};
				})
			}
		} else if ((vertices.length > 3) && (randboolean == 0)) {
			for ( i = 0; i < randmultiplier; i++) {
				vertices.pop();
			}
		}
		force.nodes(vertices).start()
		loop();
	}, rand);
}());


function varyHue() {
	return function() {
		var randT = Math.round(Math.random() * (8000 - 1000)) + 1000;
		var randC = d3.rgb(RandomColor());
		d3.select(this).transition()
		.duration(randT)
		.attr("fill",randC)
		.each("end", varyHue());
	};
}


function update(e) {
	voronoiVertices = vertices.map(function(o) {
		return [o.x, o.y, o]
	})
	path = path.data(d3.geom.voronoi(voronoiVertices))
	path.enter().insert("path", "path")//group all the path elements first so they have the lowest z-order

	/*.attr("class", function(d, i) { return "q"+color(d3.geom.polygon(d).area())+"-9"; })
	 .attr("d", function(d) { return "M" + d.join("L") + "Z"; });
	 path.attr("class", function(d, i) { return "q"+color(d3.geom.polygon(d).area())+"-9"; })
	 .attr("d", function(d) { return "M" + d.join("L") + "Z"; });*/
	 path.exit().remove();
	 circle = circle.data(vertices)
	 circle.enter().append("circle")
	 .call(force.drag)
	 .attr("r", 1)
	//.each(varyHue())
	.attr("fill", d3.rgb(RandomColor()))
	.on("click", function(d,i) { 
		if ((vertices.length < maxVertices)) {
			vertices.push(function(d) {
				return {
					x : d.x,
					y : d.y
				};
			})
		}
		force.nodes(vertices).start()
		prevEventScale = d3.event.scale;

	})

	
	

	
	
	.attr("cx", function(d) {
		return d.x;
	}).attr("cy", function(d) {
		return d.y;
	}).transition().duration(500).attr("r", radius).transition().duration(100).style("opacity", 0.75).each(varyHue())
	circle.attr("cx", function(d) {
		return d.x;
	}).attr("cy", function(d) {
		return d.y;
	});
	circle.exit().transition().duration(500).attr("r", 0).remove();
	//modified this line

	links = []
	d3.geom.delaunay(voronoiVertices).forEach(function(d) {
		links.push(edge(d[0], d[1]));
		links.push(edge(d[1], d[2]));
		links.push(edge(d[2], d[0]));
	});

	link = link.data(links)
	link.enter().append("line")
	//.style("opacity", 0)
	//.transition().duration(1000)
	//.style("opacity", 1)
	.attr("stroke-dasharray", "1 4")
	link.attr("x1", function(d) {
		return d.source[2].x;
	}).attr("y1", function(d) {
		return d.source[2].y;
	}).attr("x2", function(d) {
		return d.target[2].x;
	}).attr("y2", function(d) {
		return d.target[2].y;
	})

	link.exit().remove()

}

function edge(a, b) {
	return {
		source : a,
		target : b
	};
}