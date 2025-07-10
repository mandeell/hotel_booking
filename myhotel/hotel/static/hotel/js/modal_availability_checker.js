document.addEventListener('DOMContentLoaded', function () {
    // Add availability checking to booking modal
    const modalForm = document.getElementById('fullBookingForm');
    const modalCheckinInput = document.getElementById('modalCheckin');
    const modalCheckoutInput = document.getElementById('modalCheckout');
    const modalRoomTypeSelect = document.getElementById('roomType');
    const modalRoomsSelect = document.getElementById('modalRooms');
    const modalGuestsInput = document.getElementById('modalGuests');

    if (!modalForm) {
        console.error('Modal form not found');
        return;
    }

    // Create feedback div for modal if it doesn't exist
    let modalFeedbackDiv = document.getElementById('modal-availability-feedback');
    if (!modalFeedbackDiv) {
        modalFeedbackDiv = document.createElement('div');
        modalFeedbackDiv.id = 'modal-availability-feedback';
        modalFeedbackDiv.className = 'mt-3';
        
        // Insert before the modal footer
        const modalBody = document.querySelector('#bookingModal .modal-body');
        if (modalBody) {
            modalBody.appendChild(modalFeedbackDiv);
        }
    }

    // Function to check availability in modal
    async function checkModalAvailability() {
        if (!modalCheckinInput?.value || !modalCheckoutInput?.value || 
            !modalRoomTypeSelect?.value || !modalRoomsSelect?.value) {
            modalFeedbackDiv.innerHTML = '';
            return;
        }

        modalFeedbackDiv.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Checking availability...</span></div> Checking availability...</div>';

        try {
            const result = await window.checkRoomAvailability(
                modalCheckinInput.value,
                modalCheckoutInput.value,
                modalRoomTypeSelect.value,
                modalRoomsSelect.value,
                modalGuestsInput.value
            );

            modalFeedbackDiv.innerHTML = '';

            if (result.errors && result.errors.length > 0) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger alert-sm';
                errorDiv.innerHTML = `<strong>Availability Issue:</strong><br>${result.errors.join('<br>')}`;
                modalFeedbackDiv.appendChild(errorDiv);
                
                // Disable submit button
                const submitBtn = document.getElementById('submitBooking');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Room Not Available';
                }
            } else if (result.availability_message) {
                if (result.availability_message === 'Room available') {
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success alert-sm';
                    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${result.availability_message}`;
                    modalFeedbackDiv.appendChild(successDiv);
                    
                    // Enable submit button
                    const submitBtn = document.getElementById('submitBooking');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Proceed to Confirmation';
                    }
                } else {
                    const warningDiv = document.createElement('div');
                    warningDiv.className = 'alert alert-warning alert-sm';
                    warningDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${result.availability_message}`;
                    modalFeedbackDiv.appendChild(warningDiv);
                    
                    // Disable submit button for unavailable rooms
                    const submitBtn = document.getElementById('submitBooking');
                    if (submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.textContent = 'Room Not Available';
                    }
                }
            }
        } catch (error) {
            console.error('Modal availability check error:', error);
            modalFeedbackDiv.innerHTML = `<div class="alert alert-danger alert-sm">Error checking availability: ${error.message}</div>`;
            
            // Disable submit button on error
            const submitBtn = document.getElementById('submitBooking');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Error - Try Again';
            }
        }
    }

    // Debounce function to avoid too many API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const debouncedCheck = debounce(checkModalAvailability, 500);

    // Add event listeners to modal form fields
    if (modalCheckinInput) modalCheckinInput.addEventListener('change', debouncedCheck);
    if (modalCheckoutInput) modalCheckoutInput.addEventListener('change', debouncedCheck);
    if (modalRoomTypeSelect) modalRoomTypeSelect.addEventListener('change', debouncedCheck);
    if (modalRoomsSelect) modalRoomsSelect.addEventListener('change', debouncedCheck);

    // Check availability when modal is shown
    const bookingModal = document.getElementById('bookingModal');
    if (bookingModal) {
        bookingModal.addEventListener('shown.bs.modal', function () {
            // Small delay to ensure all fields are populated
            setTimeout(checkModalAvailability, 100);
        });
    }

    // Reset feedback when modal is hidden
    if (bookingModal) {
        bookingModal.addEventListener('hidden.bs.modal', function () {
            modalFeedbackDiv.innerHTML = '';
            const submitBtn = document.getElementById('submitBooking');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Proceed to Confirmation';
            }
        });
    }
});