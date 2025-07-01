document.addEventListener('DOMContentLoaded', function () {
    // Navbar scroll handling
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav ? mainNav.clientHeight : 0;

    if (mainNav) {
        window.addEventListener('scroll', function () {
            const currentTop = document.body.getBoundingClientRect().top * -1;
            if (currentTop < scrollPos) {
                if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-visible');
                } else {
                    mainNav.classList.remove('is-visible', 'is-fixed');
                }
            } else {
                mainNav.classList.remove('is-visible');
                if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-fixed');
                }
            }
            scrollPos = currentTop;
        });
    }

    // Form handling
    const roomTypeSelect = document.getElementById('room_type');
    const roomsSelect = document.getElementById('rooms');
    const guestsInput = document.getElementById('guests');
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    const form = document.getElementById('quickBookingForm');
    const feedbackDiv = document.getElementById('availability-feedback');

    // Check if elements exist
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

    // Set minimum date for check-in to today
    const today = new Date().toISOString().split('T')[0];
    checkinInput.setAttribute('min', today);

    // Update guests based on room type and number of rooms
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

    // Update check-out minimum date based on check-in
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

    // Handle form submission via AJAX
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        console.log("Form submission intercepted, sending AJAX request");

        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        const formData = new FormData(form);
        console.log("Submitting availability check with data:", Object.fromEntries(formData));
        fetch(window.availabilityCheckUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received response:", data);
            feedbackDiv.innerHTML = '';

            if (data.errors && data.errors.length > 0) {
                const errorList = document.createElement('div');
                errorList.className = 'alert alert-danger';
                const ul = document.createElement('ul');
                data.errors.forEach(error => {
                    const li = document.createElement('li');
                    li.textContent = error;
                    ul.appendChild(li);
                });
                errorList.appendChild(ul);
                feedbackDiv.appendChild(errorList);
            } else if (data.availability_message) {
                const messageDiv = document.createElement('div');
                if (data.availability_message === 'Room available') {
                    messageDiv.className = 'alert alert-success';
                    messageDiv.innerHTML = `
                        ${data.availability_message}<br>
                        <button class="btn btn-primary mt-2" onclick="openBookingModal()">Book Now</button>
                    `;
                } else {
                    messageDiv.className = 'alert alert-danger';
                    messageDiv.textContent = data.availability_message;
                }
                feedbackDiv.appendChild(messageDiv);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            feedbackDiv.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
        })
        .finally(() => {
            submitButton.disabled = false;
        });
    });

    // Attach event listeners
    roomTypeSelect.addEventListener('change', updateGuests);
    roomsSelect.addEventListener('change', updateGuests);
    checkinInput.addEventListener('change', updateCheckoutMin);

    // Initialize on page load
    updateGuests();
    updateCheckoutMin();

    // Modal handling
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

            updateModalCheckoutMin();
            updateBookingPrices();
        } catch (error) {
            console.error("Error in openBookingModal:", error);
        }
    };

    // Book room from room cards
    window.bookRoom = function (roomTypeId) {
        console.log("Booking room:", roomTypeId);
        document.getElementById('roomType').value = roomTypeId;
        window.openBookingModal();
    };
});