document.addEventListener('DOMContentLoaded', function () {
    // Table sorting
    const table = document.getElementById('bookingsTable');
    if (table) {
        const headers = table.querySelectorAll('th');
        let sortCol = -1;
        let sortAsc = true;

        headers.forEach((header, idx) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function () {
                sortAsc = (sortCol === idx) ? !sortAsc : true;
                sortCol = idx;
                sortTable(table, idx, sortAsc);
            });
        });
    }

    function sortTable(table, col, asc) {
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
            const aText = a.children[col].textContent.trim();
            const bText = b.children[col].textContent.trim();
            return asc ? aText.localeCompare(bText, undefined, {numeric: true}) : bText.localeCompare(aText, undefined, {numeric: true});
        });
        rows.forEach(row => tbody.appendChild(row));
    }

    // Table filtering
    const filterInput = document.createElement('input');
    filterInput.type = 'text';
    filterInput.placeholder = 'Filter bookings...';
    filterInput.className = 'form-control mb-3 w-1/3';
    table.parentNode.insertBefore(filterInput, table);
    filterInput.addEventListener('input', function () {
        const filter = filterInput.value.toLowerCase();
        const rows = table.tBodies[0].querySelectorAll('tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });

    // AJAX delete
    table.addEventListener('submit', function (e) {
        if (e.target.matches('form')) {
            e.preventDefault();
            if (!confirm('Are you sure you want to delete this booking?')) return;
            const form = e.target;
            const url = form.action;
            const csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch(url, {
                method: 'POST',
                headers: {'X-CSRFToken': csrf},
            })
            .then(resp => resp.ok ? resp : Promise.reject(resp))
            .then(() => {
                form.closest('tr').remove();
            })
            .catch(() => {
                alert('Failed to delete booking.');
            });
        }
    });
});
