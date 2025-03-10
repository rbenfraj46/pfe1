function change_language(lang_code){
	document.getElementById('language_form_id_language').value = lang_code;
	document.getElementById('language_form_id_next').value = window.location.href;
	document.getElementById('language_form_id').submit();
}

function change_devise(devise){
	document.getElementById('devise_id').value = devise;
	document.getElementById('next_devise_id').value = window.location.href;
	document.getElementById('devise_form_id').submit();
}

