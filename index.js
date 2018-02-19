//console.log("test")

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var format = d3.format(",d");

var tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden")
    .style("color", "white")
    .style("padding", "8px")
    .style("background-color", "rgba(0, 0, 0, 0.75)")
    .style("border-radius", "6px")
    .style("font", "12px sans-serif")
    .text("tooltip");

var color = d3.scaleOrdinal(d3.schemeCategory20c);

var pack = d3.pack()
    .size([width, height])
    .padding(1.5);

function drawWordCloud(word_dict, divID){
        
        //var word_count = {};
        //dict {word: freq}


        var svg_location = divID;
        var width = 400;
        var height = 400;

        var fill = d3.scaleOrdinal(d3.schemeCategory10);
        console.log(word_dict)
        var word_entries = d3.entries(word_dict);

        var xScale = d3.scaleLinear()
           .domain([0, d3.max(word_entries, function(d) {
              return d.value;
            })
           ])
           .range([10,100]);

        d3.layout.cloud().size([width, height])
          .timeInterval(20)
          .words(word_entries)
          .fontSize(function(d) { return xScale(+d.value); })
          .text(function(d) { return d.key; })
          .rotate(function() { return ~~(Math.random() * 2) * 90; })
          .font("Impact")
          .on("end", draw)
          .start();

        function draw(words) {
          d3.select(svg_location).selectAll("svg").remove();
          d3.select(svg_location).append("svg")
              .attr("width", width)
              .attr("height", height)
            .append("g")
              .attr("transform", "translate(" + [width >> 1, height >> 1] + ")")
            .selectAll("text")
              .data(words)
            .enter().append("text")
              .style("font-size", function(d) { return xScale(d.value) + "px"; })
              .style("font-family", "Impact")
              .style("fill", function(d, i) { return fill(i); })
              .attr("text-anchor", "middle")
              .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
              })
              .text(function(d) { return d.key; });
        }

        d3.layout.cloud().stop();
}


var updateRadar = function(categoryName, fillcolor, divID){
	var radarwidth = 200;
	var radarheight = 200;
	

	d3.json("./data.json", function(err, data){
		if(err) throw err;
    console.log("RadarData")
    console.log(data)

		var categoryData = [];

		data.forEach(function(d){
			if(d.name == categoryName){
        categoryData.push({"area" : "1", "value" : +d.star[1] });
			  categoryData.push({"area" : "2", "value" : +d.star[2] });
			  categoryData.push({"area" : "3", "value": +d.star[3] });
			  categoryData.push({"area" : "4", "value" : +d.star[4] });
			  categoryData.push({"area" : "5", "value" : +d.star[5]});
      }
		});
		var newcategoryData = [];
		newcategoryData.push(categoryData);
    var starMax = 0
    categoryData.forEach(function(d){
      if(d.value > starMax){
        starMax = d.value;
      }
    });

    console.log(starMax)
    var config = {
    w: radarwidth,
    h: radarheight,
    maxValue: +starMax,
    levels: 5,
    ExtraWidthX: 300,
    fill: fillcolor
    }
		RadarChart.draw(divID, newcategoryData, config);
		d3.select("h3").text("Star distribution of " + categoryName);
	});


}

var global_data = {}

d3.json("data.json", function(err, data){
	if(err) throw err;
  var classes = []
  data.forEach(function(category){
    classes.push({categoryName: category.name, categorySize: category.reviews, categoryPostive: category.postive, categoryNegative: category.negative});
    if(category.name == "Food"){
      global_data = {categoryPostive: category.postive, categoryNegative: category.negative};
      console.log(global_data)
    }
  })
	var root = d3.hierarchy({ "children" : classes})
				.sum(function(d){
					return d.categorySize; 
				});
	
	var div = d3.select("body").append("div")	
    .attr("class", "tooltip")				
    .style("opacity", 0);

	node = svg.selectAll(".node")
    .data(pack(root).leaves())
    .enter().append("g")
    .attr("class", "node")
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    //console.log(node)
    node.append("circle")
      .attr("id", function(d) { return d.data.type; })
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) { return color(d.data.categoryName)})
      .attr('stroke','black')
      .attr('stroke-width',0)
      .attr("opacity", 0.8)
      .on('mouseover',function(d) {
      	//console.log(d);
      	var rad = 1.1 * d.r;

        d3.select(this)
      	  .transition()
      	  .duration(1000)
      	  .attr("r", 1.1 * d.r )
      	  tooltip.text(d.data.categoryName + ": " + format(d.data.categorySize));
          tooltip.style("visibility", "visible");
      })
      .on('mouseout',function (d) {
        d3.select(this)
          .transition()
          .duration(1000)
          .attr("r", d.r)
    
        return tooltip.style("visibility", "hidden");
      })
      .on('mousemove', function(){ 
      	return tooltip.style("top", (d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");
      })
      .on('click', function(d){
      	//reDrawBar(d.data.type);
      	//Draw two cloud
        updateRadar(d.data.categoryName, color(d.data.categoryName), "#radar");
        drawWordCloud(d.data.categoryPostive, "#cloud-postive");
        drawWordCloud(d.data.categoryNegative, "#cloud-negative");
      })
      
      node.append("text")
      .attr("dy", ".3em")
      .attr("font-size","10px")
      .style("text-anchor", "middle")
      .text(function(d) {
      		//console.log(d);
            return d.data.categoryName;
      });

      updateRadar("Food", color("Food"), "#radar");
      drawWordCloud(global_data.categoryPostive, "#cloud-postive");
      drawWordCloud(global_data.categoryNegative, "#cloud-negative");


});


	



