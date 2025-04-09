document.addEventListener('DOMContentLoaded', function () {
    const confirmButton = document.getElementById('confirm-approval-btn');
    if (confirmButton) {
        confirmButton.addEventListener('click', function (event) {
            event.preventDefault();
            const form = document.getElementById('confirmation-form');
            if (form) {
                // Ajouter CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);

                // Soumettre le formulaire avec l'URL actuelle
                form.action = window.location.href;
                form.submit();
            }
        });
    }
});
