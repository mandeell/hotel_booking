document.addEventListener('DOMContentLoaded', function () {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayISO = today.toISOString().split('T')[0];

    // Set min date for modal check-in
    const modalCheckinInput = document.getElementById('modalCheckin');
    if (modalCheckinInput) {
        modalCheckinInput.setAttribute('min', todayISO);
        modalCheckinInput.addEventListener('change', updateModalCheckoutMin);
    } else {
        console.error("modalCheckin element not found");
    }

    // Attach listeners for price and guest updates
    const bookingFields = ['roomType', 'modalRooms', 'modalCheckin', 'modalCheckout'];
    bookingFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', updateBookingPrices);
            console.log(`Change listener attached to ${fieldId}`);
        } else {
            console.error(`Element with ID ${fieldId} not found`);
        }
    });

    // Initialize checkout min date
    updateModalCheckoutMin();
});