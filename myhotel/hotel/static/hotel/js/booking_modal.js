document.addEventListener('DOMContentLoaded', function () {
    window.openBookingModal = function () {
        console.log("openBookingModal called");
        const modalElement = document.getElementById('bookingModal');
        if (!modalElement) {
            console.error("Booking modal element not found");
            return;
        }

        try {
            const checkin = document.getElementById('checkin')?.value || '';
            const checkout = document.getElementById('checkout')?.value || '';
            const roomTypeId = document.getElementById('room_type')?.value || '';
            const guests = document.getElementById('guests')?.value || '';
            const rooms = document.getElementById('rooms')?.value || '';

            const modal = new bootstrap.Modal(modalElement);
            modal.show();

            const setValue = (id, value) => {
                const element = document.getElementById(id);
                if (element) element.value = value;
                else console.error(`Element with ID ${id} not found`);
            };

            setValue('modalCheckin', checkin);
            setValue('modalCheckout', checkout);
            setValue('roomType', roomTypeId);
            setValue('modalGuests', guests);
            setValue('modalRooms', rooms);

            // Call functions from price_calculator.js
            if (typeof updateModalCheckoutMin === 'function' && typeof updateBookingPrices === 'function') {
                updateModalCheckoutMin();
                updateBookingPrices();
            } else {
                console.error("Price calculator functions not found");
            }
        } catch (error) {
            console.error("Error in openBookingModal:", error);
        }
    };



    // Book room from room cards
    window.bookRoom = function (roomTypeId) {
        console.log("Booking room:", roomTypeId);
        const roomTypeSelect = document.getElementById('roomType');
        if (roomTypeSelect) {
            roomTypeSelect.value = roomTypeId;
            window.openBookingModal();
        } else {
            console.error("roomType element not found");
        }
    };
});