function updateBookingPrices() {
    const roomTypeSelect = document.getElementById('roomType');
    const roomsSelect = document.getElementById('modalRooms');
    const checkinInput = document.getElementById('modalCheckin');
    const checkoutInput = document.getElementById('modalCheckout');
    const basePriceInput = document.getElementById('modalBasePrice');
    const totalCostInput = document.getElementById('modalTotalCost');
    const guestsInput = document.getElementById('modalGuests');

    if (!roomTypeSelect || !roomsSelect || !guestsInput) {
        console.error("Missing elements in updateBookingPrices");
        return;
    }

    const selectedRoomOption = roomTypeSelect.options[roomTypeSelect.selectedIndex];
    const basePrice = selectedRoomOption && selectedRoomOption.value ? parseFloat(selectedRoomOption.getAttribute('data-base-price') || 0) : 0;
    const capacity = selectedRoomOption && selectedRoomOption.value ? parseInt(selectedRoomOption.getAttribute('data-capacity') || 0) : 0;
    const numberOfRooms = parseInt(roomsSelect.value) || 0;
    const checkinDate = checkinInput.value ? new Date(checkinInput.value) : null;
    const checkoutDate = checkoutInput.value ? new Date(checkoutInput.value) : null;

    const totalGuests = capacity * numberOfRooms;
    guestsInput.value = capacity && numberOfRooms ? totalGuests : '';
    console.log("updateBookingPrices - Guests:", { totalGuests, capacity, numberOfRooms, roomType: selectedRoomOption?.value });

    if (basePrice && numberOfRooms && checkinDate && checkoutDate && checkoutDate > checkinDate) {
        const numberOfNights = Math.ceil((checkoutDate - checkinDate) / (1000 * 60 * 60 * 24));
        const totalCost = basePrice * numberOfRooms * numberOfNights;
        basePriceInput.value = `₦${basePrice.toFixed(2)}`;
        totalCostInput.value = `₦${totalCost.toFixed(2)}`;
    } else {
        basePriceInput.value = 'N/A';
        totalCostInput.value = 'N/A';
    }
}

function updateModalCheckoutMin() {
    const modalCheckinInput = document.getElementById('modalCheckin');
    const modalCheckoutInput = document.getElementById('modalCheckout');
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayISO = today.toISOString().split('T')[0];

    if (modalCheckinInput.value) {
        const checkinDate = new Date(modalCheckinInput.value);
        if (checkinDate < today) {
            modalCheckinInput.value = '';
            modalCheckoutInput.value = '';
            modalCheckoutInput.removeAttribute('min');
            return;
        }
        const minCheckoutDate = new Date(checkinDate);
        minCheckoutDate.setDate(checkinDate.getDate() + 1);
        const minCheckoutISO = minCheckoutDate.toISOString().split('T')[0];
        modalCheckoutInput.setAttribute('min', minCheckoutISO);
        if (modalCheckoutInput.value && new Date(modalCheckoutInput.value) <= checkinDate) {
            modalCheckoutInput.value = '';
        }
    } else {
        modalCheckoutInput.setAttribute('min', todayISO);
    }
}