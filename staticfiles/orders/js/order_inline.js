(function() {
    console.log("✅ Inline auto-calculation script loaded");

    function calculateTotals() {
        let subtotal = 0;

        document.querySelectorAll('.dynamic-items').forEach(row => {
            const qty = parseFloat(row.querySelector('input[id*="quantity"]')?.value || 0);
            const price = parseFloat(row.querySelector('input[id*="price"]')?.value || 0);

            subtotal += qty * price;
        });

        const taxRate = 0.16;
        const subtotalField = document.querySelector('#id_subtotal');
        const taxField = document.querySelector('#id_tax');
        const totalField = document.querySelector('#id_total');

        const tax = subtotal * taxRate;
        const total = subtotal + tax;

        if (subtotalField) subtotalField.value = subtotal.toFixed(2);
        if (taxField) taxField.value = tax.toFixed(2);
        if (totalField) totalField.value = total.toFixed(2);
    }

    function loadPrice(row) {
        const menuSelect = row.querySelector('select[id*="menu_item"]');
        const priceInput = row.querySelector('input[id*="price"]');

        if (!menuSelect || !priceInput) return;

        menuSelect.addEventListener("change", function() {
            const option = menuSelect.options[menuSelect.selectedIndex];
            const price = parseFloat(option.getAttribute("data-price") || 0);
            priceInput.value = price.toFixed(2);
            calculateTotals();
        });
    }

    function init() {
        document.querySelectorAll('.dynamic-items').forEach(row => {
            loadPrice(row);

            let qtyInput = row.querySelector('input[id*="quantity"]');
            let priceInput = row.querySelector('input[id*="price"]');

            if (qtyInput) qtyInput.addEventListener("input", calculateTotals);
            if (priceInput) priceInput.addEventListener("input", calculateTotals);
        });
    }

    document.addEventListener("DOMContentLoaded", init);

    document.body.addEventListener("formset:added", function(event) {
        const row = event.detail?.formsetRow || event.target;
        if (row.classList.contains("dynamic-items")) {
            loadPrice(row);
            calculateTotals();
        }
    });

})();
