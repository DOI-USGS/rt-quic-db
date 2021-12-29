// Fill Locations in Reg Page
$(function() {
   $(document).ready(function() {
	   $.getJSON('/getTeamsForReg', function(data) {
	     updateTeams(data.result);
	   });
	   
	   return false;
   });
 });

function updateTeams(teams){
   var team_selector = document.getElementById('team');
   
	for(index in teams) {
		   team_selector.options[team_selector.options.length] = new Option(teams[index], index);
	}
}