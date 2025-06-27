document.addEventListener('DOMContentLoaded', function () {
    // Navbar scroll handling
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav ? mainNav.clientHeight : 0;

    if (mainNav) {
        window.addEventListener('scroll', function () {
            const currentTop = document.body.getBoundingClientRect().top * -1;
            if (currentTop < scrollPos) {
                // Scrolling Up
                if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-visible');
                } else {
                    console.log("Scrolling up, removing fixed/visible classes");
                    mainNav.classList.remove('is-visible', 'is-fixed');
                }
            } else {
                // Scrolling Down
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
        const capacity = selectedOption && selectedOption.getAttribute('data-capacity')
            ? parseInt(selectedOption.getAttribute('data-capacity'))
            : 0;
        const numRooms = parseInt(roomsSelect.value || 1);
        const totalGuests = capacity * numRooms;
        guestsInput.value = totalGuests;
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

        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        // Show loading spinner
        feedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        const formData = new FormData(form);
        fetch(window.availabilityCheckUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            feedbackDiv.innerHTML = ''; // Clear spinner

            // Display errors
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
            }

            // Display availability message
            else if (data.availability_message) {
                const messageDiv = document.createElement('div');
                if (data.availability_message === 'Room available') {
                 messageDiv.className = 'alert alert-success';
                 messageDiv.innerHTML = `
                        ${data.availability_message}<br>
                        Price per Room: $${data.base_price} per night<br>
                        Total cost: $${data.total_cost} for ${data.number_of_nights} nights<br>
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
            submitButton.disabled = false; // Re-enable button
        });
    });

    // Attach event listeners
    roomTypeSelect.addEventListener('change', updateGuests);
    roomsSelect.addEventListener('change', updateGuests);
    checkinInput.addEventListener('change', updateCheckoutMin);

    function openBookingModal() {
        // Get values from availability form
        const checkin = document.getElementById('checkin').value;
        const checkout = document.getElementById('checkout').value;
        const roomTypeSelect = document.getElementById('room_type');
        const selectedRoomTypeOption = roomTypeSelect.options[roomTypeSelect.selectedIndex];
        const roomTypeName = selectedRoomTypeOption.text;
        const slugifiedRoomType = roomTypeName.toLowerCase().replace(/\s+/g, '-');
        const guests = document.getElementById('guests').value;
        const rooms = document.getElementById('rooms').value;

        // Open modal
        const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
        modal.show();

        // Set values in modal form
        document.getElementById('modalCheckin').value = checkin;
        document.getElementById('modalCheckout').value = checkout;
        document.getElementById('roomType').value = slugifiedRoomType;
        document.getElementById('modalGuests').value = guests;
        document.getElementById('modalRooms').value = rooms;
    }

    // Initialize on page load
    updateGuests();
    updateCheckoutMin();

    // Modal handling
    window.showBookingModal = function () {
        var myModal = new bootstrap.Modal(document.getElementById('bookingModal'));
        myModal.show();
    };

    // Existing bookRoom function for room cards
    window.bookRoom = function (roomType) {
        console.log("Booking room:", roomType);
        document.getElementById('roomType').value = roomType;
    };
});