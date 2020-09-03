<!-- WELL EDIT -->
$(document).on('contextmenu', function(e) {
	  var top = e.pageY - 10;
	  var left = e.pageX - 90;
	  $("#context-menu").css({
	    display: "block",
	    top: top,
	    left: left
	  }).addClass("show");
	  return false; //blocks default Webbrowser right click menu
	}).on("click", function() {
	  $("#context-menu").removeClass("show").hide();
	});
	$("#context-menu a").on("click", function() {
	  $(this).parent().removeClass("show").hide();
	});


$(function() {
    $('#well_edit').on('shown.bs.modal', function() {
      $.getJSON($SCRIPT_ROOT + '/fillWellEdit', {
        "wc_ID": getSelectedWCIDs()
      }, function(data) {
        fillWellEditForm(data)
      });
      return false;
    });
  });

$(function() {
    $('#well_edit_save').click(function() {
			var data = $("#well_edit_form").serializeArray();
			data[data.length] = { name: "wc_ID", value: wc_IDs_global };
			$.getJSON($SCRIPT_ROOT + '/submitWellEdits', data);
			$("#well_edit").modal('hide');
    });
  });

function fillWellEditForm(data) {
		// (hidden) wc IDs
		wc_IDs_global = data.wc_ID;
		
		// Well names
		var wells_text = document.getElementById('wells');
		wells_text.value = data.well_name;
		
		// Sample
		var sample_selector = document.getElementById('sample_ID');
		var sample_ID = data.sample_ID;
		if (sample_ID[0] == true) {
			sample_selector.value = sample_ID[1];
		} else {
			sample_selector.value = "";
		};
		
		// Contents
		var contents_text = document.getElementById('contents');
		if (data.contents[0] == true) {
			contents_text.value = data.contents[1];
			contents_text.placeholder = "Unspecified";
		} else {
			contents_text.placeholder = "Multiple values selected";
			contents_text.value = "";
		};
		
		// Salt
		var salt_type = document.getElementById('salt_type');
		if (data.salt_type[0] == true) {
			salt_type.value = data.salt_type[1];
			salt_type.placeholder = "Unspecified";
		} else {
			salt_type.placeholder = "Multiple values selected";
			salt_type.value = "";
		};
		
		var salt_conc = document.getElementById('salt_conc');
		if (data.salt_conc[0] == true) {
			salt_conc.value = data.salt_conc[1];
			salt_conc.placeholder = "Unspecified";
		} else {
			salt_conc.placeholder = "Multiple values selected";
			salt_conc.value = "";
		};
		
		// Substrate
		var substrate_type = document.getElementById('substrate_type');
		if (data.substrate_type[0] == true) {
			substrate_type.value = data.substrate_type[1];
			substrate_type.placeholder = "Unspecified";
		} else {
			substrate_type.placeholder = "Multiple values selected";
			substrate_type.value = "";
		};
		
		var substrate_conc = document.getElementById('substrate_conc');
		if (data.substrate_conc[0] == true) {
			substrate_conc.value = data.substrate_conc[1];
			substrate_conc.placeholder = "Unspecified";
		} else {
			substrate_conc.placeholder = "Multiple values selected";
			substrate_conc.value = "";
		};
		
		// Surfactant
		var surfact_type = document.getElementById('surfact_type');
		if (data.surfact_type[0] == true) {
			surfact_type.value = data.surfact_type[1];
			surfact_type.placeholder = "Unspecified";
		} else {
			surfact_type.placeholder = "Multiple values selected";
			surfact_type.value = "";
		};
		
		var surfact_conc = document.getElementById('surfact_conc');
		if (data.surfact_conc[0] == true) {
			surfact_conc.value = data.surfact_conc[1];
			surfact_conc.placeholder = "Unspecified";
		} else {
			surfact_conc.placeholder = "Multiple values selected";
			surfact_conc.value = "";
		};
		
		// Other
		var other_wc_attr = document.getElementById('other_wc_attr');
		if (data.other_wc_attr[0] == true) {
			other_wc_attr.value = data.other_wc_attr[1];
			other_wc_attr.placeholder = "Unspecified";
		} else {
			other_wc_attr.placeholder = "Multiple values selected";
			other_wc_attr.value = "";
		};
}

<!-- VISUALIZATION GRID-->

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
            drawChartGrid(data.Xs, data.Ys, data.result, data.wc_ID_list);
        }else{
            assay_name =  $('select#assay option:selected').text();
            wc_name =  $('select#wc_ID option:selected').text();
            drawChart("chart_data", assay_name, wc_name, data.result);
        }

      });
      return false;
    });
  });

function drawChartGrid(Xs, Ys, grid_data, wc_ID_list){
//   for(i in range(Xs)){
//        for (j in range(Ys)){
//            // create a div with with id = wc_row_col and data-wc_ID = wc_ID, style to it
//            drawChart(grid_data[index],id)
//        }
//   }

   var html = '<table width="100%" class="data-table" id="chart_grid"><thead><tr>';

   //adding row header
   for (var m in Ys){
    html += '<th>'+Ys[m]+'</th>'
   }
   html += '</tr></thead><tbody>';
   
   var flat_index = 0;

   for (var i = 0, len = grid_data.length; i < len; ++i) {

    html += '<tr>';
//    html += '<td>'+Xs[i]+'</td>';
      for (var j = 0, rowLen = grid_data[i].length; j < rowLen; ++j, ++flat_index) {
        html += '<td class="selectable" data-wc_ID = "' + wc_ID_list[flat_index] + '"><div id = "wc_'+i+'_'+j+'" title = "' + wc_ID_list[flat_index] + '">' + '</div></td>';
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

<!-- WELL SELECTION -->
// Retrieve selected cells
function getSelectedWCIDs() {
	var hl = document.getElementsByClassName('highlighted');
	var array = new Array();
	
	for (var i = 0; i < hl.length; ++i) {
	    var element = hl[i];  
	    if (element.nodeName == "TD") {
	    	var wc_ID = element.getAttribute('data-wc_ID');
	    	array.push(wc_ID);
	    }
	}
	return array;
}

// Clear selection
function clearSelectedCells() {
	var hl = document.getElementsByClassName('highlighted');
	for (var i = hl.length - 1; i >= 0; --i) {
	   var element = hl[i];
		element.classList.remove('highlighted');
	}
}


// Selection of table cells
$(function () {
   // Create table dragging functionality
   var isMouseDown = false;
   var highlighted
   $("body")
     .on('mousedown', 'table#chart_grid td.selectable', function (e) {
     	 if (e.which == 1) {
     	 	isMouseDown = true;
       	highlighted = $(this).hasClass('highlighted')
       	toggleHighlightingOfCell($(this));
     	 }
       return false; // prevent text selection
     })
//     .on('mousedown', ':not(#context-menu)', function (e) {
//     	 if (e.which == 1) {
//     	 	isMouseDown = true;
//       	$('.highlighted').removeClass('highlighted')
//     	 }
//       return true; // prevent text selection
//     })
     .on('mouseover', 'table#chart_grid td.selectable', function () {
       if (isMouseDown) {
         toggleHighlightingOfCell($(this));
       }
     })
     .bind("selectstart", function () {
       return false; // prevent text selection in IE
     })

   $(document)
       .mouseup(function () {
       isMouseDown = false
   })
 });

function toggleHighlightingOfCell(cell) {
    isHighlighted = cell.hasClass('highlighted');
    if (isHighlighted) {
        cell.removeClass('highlighted');
    } else {
        cell.addClass('highlighted');
    }
}