document.addEventListener('DOMContentLoaded', function () {
    // Load Paystack SDK dynamically
    const script = document.createElement('script');
    script.src = 'https://js.paystack.co/v1/inline.js';
    script.async = true;
    script.onload = () => console.log('Paystack SDK loaded successfully');
    script.onerror = () => console.error('Failed to load Paystack SDK');
    document.head.appendChild(script);

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayISO = today.toISOString().split('T')[0];

    // Set min date for modal check-in
    const modalCheckinInput = document.getElementById('modalCheckin');
    if (modalCheckinInput) {
        modalCheckinInput.setAttribute('min', todayISO);
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

    // Attach listener for check-in to update check-out min
    if (modalCheckinInput) {
        modalCheckinInput.addEventListener('change', updateModalCheckoutMin);
    }

    // Proceed to confirmation handler
    const submitBookingBtn = document.getElementById('submitBooking');
    if (submitBookingBtn) {
        submitBookingBtn.addEventListener('click', function () {
            const form = document.getElementById('fullBookingForm');
            if (!form.checkValidity()) {
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

// Confirm booking handler with Paystack payment
const confirmBookingBtn = document.getElementById('confirmBooking');
if (confirmBookingBtn) {
    confirmBookingBtn.addEventListener('click', function () {
        const formData = window.currentBookingData;
        const confirmationModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
        const paymentResultModal = new bootstrap.Modal(document.getElementById('paymentResultModal'), { backdrop: 'static' });
        const feedbackDiv = document.getElementById('paymentResultFeedback');
        const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));

        feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        confirmBookingBtn.disabled = true;

        const totalCostRaw = formData.get('modalTotalCost');
        const totalCost = totalCostRaw ? parseFloat(totalCostRaw.replace('₦', '').trim()) : 0;
        const email = formData.get('email');
        const phoneRaw = formData.get('phone');
        const phone = phoneRaw.startsWith('0') ? `+234${phoneRaw.slice(1)}` : phoneRaw;
        const firstName = formData.get('first_name');
        const lastName = formData.get('last_name');
        const reference = `HOTEL-BKG-${Date.now()}`;

        if (!totalCost || isNaN(totalCost) || totalCost <= 0) {
            console.error('Invalid total cost:', totalCostRaw);
            feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Invalid booking amount. Please check your booking details.</div>';
            confirmBookingBtn.disabled = false;
            paymentResultModal.show();
            confirmationModal.hide();
            return;
        }
        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            console.error('Invalid email:', email);
            feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid email is required.</div>';
            confirmBookingBtn.disabled = false;
            paymentResultModal.show();
            confirmationModal.hide();
            return;
        }
        if (!phone || !/^\+?\d{10,15}$/.test(phone)) {
            console.error('Invalid phone:', phone);
            feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid phone number is required (e.g., +2347034618587).</div>';
            confirmBookingBtn.disabled = false;
            paymentResultModal.show();
            confirmationModal.hide();
            return;
        }
        if (typeof PaystackPop === 'undefined') {
            console.error('Paystack SDK not loaded');
            feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Payment system not available. Please try again later.</div>';
            confirmBookingBtn.disabled = false;
            paymentResultModal.show();
            confirmationModal.hide();
            return;
        }

        fetch('/store-expected-amount', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify({ amount: totalCost })
        })
        .then(response => {
            console.log('Response from /store-expected-amount:', response.status, response.statusText);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                console.error('Failed to store expected amount:', data.errors);
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error preparing payment: ${data.errors}</div>`;
                confirmBookingBtn.disabled = false;
                paymentResultModal.show();
                confirmationModal.hide();
                return;
            }

            console.log('Initiating payment with:', { totalCost, email, phone, reference });

            const handler = PaystackPop.setup({
                key: window.PAYSTACK_PUBLIC_KEY || 'pk_test_f32ac6a155ff0bee5c5b86e25499cf957b6e8c51',
                email: email,
                amount: totalCost * 100, // Paystack expects amount in kobo
                currency: 'NGN',
                ref: reference,
                metadata: {
                    custom_fields: [
                        {
                            display_name: "Phone Number",
                            variable_name: "phone_number",
                            value: phone
                        },
                        {
                            display_name: "Full Name",
                            variable_name: "full_name",
                            value: `${firstName} ${lastName}`
                        }
                    ]
                },
                callback: function(response) {
                    console.log('Paystack payment response:', response);
                    const verifyReference = response.reference || response.ref || reference;
                    const verifyPayload = { reference: verifyReference };
                    console.log('Sending to /verify-payment:', verifyPayload);
                    fetch('/verify-payment', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                        },
                        body: JSON.stringify(verifyPayload)
                    })
                    .then(response => {
                        console.log('Response from /verify-payment:', response.status, response.statusText);
                        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Verification response:', data);
                        confirmationModal.hide();
                        paymentResultModal.show();
                        feedbackDiv.innerHTML = '';
                        if (data.status === 'success') {
                            fetch('/submit-booking', {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                                }
                            })
                            .then(response => {
                                console.log('Response from /submit-booking:', response.status, response.statusText);
                                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                                return response.json();
                            })
                            .then(data => {
                                console.log('Booking response:', data);
                                if (data.success) {
                                    feedbackDiv.innerHTML = '<div class="alert alert-success" role="alert">Booking and payment confirmed successfully!</div>';
                                    document.getElementById('bookingDetails').style.display = 'block';
                                    document.getElementById('printReceiptBtn').style.display = 'inline-block';
                                    document.getElementById('resultBookingId').textContent = data.booking_id || 'N/A';
                                    document.getElementById('resultGuestName').textContent = `${firstName} ${lastName}`;
                                    document.getElementById('resultEmail').textContent = email;
                                    document.getElementById('resultPhone').textContent = phone;
                                    document.getElementById('resultCheckin').textContent = formData.get('modalCheckin');
                                    document.getElementById('resultCheckout').textContent = formData.get('modalCheckout');
                                    document.getElementById('resultRoomType').textContent = document.getElementById('roomType').options[document.getElementById('roomType').selectedIndex].text;
                                    document.getElementById('resultGuests').textContent = formData.get('modalGuests');
                                    document.getElementById('resultRooms').textContent = formData.get('modalRooms');
                                    document.getElementById('resultTotalCost').textContent = totalCostRaw;
                                    document.getElementById('resultTransactionId').textContent = response.transaction || 'N/A';
                                } else {
                                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Booking error: ${data.errors}</div>`;
                                    document.getElementById('bookingDetails').style.display = 'none';
                                    document.getElementById('printReceiptBtn').style.display = 'none';
                                    confirmBookingBtn.disabled = false;
                                }
                            })
                            .catch(error => {
                                console.error('Error submitting booking:', error);
                                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error submitting booking: ${error.message}</div>`;
                                document.getElementById('bookingDetails').style.display = 'none';
                                document.getElementById('printReceiptBtn').style.display = 'none';
                                confirmBookingBtn.disabled = false;
                            });
                        } else {
                            console.error('Payment verification failed:', data.message);
                            feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Payment verification failed: ${data.message}</div>`;
                            document.getElementById('bookingDetails').style.display = 'none';
                            document.getElementById('printReceiptBtn').style.display = 'none';
                            confirmBookingBtn.disabled = false;
                        }
                    })
                    .catch(error => {
                        console.error('Error verifying payment:', error);
                        confirmationModal.hide();
                        paymentResultModal.show();
                        feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error verifying payment: ${error.message}</div>`;
                        document.getElementById('bookingDetails').style.display = 'none';
                        document.getElementById('printReceiptBtn').style.display = 'none';
                        confirmBookingBtn.disabled = false;
                    });
                },
                onClose: function() {
                    console.log('Payment modal closed');
                    confirmationModal.hide();
                    paymentResultModal.show();
                    feedbackDiv.innerHTML = '<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>';
                    document.getElementById('bookingDetails').style.display = 'none';
                    document.getElementById('printReceiptBtn').style.display = 'none';
                    confirmBookingBtn.disabled = false;
                }
            });
            try {
                handler.openIframe();
            } catch (error) {
                console.error('Paystack initialization error:', error);
                confirmationModal.hide();
                paymentResultModal.show();
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Payment initialization failed: ${error.message}</div>`;
                document.getElementById('bookingDetails').style.display = 'none';
                document.getElementById('printReceiptBtn').style.display = 'none';
                confirmBookingBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error storing expected amount:', error);
            confirmationModal.hide();
            paymentResultModal.show();
            feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error preparing payment: ${error.message}</div>`;
            document.getElementById('bookingDetails').style.display = 'none';
            document.getElementById('printReceiptBtn').style.display = 'none';
            confirmBookingBtn.disabled = false;
            document.getElementById('retryBookingBtn').style.display = 'inline-block';
        });
    });
} else {
    console.error("confirmBooking element not found");
}
});

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