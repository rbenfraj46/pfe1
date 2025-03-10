$(function() {
	// Add refresh button after field (this can be done in the template as well)
	$('img.captcha').after(
			$('<img src="/static/images/refresh.png" class="captcha-refresh"/>')
			);
	$('img.captcha').before(
			$('<img src="/static/images/audio-icon.jpg" class="captcha-audio"/><audio id="audio" src="' + $('form a').attr('href') + '"></audio')
			);

	// Click-handler for the refresh-link
	$('.captcha-refresh').click(function(){
		var $form = $(this).parents('form');
		var url = location.protocol + "//" + window.location.hostname + ":"
				  + location.port + "/captcha/refresh/";

		// Make the AJAX-call
		$.getJSON(url, {}, function(json) {
			$form.find('input[name="captcha_0"]').val(json.key);
			$form.find('img.captcha').attr('src', json.image_url);
			$form.find('audio').attr('src', json.audio_url);
		});

		return false;
	});

	$('.captcha-audio').click(function(){
		var $form = $(this).parents('form');
		var url = location.protocol + "//" + window.location.hostname + ":"
				  + location.port + $form.find('audio').attr('src');
		// Make the AJAX-call
		new Audio(url).play();

		return false;
	});
});

function toggle_accordion(div_id){
	var accordion = $(div_id);
	if (accordion.hasClass('active')){
		accordion.removeClass('active');
	} else {
		accordion.addClass('active');
	}
}

function add_next_prefix(){
	var url = window.location.href;
	if (url.indexOf('?')>-1){
		var form = $('#login_form_id');
		var redirect =  url.substring(url.indexOf('?'));
		var new_url = form.attr('action') + redirect;
		form.attr("action", new_url);
	}
	return true;
}
