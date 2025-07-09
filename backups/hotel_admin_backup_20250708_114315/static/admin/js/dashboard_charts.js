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
const allBookings = window.allBookings || [];

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

// Modern Chart.js options for a beautiful look
function getModernOptions(title) {
    return {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: '#374151',
                    font: { size: 15, weight: 'bold', family: 'Inter, sans-serif' },
                    boxWidth: 18,
                    boxHeight: 18,
                    padding: 20
                }
            },
            title: {
                display: false,
                text: title,
                color: '#111827',
                font: { size: 20, weight: 'bold', family: 'Inter, sans-serif' }
            },
            tooltip: {
                backgroundColor: '#fff',
                titleColor: '#111827',
                bodyColor: '#374151',
                borderColor: '#e5e7eb',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
                caretSize: 8,
                boxPadding: 8,
                displayColors: true,
                callbacks: {}
            },
        },
        layout: {
            padding: 20
        },
        scales: {
            x: {
                grid: {
                    color: '#e5e7eb',
                    borderColor: '#e5e7eb',
                    borderDash: [4, 4],
                    drawBorder: false
                },
                ticks: {
                    color: '#6b7280',
                    font: { size: 13, family: 'Inter, sans-serif' }
                }
            },
            y: {
                grid: {
                    color: '#e5e7eb',
                    borderColor: '#e5e7eb',
                    borderDash: [4, 4],
                    drawBorder: false
                },
                ticks: {
                    color: '#6b7280',
                    font: { size: 13, family: 'Inter, sans-serif' }
                }
            }
        },
        elements: {
            bar: {
                borderRadius: 12,
                borderSkipped: false,
                backgroundColor: function(context) {
                    // Use a gradient for a modern look
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) return null;
                    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    if (context.dataset.label === 'Confirmed') {
                        gradient.addColorStop(0, '#34d399');
                        gradient.addColorStop(1, '#10b981');
                    } else if (context.dataset.label === 'Pending') {
                        gradient.addColorStop(0, '#fde68a');
                        gradient.addColorStop(1, '#f59e42');
                    } else {
                        gradient.addColorStop(0, '#fca5a5');
                        gradient.addColorStop(1, '#ef4444');
                    }
                    return gradient;
                },
                borderWidth: 0,
                hoverBackgroundColor: '#6366f1',
                hoverBorderColor: '#6366f1',
            }
        }
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
                    },
                    {
                        label: 'Pending',
                        data: dayData.pending,
                    },
                    {
                        label: 'Cancelled',
                        data: dayData.cancelled,
                    }
                ]
            },
            options: getModernOptions('Bookings Today')
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
                    },
                    {
                        label: 'Pending',
                        data: weekData.pending,
                    },
                    {
                        label: 'Cancelled',
                        data: weekData.cancelled,
                    }
                ]
            },
            options: getModernOptions('Bookings This Week')
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
                    },
                    {
                        label: 'Pending',
                        data: monthData.pending,
                    },
                    {
                        label: 'Cancelled',
                        data: monthData.cancelled,
                    }
                ]
            },
            options: getModernOptions('Bookings This Month')
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
                    },
                    {
                        label: 'Pending',
                        data: yearData.pending,
                    },
                    {
                        label: 'Cancelled',
                        data: yearData.cancelled,
                    }
                ]
            },
            options: getModernOptions('Bookings This Year')
        });
    }
    // All Bookings (use 'label' field for all bookings summary)
    const allData = extractData(allBookings, 'label', false);
    if (document.getElementById('allBookingsChart')) {
        new Chart(document.getElementById('allBookingsChart'), {
            type: 'bar',
            data: {
                labels: allData.labels,
                datasets: [
                    {
                        label: 'Confirmed',
                        data: allData.confirmed,
                    },
                    {
                        label: 'Pending',
                        data: allData.pending,
                    },
                    {
                        label: 'Cancelled',
                        data: allData.cancelled,
                    }
                ]
            },
            options: getModernOptions('All Bookings')
        });
    }
});
