document.addEventListener('DOMContentLoaded', function() {
    const forTransferField = document.getElementById('id_for_transfer');
    const transferFieldset = document.querySelector('fieldset.transfer-info');
    const requiredFields = ['id_price_per_km', 'id_price_per_hour', 'id_max_passengers'];

    function toggleTransferFields(isChecked) {
        if (transferFieldset) {
            transferFieldset.style.display = isChecked ? 'block' : 'none';
            
            // Gérer les champs requis
            requiredFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    if (isChecked) {
                        field.setAttribute('required', 'required');
                        field.closest('.form-row').classList.add('required');
                    } else {
                        field.removeAttribute('required');
                        field.closest('.form-row').classList.remove('required');
                        field.value = '';
                    }
                }
            });
        }
    }

    if (forTransferField && transferFieldset) {
        // État initial
        toggleTransferFields(forTransferField.checked);

        // Gérer les changements
        forTransferField.addEventListener('change', function() {
            toggleTransferFields(this.checked);
        });
    }
});