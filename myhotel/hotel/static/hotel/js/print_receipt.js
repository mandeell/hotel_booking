document.addEventListener('DOMContentLoaded', function () {
    const printReceiptBtn = document.getElementById('printReceiptBtn');
    if (printReceiptBtn) {
        printReceiptBtn.addEventListener('click', function () {
            const printContent = `
                <html>
                <head>
                    <title>Booking Receipt</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .receipt { max-width: 600px; margin: auto; border: 1px solid #ccc; padding: 20px; }
                        .receipt h2 { text-align: center; color: #007bff; }
                        .receipt p { margin: 5px 0; }
                        .receipt .label { font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="receipt">
                        <h2>Hotel Booking Receipt</h2>
                        <p><span class="label">Booking ID:</span> ${document.getElementById('resultBookingId').textContent}</p>
                        <p><span class="label">Guest Name:</span> ${document.getElementById('resultGuestName').textContent}</p>
                        <p><span class="label">Email:</span> ${document.getElementById('resultEmail').textContent}</p>
                        <p><span class="label">Phone:</span> ${document.getElementById('resultPhone').textContent}</p>
                        <p><span class="label">Check-in:</span> ${document.getElementById('resultCheckin').textContent}</p>
                        <p><span class="label">Check-out:</span> ${document.getElementById('resultCheckout').textContent}</p>
                        <p><span class="label">Room Type:</span> ${document.getElementById('resultRoomType').textContent}</p>
                        <p><span class="label">Guests:</span> ${document.getElementById('resultGuests').textContent}</p>
                        <p><span class="label">Rooms:</span> ${document.getElementById('resultRooms').textContent}</p>
                        <p><span class="label">Total Cost:</span> ${document.getElementById('resultTotalCost').textContent}</p>
                        <p><span class="label">Transaction ID:</span> ${document.getElementById('resultTransactionId').textContent}</p>
                        <p><span class="label">Date:</span> ${new Date().toLocaleString()}</p>
                    </div>
                </body>
                </html>
            `;
            const printWindow = window.open('', '_blank');
            if (printWindow) {
                printWindow.document.write(printContent);
                printWindow.document.close();
                printWindow.print();
            } else {
                alert('Please allow pop-ups to print the receipt.');
            }
        });
    } else {
        console.error("printReceiptBtn element not found");
    }
});