document.addEventListener('DOMContentLoaded', function() {
    // Price Range Slider
    const priceRangeSlider = document.getElementById('priceRangeSlider');
    if (priceRangeSlider) {
        noUiSlider.create(priceRangeSlider, {
            start: [
                parseInt(document.getElementById('minPrice').value),
                parseInt(document.getElementById('maxPrice').value)
            ],
            connect: true,
            step: 10,
            range: {
                'min': 40,
                'max': 4000
            }
        });

        priceRangeSlider.noUiSlider.on('update', function(values) {
            document.getElementById('minPriceValue').textContent = parseInt(values[0]);
            document.getElementById('maxPriceValue').textContent = parseInt(values[1]);
            document.getElementById('minPrice').value = parseInt(values[0]);
            document.getElementById('maxPrice').value = parseInt(values[1]);
        });
    }

    // Deposit Range Slider
    const depositRangeSlider = document.getElementById('depositRangeSlider');
    if (depositRangeSlider) {
        noUiSlider.create(depositRangeSlider, {
            start: [
                parseInt(document.getElementById('minDeposit').value),
                parseInt(document.getElementById('maxDeposit').value)
            ],
            connect: true,
            step: 50,
            range: {
                'min': 100,
                'max': 5000
            }
        });

        depositRangeSlider.noUiSlider.on('update', function(values) {
            document.getElementById('minDepositValue').textContent = parseInt(values[0]);
            document.getElementById('maxDepositValue').textContent = parseInt(values[1]);
            document.getElementById('minDeposit').value = parseInt(values[0]);
            document.getElementById('maxDeposit').value = parseInt(values[1]);
        });
    }

    // Auto-submit form when filters change
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input[type="checkbox"], select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                filterForm.submit();
            });
        });

        // For range sliders, submit on change end
        if (priceRangeSlider) {
            priceRangeSlider.noUiSlider.on('change', () => {
                filterForm.submit();
            });
        }
        if (depositRangeSlider) {
            depositRangeSlider.noUiSlider.on('change', () => {
                filterForm.submit();
            });
        }
    }

    // Sort functionality
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', this.value);
            window.location.href = currentUrl.toString();
        });
    }
});