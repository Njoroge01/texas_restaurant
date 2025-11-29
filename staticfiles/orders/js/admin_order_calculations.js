document.addEventListener('DOMContentLoaded', function () {
    const itemRows = document.querySelectorAll('.dynamic-items');

    function recalculateTotals() {
        let subtotal = 0;

        itemRows.forEach(row => {
            const qty = row.querySelector('input[id$="quantity"]');
            const price = row.querySelector('input[id$="price"]');

            if (qty && price) {
                const qtyValue = parseFloat(qty.value) || 0;
                const priceValue = parseFloat(price.value) || 0;
                const total = qtyValue * priceValue;

                const totalField = row.querySelector('input[id$="item_total"]');
                if (totalField) {
                    totalField.value = total.toFixed(2);
                }
                subtotal += total;
            }
        });

        const subtotalField = document.querySelector('#id_subtotal');
        const taxField = document.querySelector('#id_tax');
        const discountField = document.querySelector('#id_discount');
        const totalField = document.querySelector('#id_total');

        const tax = parseFloat(taxField.value) || 0;
        const discount = parseFloat(discountField.value) || 0;

        subtotalField.value = subtotal.toFixed(2);
        totalField.value = (subtotal + tax - discount).toFixed(2);
    }

    // Price auto-fetch on menu change
    itemRows.forEach(row => {
        const menuField = row.querySelector('select[id$="menu_item"]');
        const priceField = row.querySelector('input[id$="price"]');

        if (menuField) {
            menuField.addEventListener('change', function () {
                const selectedOption = menuField.options[menuField.selectedIndex];
                const price = selectedOption.getAttribute('data-price') || 0;
                priceField.value = price;
                recalculateTotals();
            });
        }
    });

    // Watch quantity changes
    itemRows.forEach(row => {
        const qtyField = row.querySelector('input[id$="quantity"]');
        if (qtyField) {
            qtyField.addEventListener('input', recalculateTotals);
        }
    });

});
