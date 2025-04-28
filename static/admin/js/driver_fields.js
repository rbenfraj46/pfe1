document.addEventListener('DOMContentLoaded', function() {
    const withDriverField = document.getElementById('id_with_driver');
    const driverFieldset = document.querySelector('fieldset.driver-info');
    const requiredFields = ['id_driver_name', 'id_driver_phone', 'id_driver_license_number'];

    function toggleDriverFields(isChecked) {
        if (driverFieldset) {
            driverFieldset.style.display = isChecked ? 'block' : 'none';
            
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
                    }
                }
            });
        }
    }

    if (withDriverField && driverFieldset) {
        // État initial
        toggleDriverFields(withDriverField.checked);

        // Gérer les changements
        withDriverField.addEventListener('change', function() {
            toggleDriverFields(this.checked);
        });
    }
});