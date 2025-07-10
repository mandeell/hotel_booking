document.addEventListener('DOMContentLoaded', function () {
    // Helper function to get CSRF token
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         getCookie('csrftoken');
        return csrfToken;
    }

    // Helper function to get cookie value
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Enhanced fetch with retry mechanism
    async function fetchWithRetry(url, options, maxRetries = 3) {
        let lastError = null;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(`Fetch attempt ${attempt}/${maxRetries} to ${url}`);
                
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000);
                
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                return response;
                
            } catch (error) {
                console.error(`Fetch attempt ${attempt} failed:`, error);
                lastError = error;
                
                // Don't retry for certain errors
                if (error.name === 'AbortError' || 
                    error.message.includes('403') ||
                    error.message.includes('401')) {
                    break;
                }
                
                // Wait before retrying
                if (attempt < maxRetries) {
                    const delay = Math.pow(2, attempt) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        throw lastError;
    }

    // Confirm booking handler with modern Paystack payment
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
                    formData.get('modalRooms'),
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

            // Wait for Paystack to be available
            const waitForPaystack = () => {
                return new Promise((resolve, reject) => {
                    if (typeof PaystackPop !== 'undefined') {
                        console.log('PaystackPop already available');
                        resolve();
                        return;
                    }
                    
                    console.log('Waiting for Paystack to load...');
                    
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
                    }, 10000);
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

            // Store expected amount with retry mechanism
            try {
                const csrfToken = getCSRFToken();
                if (!csrfToken) {
                    throw new Error('CSRF token not found. Please refresh the page and try again.');
                }

                const storeResponse = await fetchWithRetry('/hotel/store-expected-amount', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ amount: totalCost })
                });

                if (!storeResponse.ok) {
                    let errorMessage = `Failed to prepare payment (${storeResponse.status})`;
                    try {
                        const errorData = await storeResponse.json();
                        errorMessage = errorData.errors || errorMessage;
                    } catch (e) {
                        console.error('Error parsing store amount error response:', e);
                    }
                    throw new Error(errorMessage);
                }

                const storeData = await storeResponse.json();
                if (!storeData.success) {
                    console.error('Failed to store expected amount:', storeData.errors);
                    throw new Error(storeData.errors || 'Failed to prepare payment');
                }

                console.log('Initiating payment with:', { totalCost, email, phone, reference });

                // Use modern Paystack API
                let paystack = null;
                
                try {
                    // Try modern constructor first
                    paystack = new PaystackPop();
                } catch (constructorError) {
                    console.log('Modern constructor failed, trying legacy setup:', constructorError);
                    // Fallback to legacy API
                    if (typeof PaystackPop.setup === 'function') {
                        paystack = PaystackPop.setup({
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
                            },
                            callback: function(response) {
                                console.log('Paystack payment response:', response);
                                const verifyReference = response.reference || response.ref || reference;
                                handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry);
                            },
                            onClose: function() {
                                console.log('Payment modal closed');
                                confirmationModal.hide();
                                paymentResultModal.show();
                                feedbackDiv.innerHTML = `<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>`;
                                document.getElementById('bookingDetails').style.display = 'none';
                                document.getElementById('printReceiptBtn').style.display = 'none';
                                enableRetry();
                            }
                        });
                    } else {
                        throw new Error('No valid Paystack API found');
                    }
                }

                if (paystack) {
                    if (typeof paystack.newTransaction === 'function') {
                        // Modern API
                        paystack.newTransaction({
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
                            },
                            onSuccess: function(response) {
                                console.log('Paystack payment response:', response);
                                const verifyReference = response.reference || response.ref || reference;
                                handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry);
                            },
                            onCancel: function() {
                                console.log('Payment modal closed');
                                confirmationModal.hide();
                                paymentResultModal.show();
                                feedbackDiv.innerHTML = `<div class="alert alert-warning" role="alert">Payment was not completed. Please try again.</div>`;
                                document.getElementById('bookingDetails').style.display = 'none';
                                document.getElementById('printReceiptBtn').style.display = 'none';
                                enableRetry();
                            }
                        });
                    } else if (typeof paystack.openIframe === 'function') {
                        // Legacy API
                        paystack.openIframe();
                    } else if (typeof paystack.open === 'function') {
                        // Modern open method
                        paystack.open();
                    } else {
                        throw new Error('No valid payment method found on Paystack instance');
                    }
                } else {
                    throw new Error('Failed to initialize Paystack');
                }

            } catch (error) {
                console.error('Error in payment setup:', error);
                confirmationModal.hide();
                paymentResultModal.show();
                
                let errorMessage = error.message;
                if (error.message.includes('Failed to fetch') || 
                    error.message.includes('ERR_CONNECTION_RESET') ||
                    error.message.includes('ERR_SOCKET_NOT_CONNECTED')) {
                    errorMessage = 'Network connection failed. Please check your internet connection and try again.';
                }
                
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error preparing payment: ${errorMessage}</div>`;
                document.getElementById('bookingDetails').style.display = 'none';
                document.getElementById('printReceiptBtn').style.display = 'none';
                enableRetry();
            }
        });
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
    }
});

// Enhanced payment success handler with retry mechanism
async function handlePaymentSuccess(verifyReference, formData, confirmationModal, paymentResultModal, feedbackDiv, firstName, lastName, email, phone, totalCostRaw, enableRetry) {
    try {
        console.log('Starting payment verification for reference:', verifyReference);
        
        function getCSRFToken() {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                             getCookie('csrftoken');
            return csrfToken;
        }

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Enhanced fetch with retry
        async function fetchWithRetry(url, options, maxRetries = 3) {
            let lastError = null;
            
            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 30000);
                    
                    const response = await fetch(url, {
                        ...options,
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    return response;
                    
                } catch (error) {
                    lastError = error;
                    if (attempt < maxRetries && 
                        !error.message.includes('403') && 
                        !error.message.includes('401')) {
                        const delay = Math.pow(2, attempt) * 1000;
                        await new Promise(resolve => setTimeout(resolve, delay));
                    } else {
                        break;
                    }
                }
            }
            
            throw lastError;
        }

        const csrfToken = getCSRFToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found. Please refresh the page and try again.');
        }

        // Verify payment with retry mechanism
        const verifyResponse = await fetchWithRetry('/hotel/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ reference: verifyReference })
        });

        console.log('Verify response status:', verifyResponse.status);

        if (!verifyResponse.ok) {
            let errorMessage = `Payment verification failed (${verifyResponse.status})`;
            try {
                const errorData = await verifyResponse.json();
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                console.error('Error parsing verification error response:', e);
            }
            throw new Error(errorMessage);
        }

        const verifyData = await verifyResponse.json();
        console.log('Verification response:', verifyData);
        
        confirmationModal.hide();
        paymentResultModal.show();
        feedbackDiv.innerHTML = '';
        
        if (verifyData.status === 'success') {
            console.log('Payment verified successfully, submitting booking...');
            
            // Add payment verification data to form
            formData.append('transaction_id', verifyData.transaction_id || verifyReference);
            formData.append('payment_status', 'success');
            
            // Submit booking with retry mechanism
            const bookingResponse = await fetchWithRetry('/hotel/submit-booking', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            console.log('Booking response status:', bookingResponse.status);

            if (!bookingResponse.ok) {
                let errorMessage = `Booking submission failed (${bookingResponse.status})`;
                try {
                    const errorData = await bookingResponse.json();
                    errorMessage = errorData.errors || errorMessage;
                } catch (e) {
                    console.error('Error parsing booking error response:', e);
                }
                throw new Error(errorMessage);
            }

            const bookingData = await bookingResponse.json();
            console.log('Booking response:', bookingData);
            
            if (bookingData.success) {
                feedbackDiv.innerHTML = '<div class="alert alert-success" role="alert"><i class="fas fa-check-circle"></i> Booking and payment confirmed successfully!</div>';
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
                document.getElementById('resultTransactionId').textContent = verifyData.transaction_id || verifyReference;
            } else {
                console.error('Booking submission failed:', bookingData.errors);
                feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i> Booking error: ${bookingData.errors}</div>`;
                document.getElementById('bookingDetails').style.display = 'none';
                document.getElementById('printReceiptBtn').style.display = 'none';
                enableRetry();
            }
        } else {
            console.error('Payment verification failed:', verifyData.message);
            feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert"><i class="fas fa-times-circle"></i> Payment verification failed: ${verifyData.message}</div>`;
            document.getElementById('bookingDetails').style.display = 'none';
            document.getElementById('printReceiptBtn').style.display = 'none';
            enableRetry();
        }
    } catch (error) {
        console.error('Error in payment callback:', error);
        confirmationModal.hide();
        paymentResultModal.show();
        
        let errorMessage = error.message;
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('ERR_CONNECTION_RESET') ||
            error.message.includes('ERR_SOCKET_NOT_CONNECTED')) {
            errorMessage = 'Network connection failed during payment processing. Please check your internet connection and contact support if the issue persists.';
        }
        
        feedbackDiv.innerHTML = `<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i> Error processing payment: ${errorMessage}</div>`;
        document.getElementById('bookingDetails').style.display = 'none';
        document.getElementById('printReceiptBtn').style.display = 'none';
        enableRetry();
    }
}