
function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toISOString().split('T')[0];
}
// Data from Django context (these must be set in the template before this script loads)
const bookingsPerDay = window.bookingsPerDay || [];
const bookingsPerWeek = window.bookingsPerWeek || [];
const bookingsPerMonth = window.bookingsPerMonth || [];
const bookingsPerYear = window.bookingsPerYear || [];

function extractData(data, key, isDate = true) {
    return {
        labels: data.map(item => {
            if (!item[key]) return '';
            if (isDate) return formatDate(item[key]);
            return item[key];
        }),
        confirmed: data.map(item => Number(item.confirmed)),
        pending: data.map(item => Number(item.pending)),
        cancelled: data.map(item => Number(item.cancelled)),
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // Per Day (use 'label' field for friendly date)
    const dayData = extractData(bookingsPerDay, 'label', false);
    if (document.getElementById('bookingsPerDayChart')) {
        new Chart(document.getElementById('bookingsPerDayChart'), {
            type: 'bar',
            data: {
                labels: dayData.labels,
                datasets: [
                    {
                        label: 'Confirmed',
                        data: dayData.confirmed,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)'
                    },
                    {
                        label: 'Pending',
                        data: dayData.pending,
                        backgroundColor: 'rgba(245, 158, 11, 0.7)'
                    },
                    {
                        label: 'Cancelled',
                        data: dayData.cancelled,
                        backgroundColor: 'rgba(239, 68, 68, 0.7)'
                    }
                ]
            },
            options: {responsive: true}
        });
    }
    // Per Week (use 'label' field for week range)
    const weekData = extractData(bookingsPerWeek, 'label', false);
    if (document.getElementById('bookingsPerWeekChart')) {
        new Chart(document.getElementById('bookingsPerWeekChart'), {
            type: 'bar',
            data: {
                labels: weekData.labels,
                datasets: [
                    {
                        label: 'Confirmed',
                        data: weekData.confirmed,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)'
                    },
                    {
                        label: 'Pending',
                        data: weekData.pending,
                        backgroundColor: 'rgba(245, 158, 11, 0.7)'
                    },
                    {
                        label: 'Cancelled',
                        data: weekData.cancelled,
                        backgroundColor: 'rgba(239, 68, 68, 0.7)'
                    }
                ]
            },
            options: {responsive: true}
        });
    }
    // Per Month (use 'label' field for month name)
    const monthData = extractData(bookingsPerMonth, 'label', false);
    if (document.getElementById('bookingsPerMonthChart')) {
        new Chart(document.getElementById('bookingsPerMonthChart'), {
            type: 'bar',
            data: {
                labels: monthData.labels,
                datasets: [
                    {
                        label: 'Confirmed',
                        data: monthData.confirmed,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)'
                    },
                    {
                        label: 'Pending',
                        data: monthData.pending,
                        backgroundColor: 'rgba(245, 158, 11, 0.7)'
                    },
                    {
                        label: 'Cancelled',
                        data: monthData.cancelled,
                        backgroundColor: 'rgba(239, 68, 68, 0.7)'
                    }
                ]
            },
            options: {responsive: true}
        });
    }
    // Per Year (use 'label' field for year)
    const yearData = extractData(bookingsPerYear, 'label', false);
    if (document.getElementById('bookingsPerYearChart')) {
        new Chart(document.getElementById('bookingsPerYearChart'), {
            type: 'bar',
            data: {
                labels: yearData.labels,
                datasets: [
                    {
                        label: 'Confirmed',
                        data: yearData.confirmed,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)'
                    },
                    {
                        label: 'Pending',
                        data: yearData.pending,
                        backgroundColor: 'rgba(245, 158, 11, 0.7)'
                    },
                    {
                        label: 'Cancelled',
                        data: yearData.cancelled,
                        backgroundColor: 'rgba(239, 68, 68, 0.7)'
                    }
                ]
            },
            options: {responsive: true}
        });
    }
});
