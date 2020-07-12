
$(function() {
    $('button#chartBtn').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/showCharts', {
        assay_id: $('select#assay').val(),
        wc_id: $('select#wc_ID').val()
      }, function(data) {
//        console.log(data);
        drawChart(data.result, "chart_data");
      });
      return false;
    });
  });

function drawGrid(grid_data){

   Xs = grid_data.Xs
   Ys = grid_data.Ys
   for(i in range(Xs)){
        for (j in range(Ys)){
            // create a div with with id , style to it
            drawChart(grid_data[index],id)
        }
   }
   drawChart
}

function drawChart(figData, id){
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'x value');
//    data.addColumn('number', 'y value');
    data.addRows(figData);

    var options = {
        hAxis: {
          title: 'Time'
        },
        vAxis: {
          title: 'Observation'
        },
        colors: ['#a52714']
      };


     var chart = new google.visualization.LineChart(document.getElementById(id));
      chart.draw(data, options);
}

///////////// SimpleVis page ////////
$(function() {
    $('select#assay').change(function() {
    $('select#wc_ID').children().remove();

    alert($('select#assay').val())
      $.getJSON($SCRIPT_ROOT + '/getWellsForAssay', {
        assay_ID: $('select#assay').val(),
      }, function(data) {
        updateWells(data.result)
      });
      return false;
    });
  });

function updateWells(well_conditions){

    var wc_selector = document.getElementById('wc_ID');
    wc_selector.options[0] = new Option(" -- select an option -- ", -1);
	for(index in well_conditions) {
		   wc_selector.options[wc_selector.options.length] = new Option(well_conditions[index], index);
	}
    wc_selector.disabled = false;
}