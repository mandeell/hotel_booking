document.addEventListener('DOMContentLoaded', function () {
    // Proceed to confirmation handler
    const submitBookingBtn = document.getElementById('submitBooking');
    if (submitBookingBtn) {
        submitBookingBtn.addEventListener('click', async function () {
            const form = document.getElementById('fullBookingForm');
            console.log("Submit button clicked, form validity:", form.checkValidity());
            if (!form.checkValidity()) {
                console.log("Form validation failed, showing report");
                form.reportValidity();
                return;
            }

            const formData = new FormData(form);
            const bookingData = {
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                modalCheckin: formData.get('modalCheckin'),
                modalCheckout: formData.get('modalCheckout'),
                roomType: document.getElementById('roomType').options[document.getElementById('roomType').selectedIndex].text,
                modalGuests: formData.get('modalGuests'),
                modalRooms: formData.get('modalRooms'),
                modalBasePrice: formData.get('modalBasePrice'),
                modalTotalCost: formData.get('modalTotalCost'),
                special_requests: formData.get('special_requests') || 'None'
            };

            if (!bookingData.email || !bookingData.phone || !bookingData.modalTotalCost) {
                console.error('Invalid booking data:', bookingData);
                const feedbackDiv = document.getElementById('confirmationFeedback');
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Invalid booking details. Please check your input.</div>';
                return;
            }

            // Check room availability
            try {
                const availability = await window.checkRoomAvailability(
                    formData.get('modalCheckin'),
                    formData.get('modalCheckout'),
                    formData.get('roomType'),
                    formData.get('rooms'),
                    formData.get('modalGuests')
                );
                if (availability.errors?.length > 0 || availability.availability_message !== 'Room available') {
                    console.error('Rooms not available:', availability.errors?.length > 0 ? availability.errors : availability.availability_message);
                    const feedbackDiv = document.getElementById('confirmationFeedback');
                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">${
                        availability.errors?.length > 0 ? availability.errors.join(', ') : availability.availability_message
                    }</div>`;
                    return;
                }
            } catch (error) {
                console.error('Availability check error:', error);
                const feedbackDiv = document.getElementById('confirmationFeedback');
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error checking availability: ${error.message}</div>`;
                return;
            }

            // Proceed to confirmationModal
            const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'), { backdrop: 'static' });
            const bookingModal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));

            document.getElementById('confirmFirstName').textContent = bookingData.first_name || '';
            document.getElementById('confirmLastName').textContent = bookingData.last_name || '';
            document.getElementById('confirmEmail').textContent = bookingData.email || '';
            document.getElementById('confirmPhone').textContent = bookingData.phone || '';
            document.getElementById('confirmCheckin').textContent = bookingData.modalCheckin || '';
            document.getElementById('confirmCheckout').textContent = bookingData.modalCheckout || '';
            document.getElementById('confirmRoomType').textContent = bookingData.roomType || '';
            document.getElementById('confirmGuests').textContent = bookingData.modalGuests || '';
            document.getElementById('confirmRooms').textContent = bookingData.modalRooms || '';
            document.getElementById('confirmBasePrice').textContent = bookingData.modalBasePrice || '';
            document.getElementById('confirmTotalCost').textContent = bookingData.modalTotalCost || '';
            document.getElementById('confirmSpecialRequests').textContent = bookingData.special_requests;

            bookingModal.hide();
            confirmationModal.show();

            window.currentBookingData = formData;
        });
    } else {
        console.error("submitBooking element not found");
    }

    // Back to booking handler
    const backToBookingBtn = document.getElementById('backToBooking');
    if (backToBookingBtn) {
        backToBookingBtn.addEventListener('click', function () {
            const confirmationModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
            const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));
            confirmationModal.hide();
            bookingModal.show();
        });
    } else {
        console.error("backToBooking element not found");
    }
});