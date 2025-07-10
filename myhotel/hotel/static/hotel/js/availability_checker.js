document.addEventListener('DOMContentLoaded', function () {
    const roomTypeSelect = document.getElementById('room_type');
    const roomsSelect = document.getElementById('rooms');
    const guestsInput = document.getElementById('guests');
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    const form = document.getElementById('quickBookingForm');
    const feedbackDiv = document.getElementById('availability-feedback');

    if (!roomTypeSelect || !roomsSelect || !guestsInput || !checkinInput || !checkoutInput || !form || !feedbackDiv) {
        console.error("Form elements not found: ", {
            roomTypeSelect: !!roomTypeSelect,
            roomsSelect: !!roomsSelect,
            guestsInput: !!guestsInput,
            checkinInput: !!checkinInput,
            checkoutInput: !!checkoutInput,
            form: !!form,
            feedbackDiv: !!feedbackDiv
        });
        return;
    }

    const today = new Date().toISOString().split('T')[0];
    checkinInput.setAttribute('min', today);

    function updateGuests() {
        const selectedOption = roomTypeSelect.options[roomTypeSelect.selectedIndex];
        const capacity = selectedOption && selectedOption.value && selectedOption.getAttribute('data-capacity')
            ? parseInt(selectedOption.getAttribute('data-capacity'))
            : 0;
        const numRooms = parseInt(roomsSelect.value || 1);
        const totalGuests = capacity * numRooms;
        guestsInput.value = capacity ? totalGuests : '';
        console.log("Updated guests:", totalGuests, "Capacity:", capacity, "Rooms:", numRooms);
    }

    function updateCheckoutMin() {
        const checkinDate = checkinInput.value;
        if (checkinDate) {
            const minCheckoutDate = new Date(checkinDate);
            minCheckoutDate.setDate(minCheckoutDate.getDate() + 1);
            checkoutInput.setAttribute('min', minCheckoutDate.toISOString().split('T')[0]);
            if (checkoutInput.value && checkoutInput.value <= checkinDate) {
                checkoutInput.value = '';
            }
        } else {
            checkoutInput.setAttribute('min', today);
        }
    }

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

    // Enhanced function to check room availability with better error handling
    window.checkRoomAvailability = async function (checkin, checkout, roomTypeId, rooms, guests) {
        const csrfToken = getCSRFToken();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            return { errors: ['Security token not found. Please refresh the page and try again.'] };
        }

        const formData = new FormData();
        formData.append('checkin', checkin);
        formData.append('checkout', checkout);
        formData.append('room_type', roomTypeId);
        formData.append('rooms', rooms);
        formData.append('guest', guests || '');
        formData.append('csrfmiddlewaretoken', csrfToken);

        console.log('Sending availability check with data:', {
            checkin, checkout, roomTypeId, rooms, guests
        });

        // Retry mechanism for network failures
        const maxRetries = 3;
        let lastError = null;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.log(`Availability check attempt ${attempt}/${maxRetries}`);
                
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

                const response = await fetch(window.availabilityCheckUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    if (response.status === 403) {
                        throw new Error('Access denied. Please refresh the page and try again.');
                    } else if (response.status === 500) {
                        throw new Error('Server error. Please try again later.');
                    } else if (response.status === 0) {
                        throw new Error('Network connection failed. Please check your internet connection.');
                    } else {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                }

                const data = await response.json();
                console.log('Availability check response:', data);
                return data;

            } catch (error) {
                console.error(`Availability check attempt ${attempt} failed:`, error);
                lastError = error;
                
                // Don't retry for certain errors
                if (error.message.includes('Access denied') || 
                    error.message.includes('refresh the page') ||
                    error.name === 'AbortError') {
                    break;
                }
                
                // Wait before retrying (exponential backoff)
                if (attempt < maxRetries) {
                    const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
                    console.log(`Waiting ${delay}ms before retry...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }

        // All retries failed
        let errorMessage = 'Error checking availability. Please try again.';
        
        if (lastError) {
            if (lastError.name === 'AbortError') {
                errorMessage = 'Request timed out. Please check your internet connection and try again.';
            } else if (lastError.message.includes('Failed to fetch') || 
                       lastError.message.includes('ERR_CONNECTION_RESET') ||
                       lastError.message.includes('Network connection failed')) {
                errorMessage = 'Connection failed. Please check your internet connection and try again.';
            } else if (lastError.message.includes('ERR_SOCKET_NOT_CONNECTED')) {
                errorMessage = 'Network connection lost. Please check your internet connection and try again.';
            } else if (lastError.message) {
                errorMessage = lastError.message;
            }
        }
        
        return { 
            errors: [errorMessage],
            success: false
        };
    };

    // Handle form submission via AJAX
    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        console.log("Form submission intercepted, sending AJAX request");

        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        const formData = new FormData(form);
        console.log("Submitting availability check with data:", Object.fromEntries(formData));

        const data = await window.checkRoomAvailability(
            formData.get('checkin'),
            formData.get('checkout'),
            formData.get('room_type'),
            formData.get('rooms'),
            formData.get('guests')
        );

        feedbackDiv.innerHTML = '';

        if (data.errors && data.errors.length > 0) {
            const errorList = document.createElement('div');
            errorList.className = 'alert alert-danger';
            const ul = document.createElement('ul');
            ul.style.marginBottom = '0';
            data.errors.forEach(error => {
                const li = document.createElement('li');
                li.textContent = error;
                ul.appendChild(li);
            });
            errorList.appendChild(ul);
            
            // Add retry button for network errors
            if (data.errors.some(error => 
                error.includes('Connection failed') || 
                error.includes('Network connection') ||
                error.includes('timed out'))) {
                const retryBtn = document.createElement('button');
                retryBtn.textContent = 'Retry';
                retryBtn.className = 'btn btn-sm btn-outline-primary mt-2';
                retryBtn.onclick = () => form.dispatchEvent(new Event('submit'));
                errorList.appendChild(retryBtn);
            }
            
            feedbackDiv.appendChild(errorList);
        } else if (data.availability_message) {
            const messageDiv = document.createElement('div');
            if (data.availability_message === 'Room available') {
                messageDiv.className = 'alert alert-success';
                messageDiv.innerHTML = `
                    <i class="fas fa-check-circle"></i> ${data.availability_message}<br>
                    <button class="btn btn-primary mt-2" onclick="openBookingModal()">Book Now</button>
                `;
            } else {
                messageDiv.className = 'alert alert-warning';
                messageDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${data.availability_message}`;
            }
            feedbackDiv.appendChild(messageDiv);
        }

        submitButton.disabled = false;
    });

    roomTypeSelect.addEventListener('change', updateGuests);
    roomsSelect.addEventListener('change', updateGuests);
    checkinInput.addEventListener('change', updateCheckoutMin);

    updateGuests();
    updateCheckoutMin();
});