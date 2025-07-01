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

    // Reusable function to check room availability
    window.checkRoomAvailability = async function (checkin, checkout, roomTypeId, rooms, guests) {
        const formData = new FormData();
        formData.append('checkin', checkin);
        formData.append('checkout', checkout);
        formData.append('room_type', roomTypeId);
        formData.append('rooms', rooms);
        formData.append('guest', guests || ''); // Send guest, default to empty string if null
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        try {
            const response = await fetch(window.availabilityCheckUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Availability check error:', error);
            return { errors: ['Error checking availability: ' + error.message] };
        }
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

        submitButton.disabled = false;
    });

    roomTypeSelect.addEventListener('change', updateGuests);
    roomsSelect.addEventListener('change', updateGuests);
    checkinInput.addEventListener('change', updateCheckoutMin);

    updateGuests();
    updateCheckoutMin();
});