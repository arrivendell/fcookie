DATA_CACHE = {};

$(document).ready(function () {

  apiCall('graph_data', 'GET', {}, function(data) {
    DATA_CACHE = data;
    drawGraph(data.Temperature);
  });

  $('#reading-type').change(function() {
    drawGraph(DATA_CACHE[$(this).val()]);
  })

});


drawGraph = function (chart_data) {

  CHART_DATA = chart_data;

  var colors = d3.scale.category20();
  keyColor = function(d, i) {return colors(d.key)};

  nv.addGraph(function() {
    var chart = nv.models.lineWithFocusChart()
                  .x(function(d) { return d[0] })
                  .y(function(d) { return d[1] })
                  .clipEdge(true);

    chart.xAxis
        .tickFormat(function(d) { return d3.time.format('%x')(new Date(d)) });

    chart.yAxis
        .tickFormat(d3.format(',.2f'));

    chart.x2Axis
        .tickFormat(function(timestamp) {
          var d = new Date(timestamp);
          return d.getDate() + '/' + (d.getMonth()+1) + '/' + d.getFullYear();
      });

    console.log(chart_data);
    d3.select('#values-chart')
      .datum(chart_data)
        .transition().duration(500).call(chart);

    nv.utils.windowResize(chart.update);

    return chart;

  });



};
