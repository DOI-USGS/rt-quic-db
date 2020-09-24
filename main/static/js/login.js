$(function() {
	$form = $('#email_form');
	
	$('#passwordreset').on('shown.bs.modal', function () {
	  $('#email').trigger('focus');
	  $('#email').val('');
	  $('#response').text('');
	  $('#email_for_recovery').prop("disabled",false);
	});

   $('#email_for_recovery').click(function() {

		if(! $form[0].checkValidity()) {
			  // If the form is invalid, submit it. The form won't actually submit;
			  // this will just cause the browser to display the native HTML5 error messages.
			  $form.find(':submit').click();
			  
			} else {
				var data = $form.serializeArray();
				$.getJSON('/sendRecoveryEmail', data, function(data) {
			        if (data["status"] == "success") {
			        	$('#response').text("Email was sent.");
			        	$('#email_for_recovery').prop("disabled",true);
			        } else {
			        	$('#response').text(data["status"]);
			        };
			   });
			   return true;
			};
		});
});