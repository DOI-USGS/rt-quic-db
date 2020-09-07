// Fill Locations in Reg Page
$(function() {
   $(document).ready(function() {
	   $.getJSON('/getLocationsForReg', function(data) {
	     updateLocs(data.result);
	   });
	   
	   return false;
   });
 });

function updateLocs(locs){
   var loc_selector = document.getElementById('location');
   
	for(index in locs) {
		   loc_selector.options[loc_selector.options.length] = new Option(locs[index], index);
	}
}