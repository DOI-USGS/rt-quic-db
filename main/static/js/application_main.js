
$(function() {
    $('button#chartBtn').bind('click', function() {
    $('#chart_data').html('');
      $.getJSON($SCRIPT_ROOT + '/showCharts', {
        assay_id: $('select#assay').val(),
        wc_id: $('select#wc_ID').val()
      }, function(data) {
        console.log(data);
        assay_id =  $('select#assay').val();
        wc_id =  $('select#wc_ID').val();
        console.log(assay_id);
        console.log(wc_id);
        if(wc_id == -1 || wc_id ==  null){
            drawChartGrid(data.Xs, data.Ys, data.result);
        }else{
            assay_name =  $('select#assay option:selected').text();
            wc_name =  $('select#wc_ID option:selected').text();
            drawChart("chart_data", assay_name, wc_name, data.result);
        }

      });
      return false;
    });
  });

function drawChartGrid(Xs, Ys, grid_data){
//   for(i in range(Xs)){
//        for (j in range(Ys)){
//            // create a div with with id , style to it
//            drawChart(grid_data[index],id)
//        }
//   }

   var html = '<table width="100%" class="data-table"><thead><tr>';

   //adding row header
   for (var m in Ys){
    html += '<th>'+Ys[m]+'</th>'
   }
   html += '</tr></thead><tbody>';

   for (var i = 0, len = grid_data.length; i < len; ++i) {

    html += '<tr>';
//    html += '<td>'+Xs[i]+'</td>';
      for (var j = 0, rowLen = grid_data[i].length; j < rowLen; ++j ) {
        html += '<td><div id = "wc_'+i+'_'+j+'">' + '</div></td>';
      }
    html += "</tr>";
    }
    html += '</tbody></table>';

    $('#chart_data').html('');
    $(html).appendTo('#chart_data');

    for (var i = 0, len = grid_data.length; i < len; ++i) {
        for (var j = 0, rowLen = grid_data[i].length; j < rowLen; ++j ) {
            drawChart('wc_'+i+'_'+j, null, null, grid_data[i][j], grid = true);
        }
    }

//    drawChart
}

function drawChart(id, assay_name, wc_name, figData, grid = false){
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Time');
    data.addColumn('number', 'Fluorescence');
//    data.addColumn('number', 'y value');
    data.addRows(figData);

    var options = {
        title: 'Assay : '+assay_name +',  Well : '+ wc_name,
        chart: {
          title: 'Assay : '+assay_name +'  Well : '+ wc_name
        },
        hAxis: {
          title: 'Time'
        },
        vAxis: {
          title: 'Fluorescence'
        },
        colors: ['#a52714']
      };

    if(grid){
        options = {
        hAxis: {
          title: ''
        },
        vAxis: {
          title: ''
        },
        colors: ['#a52714'],
        legend: 'none'
      };
    }

     var chart = new google.visualization.LineChart(document.getElementById(id));
      chart.draw(data, options);
}

///////////// SimpleVis page ////////
$(function() {
    $('select#assay').change(function() {
    $('select#wc_ID').children().remove();

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
    wc_selector.options[0] = new Option(" -- All -- ", -1);
	for(index in well_conditions) {
		   wc_selector.options[wc_selector.options.length] = new Option(well_conditions[index], index);
	}
    wc_selector.disabled = false;
}