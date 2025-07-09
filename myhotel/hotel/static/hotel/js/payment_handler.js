document.addEventListener('DOMContentLoaded', function () {
    // Confirm booking handler with Paystack payment
    const confirmBookingBtn = document.getElementById('confirmBooking');
    if (confirmBookingBtn) {
        confirmBookingBtn.addEventListener('click', async function () {
            const formData = window.currentBookingData;
            if (!formData) {
                console.error('No booking data available');
                return;
            }
            
            const confirmationModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
            const paymentResultModal = new bootstrap.Modal(document.getElementById('paymentResultModal'), { backdrop: 'static' });
            const feedbackDiv = document.getElementById('paymentResultFeedback');
            const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));

            feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            confirmBookingBtn.disabled = true;

            // Function to re-enable button and show retry option
            const enableRetry = () => {
                confirmBookingBtn.disabled = false;
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryBookingBtn');
                    if (retryBtn) {
                        retryBtn.style.display = 'inline-block';
                    }
                }, 100);
            };

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
                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">${
                        availability.errors?.length > 0 ? availability.errors.join(', ') : availability.availability_message
                    }</div>`;
                    enableRetry();
                    paymentResultModal.show();
                    confirmationModal.hide();
                    return;
                }
            } catch (error) {
                console.error('Availability check error:', error);
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error checking availability: ${error.message}</div>`;
                enableRetry();
                paymentResultModal.show();
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

            // Validation checks
            if (!totalCost || isNaN(totalCost) || totalCost <= 0) {
                console.error('Invalid total cost:', totalCostRaw);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Invalid booking amount. Please check your booking details.</div>';
                enableRetry();
                paymentResultModal.show();
                confirmationModal.hide();
                return;
            }
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                console.error('Invalid email:', email);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid email is required.</div>';
                enableRetry();
                paymentResultModal.show();
                confirmationModal.hide();
                return;
            }
            if (!phone || !/^\+?\d{10,15}$/.test(phone)) {
                console.error('Invalid phone:', phone);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Valid phone number is required (e.g., +2347034618587).</div>';
                enableRetry();
                paymentResultModal.show();
                confirmationModal.hide();
                return;
            }

            // Wait for Paystack to be available using event listener
            const waitForPaystack = () => {
                return new Promise((resolve, reject) => {
                    if (typeof PaystackPop !== 'undefined') {
                        console.log('PaystackPop already available');
                        resolve();
                        return;
                    }
                    
                    console.log('Waiting for Paystack to load...');
                    
                    // Listen for the custom event
                    const paystackReadyHandler = () => {
                        console.log('Paystack ready event received');
                        if (typeof PaystackPop !== 'undefined') {
                            window.removeEventListener('paystackReady', paystackReadyHandler);
                            resolve();
                        } else {
                            console.error('Paystack ready event fired but PaystackPop still undefined');
                            reject(new Error('Paystack SDK loaded but PaystackPop not available'));
                        }
                    };
                    
                    window.addEventListener('paystackReady', paystackReadyHandler);
                    
                    // Fallback timeout
                    setTimeout(() => {
                        window.removeEventListener('paystackReady', paystackReadyHandler);
                        if (typeof PaystackPop !== 'undefined') {
                            resolve();
                        } else {
                            reject(new Error('Paystack SDK failed to load within timeout'));
                        }
                    }, 10000); // 10 second timeout
                });
            };

            try {
                await waitForPaystack();
                console.log('Paystack is now available, proceeding with payment setup');
            } catch (error) {
                console.error('Paystack SDK not available:', error);
                feedbackDiv.innerHTML = '<div class="alert alert-danger" role="alert">Payment system not available. Please try again later.</div>';
                enableRetry();
                paymentResultModal.show();
                confirmationModal.hide();
                return;
            }

            // Store expected amount
            try {
                const storeResponse = await fetch('/hotel/store-expected-amount', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    },
                    body: JSON.stringify({ amount: totalCost })
                });

                if (!storeResponse.ok) {
                    throw new Error(`HTTP error! Status: ${storeResponse.status}`);
                }

                const storeData = await storeResponse.json();
                if (!storeData.success) {
                    console.error('Failed to store expected amount:', storeData.errors);
                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error preparing payment: ${storeData.errors}</div>`;
                    enableRetry();
                    paymentResultModal.show();
                    confirmationModal.hide();
                    return;
                }

                console.log('Initiating payment with:', { totalCost, email, phone, reference });

                // Check which Paystack API is available
                let paystackAPI = null;
                let handler = null;

                if (typeof PaystackPop !== 'undefined' && typeof PaystackPop.setup === 'function') {
                    paystackAPI = 'PaystackPop';
                    console.log('Using PaystackPop API');
                } else if (typeof Paystack !== 'undefined' && typeof Paystack.setup === 'function') {
                    paystackAPI = 'Paystack';
                    console.log('Using Paystack API');
                } else {
                    throw new Error('No valid Paystack API found');
                }

                console.log('Using Paystack API:', paystackAPI);
                console.log('PAYSTACK_PUBLIC_KEY:', window.PAYSTACK_PUBLIC_KEY);

                // Create payment configuration
                const paymentConfig = {
                    key: window.PAYSTACK_PUBLIC_KEY,
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
                    }
                };

                // Add callbacks based on API version
                if (paystackAPI === 'PaystackPop') {
                    paymentConfig.callback = function(response) {
                        console.log('Paystack payment response:', response);
                        const verifyReference = response.reference || response.ref || reference;
                        handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry);
                    };
                    paymentConfig.onClose = function() {
                        console.log('Payment modal closed');
                        confirmationModal.hide();
                        paymentResultModal.show();
                        feedbackDiv.innerHTML = `<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>`;
                        document.getElementById('bookingDetails').style.display = 'none';
                        document.getElementById('printReceiptBtn').style.display = 'none';
                        enableRetry();
                    };
                } else if (paystackAPI === 'Paystack') {
                    paymentConfig.onSuccess = function(response) {
                        console.log('Paystack payment response:', response);
                        const verifyReference = response.reference || response.ref || reference;
                        handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry);
                    };
                    paymentConfig.onCancel = function() {
                        console.log('Payment modal closed');
                        confirmationModal.hide();
                        paymentResultModal.show();
                        feedbackDiv.innerHTML = `<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>`;
                        document.getElementById('bookingDetails').style.display = 'none';
                        document.getElementById('printReceiptBtn').style.display = 'none';
                        enableRetry();
                    };
                }

                console.log('Payment config:', paymentConfig);

                // Setup payment handler
                try {
                    if (paystackAPI === 'PaystackPop') {
                        handler = PaystackPop.setup(paymentConfig);
                    } else if (paystackAPI === 'Paystack') {
                        handler = Paystack.setup(paymentConfig);
                    }
                    console.log('Payment handler created successfully:', handler);
                } catch (setupError) {
                    console.error('Paystack setup error details:', setupError);
                    throw new Error(`Paystack setup failed: ${setupError.message}`);
                }
                
                try {
                    handler.openIframe();
                } catch (error) {
                    console.error('Paystack initialization error:', error);
                    confirmationModal.hide();
                    paymentResultModal.show();
                    feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Payment initialization failed: ${error.message}</div>`;
                    document.getElementById('bookingDetails').style.display = 'none';
                    document.getElementById('printReceiptBtn').style.display = 'none';
                    enableRetry();
                }
            } catch (error) {
                console.error('Error in payment setup:', error);
                confirmationModal.hide();
                paymentResultModal.show();
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error preparing payment: ${error.message}</div>`;
                document.getElementById('bookingDetails').style.display = 'none';
                document.getElementById('printReceiptBtn').style.display = 'none';
                enableRetry();
            }
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

// Separate function to handle payment success
async function handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry) {
    try {
        // Verify payment
        const verifyResponse = await fetch('/hotel/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify({ reference: verifyReference })
        });

        if (!verifyResponse.ok) {
            throw new Error(`HTTP error! Status: ${verifyResponse.status}`);
        }

        const verifyData = await verifyResponse.json();
        console.log('Verification response:', verifyData);
        
        confirmationModal.hide();
        paymentResultModal.show();
        feedbackDiv.innerHTML = '';
        
        if (verifyData.status === 'success') {
            // Submit booking
            const bookingResponse = await fetch('/hotel/submit-booking', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            if (!bookingResponse.ok) {
                throw new Error(`HTTP error! Status: ${bookingResponse.status}`);
            }

            const bookingData = await bookingResponse.json();
            console.log('Booking response:', bookingData);
            
            if (bookingData.success) {
                feedbackDiv.innerHTML = '<div class="alert alert-success" role="alert">Booking and payment confirmed successfully!</div>';
                document.getElementById('bookingDetails').style.display = 'block';
                document.getElementById('printReceiptBtn').style.display = 'inline-block';
                document.getElementById('retryBookingBtn').style.display = 'none';
                
                // Populate booking details
                document.getElementById('resultBookingId').textContent = bookingData.booking_id || 'N/A';
                document.getElementById('resultGuestName').textContent = `${firstName} ${lastName}`;
                document.getElementById('resultEmail').textContent = email;
                document.getElementById('resultPhone').textContent = phone;
                document.getElementById('resultCheckin').textContent = formData.get('modalCheckin');
                document.getElementById('resultCheckout').textContent = formData.get('modalCheckout');
                document.getElementById('resultRoomType').textContent = document.getElementById('roomType').options[document.getElementById('roomType').selectedIndex].text;
                document.getElementById('resultGuests').textContent = formData.get('modalGuests');
                document.getElementById('resultRooms').textContent = formData.get('modalRooms');
                document.getElementById('resultTotalCost').textContent = totalCostRaw;
                document.getElementById('resultTransactionId').textContent = verifyReference;
            } else {
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Booking error: ${bookingData.errors}</div>`;
                document.getElementById('bookingDetails').style.display = 'none';
                document.getElementById('printReceiptBtn').style.display = 'none';
                enableRetry();
            }
        } else {
            console.error('Payment verification failed:', verifyData.message);
            feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Payment verification failed: ${verifyData.message}</div>`;
            document.getElementById('bookingDetails').style.display = 'none';
            document.getElementById('printReceiptBtn').style.display = 'none';
            enableRetry();
        }
    } catch (error) {
        console.error('Error in payment callback:', error);
        confirmationModal.hide();
        paymentResultModal.show();
        feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error processing payment: ${error.message}</div>`;
        document.getElementById('bookingDetails').style.display = 'none';
        document.getElementById('printReceiptBtn').style.display = 'none';
        enableRetry();
    }
}