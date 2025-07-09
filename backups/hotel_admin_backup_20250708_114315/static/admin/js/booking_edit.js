document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('editBookingForm');
    const roomSelect = document.getElementById('roomSelect');
    const checkinInput = document.getElementById('checkinInput');
    const checkoutInput = document.getElementById('checkoutInput');
    const feedbackDiv = document.getElementById('availability-feedback');

    async function checkRoomAvailability() {
        const roomId = roomSelect.value;
        const checkin = checkinInput.value;
        const checkout = checkoutInput.value;
        const bookingId = form.dataset.bookingId || '';
        if (!roomId || !checkin || !checkout) {
            feedbackDiv.innerHTML = '';
            return true;
        }
        feedbackDiv.innerHTML = '<span class="text-blue-700">Checking availability...</span>';
        try {
            const resp = await fetch(`/api/check-room-availability/?room_id=${roomId}&checkin=${checkin}&checkout=${checkout}&booking_id=${bookingId}`);
            const data = await resp.json();
            if (data.available) {
                feedbackDiv.innerHTML = '<span class="text-green-700">Room is available for the selected dates.</span>';
                return true;
            } else {
                feedbackDiv.innerHTML = `<span class="text-red-700">Room is NOT available for the selected dates.${data.error ? ' ' + data.error : ''}</span>`;
                return false;
            }
        } catch (e) {
            feedbackDiv.innerHTML = '<span class="text-red-700">Error checking availability.</span>';
            return false;
        }
    }

    roomSelect.addEventListener('change', checkRoomAvailability);
    checkinInput.addEventListener('change', checkRoomAvailability);
    checkoutInput.addEventListener('change', checkRoomAvailability);

    form.addEventListener('submit', async function (e) {
        const available = await checkRoomAvailability();
        if (!available) {
            e.preventDefault();
            alert('Selected room is not available for the chosen dates.');
        }
    });
});
