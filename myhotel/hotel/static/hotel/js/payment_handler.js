document.addEventListener('DOMContentLoaded', function () {
    // Confirm booking handler with Paystack payment
    const confirmBookingBtn = document.getElementById('confirmBooking');
    if (confirmBookingBtn) {
        confirmBookingBtn.addEventListener('click', async function () {
            const formData = window.currentBookingData;
            const confirmationModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
            const paymentResultModal = new bootstrap.Modal(document.getElementById('paymentResultModal'), { backdrop: 'static' });
            const feedbackDiv = document.getElementById('paymentResultFeedback');
            const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));

            feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            confirmBookingBtn.disabled = true;

            // Check room availability
            try {
                const availability = await window.checkRoomAvailability(
                    formData.get('modalCheckin'),
                    formData.get('modalCheckout'),
                    formData.get('roomType'),
                    formData.get('modalRooms'),
                    formData.get('modalGuests')
                );
                if (availability.errors?.length > 0 || availability.availability_message !== 'Room available') {
                    console.error('Rooms not available:', availability.errors?.length > 0 ? availability.errors : availability.availability_message);
                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">${
                        availability.errors?.length > 0 ? availability.errors.join(', ') : availability.availability_message
                    }</div>`;
                    confirmBookingBtn.disabled = false;
                    paymentResultModal.show();
                    setTimeout(() => {
                        const retryBtn = document.getElementById('retryBookingBtn');
                        if (retryBtn) {
                            retryBtn.style.display = 'inline-block';
                        } else {
                            console.error('retryBookingBtn not found in DOM');
                        }
                    }, 100); // Delay to ensure modal is rendered
                    confirmationModal.hide();
                    return;
                }
            } catch (error) {
                console.error('Availability check error:', error);
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error checking availability: ${error.message}</div>`;
                confirmBookingBtn.disabled = false;
                paymentResultModal.show();
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmationModal.hide();
                return;
            }

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
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmationModal.hide();
                return;
            }
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                console.error('Invalid email:', email);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid email is required.</div>';
                confirmBookingBtn.disabled = false;
                paymentResultModal.show();
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmationModal.hide();
                return;
            }
            if (!phone || !/^\+?\d{10,15}$/.test(phone)) {
                console.error('Invalid phone:', phone);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid phone number is required (e.g., +2347034618587).</div>';
                confirmBookingBtn.disabled = false;
                paymentResultModal.show();
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmationModal.hide();
                return;
            }
            if (typeof PaystackPop === 'undefined') {
                console.error('Paystack SDK not loaded');
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Payment system not available. Please try again later.</div>';
                confirmBookingBtn.disabled = false;
                paymentResultModal.show();
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmationModal.hide();
                return;
            }

            // Store expected amount
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
                    setTimeout(() => {
                        const retryBtn = document.getElementById('retryBookingBtn');
                        if (retryBtn) {
                            retryBtn.style.display = 'inline-block';
                        } else {
                            console.error('retryBookingBtn not found in DOM');
                        }
                    }, 100);
                    confirmationModal.hide();
                    return;
                }

                console.log('Initiating payment with:', { totalCost, email, phone, reference });

                const handler = PaystackPop.setup({
                    key: window.PAYSTACK_PUBLIC_KEY || 'pk_test_f32ac6a155ff0bee5c5b86e25499cf957b6e8c51',
                    email: email,
                    amount: totalCost * 100,
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
                                        document.getElementById('retryBookingBtn').style.display = 'none';
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
                                        setTimeout(() => {
                                            const retryBtn = document.getElementById('retryBookingBtn');
                                            if (retryBtn) {
                                                retryBtn.style.display = 'inline-block';
                                            } else {
                                                console.error('retryBookingBtn not found in DOM');
                                            }
                                        }, 100);
                                        confirmBookingBtn.disabled = false;
                                    }
                                })
                                .catch(error => {
                                    console.error('Error submitting booking:', error);
                                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error submitting booking: ${error.message}</div>`;
                                    document.getElementById('bookingDetails').style.display = 'none';
                                    document.getElementById('printReceiptBtn').style.display = 'none';
                                    setTimeout(() => {
                                        const retryBtn = document.getElementById('retryBookingBtn');
                                        if (retryBtn) {
                                            retryBtn.style.display = 'inline-block';
                                        } else {
                                            console.error('retryBookingBtn not found in DOM');
                                        }
                                    }, 100);
                                    confirmBookingBtn.disabled = false;
                                });
                            } else {
                                console.error('Payment verification failed:', data.message);
                                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Payment verification failed: ${data.message}</div>`;
                                document.getElementById('bookingDetails').style.display = 'none';
                                document.getElementById('printReceiptBtn').style.display = 'none';
                                setTimeout(() => {
                                    const retryBtn = document.getElementById('retryBookingBtn');
                                    if (retryBtn) {
                                        retryBtn.style.display = 'inline-block';
                                    } else {
                                        console.error('retryBookingBtn not found in DOM');
                                    }
                                }, 100);
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
                            setTimeout(() => {
                                const retryBtn = document.getElementById('retryBookingBtn');
                                if (retryBtn) {
                                    retryBtn.style.display = 'inline-block';
                                } else {
                                    console.error('retryBookingBtn not found in DOM');
                                }
                            }, 100);
                            confirmBookingBtn.disabled = false;
                        });
                    },
                    onClose: function() {
                        console.log('Payment modal closed');
                        confirmationModal.hide();
                        paymentResultModal.show();
                        feedbackDiv.innerHTML = `<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>`;
                        document.getElementById('bookingDetails').style.display = 'none';
                        document.getElementById('printReceiptBtn').style.display = 'none';
                        setTimeout(() => {
                            const retryBtn = document.getElementById('retryBookingBtn');
                            if (retryBtn) {
                                retryBtn.style.display = 'inline-block';
                            } else {
                                console.error('retryBookingBtn not found in DOM');
                            }
                        }, 100);
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
                    setTimeout(() => {
                        const retryBtn = document.getElementById('retryBookingBtn');
                        if (retryBtn) {
                            retryBtn.style.display = 'inline-block';
                        } else {
                            console.error('retryBookingBtn not found in DOM');
                        }
                    }, 100);
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
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    } else {
                        console.error('retryBookingBtn not found in DOM');
                    }
                }, 100);
                confirmBookingBtn.disabled = false;
            });
        });
    } else {
        console.error("confirmBooking element not found");
    }

    // Retry booking handler
    const retryBookingBtn = document.getElementById('retryBookingBtn');
    if (retryBookingBtn) {
        retryBookingBtn.addEventListener('click', function () {
            const paymentResultModal = bootstrap.Modal.getInstance(document.getElementById('paymentResultModal'));
            const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));
            paymentResultModal.hide();
            bookingModal.show();
        });
    } else {
        console.error("retryBookingBtn element not found");
    }
});