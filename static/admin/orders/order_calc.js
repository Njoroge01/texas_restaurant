(function() {
    document.addEventListener('change', async function(event) {
        const row = event.target.closest('.dynamic-orderitem');
        if (!row) return;

        const menuSelect = row.querySelector('select[id$="menu_item"]');
        const quantityInput = row.querySelector('input[id$="quantity"]');
        const priceInput = row.querySelector('input[id$="price"]');
        const itemTotalEl = row.querySelector('.field-item_total');

        async function fetchPrice() {
            const itemId = menuSelect.value;
            if (!itemId) return 0;

            const response = await fetch(`/orders/get-price/${itemId}/`);
            const data = await response.json();
            return parseFloat(data.price);
        }

        async function updateRow() {
            const price = await fetchPrice();
            const qty = parseInt(quantityInput.value) || 1;
            const total = price * qty;

            priceInput.value = price.toFixed(2);
            itemTotalEl.innerText = total.toFixed(2);

            updateOrderTotals();
        }

        function updateOrderTotals() {
            let subtotal = 0;
            document.querySelectorAll('.dynamic-orderitem').forEach(r => {
                const price = parseFloat(r.querySelector('input[id$="price"]').value) || 0;
                const qty = parseInt(r.querySelector('input[id$="quantity"]').value) || 1;
                subtotal += price * qty;
            });

            const tax = parseFloat(document.querySelector('#id_tax').value) || 0;
            const discount = parseFloat(document.querySelector('#id_discount').value) || 0;
            document.querySelector('#id_subtotal').value = subtotal.toFixed(2);
            document.querySelector('#id_total').value = (subtotal + tax - discount).toFixed(2);
        }

        updateRow();
    });
})();
