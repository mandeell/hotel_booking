/**
 * Soft Delete Confirmation System
 * Handles delete confirmations with flash messages instead of separate pages
 */

class SoftDeleteConfirmation {
    constructor() {
        this.init();
    }

    init() {
        // Add event listeners to all delete buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.soft-delete-btn, .soft-delete-btn *')) {
                e.preventDefault();
                const button = e.target.closest('.soft-delete-btn');
                this.showConfirmation(button);
            }
        });
    }

    showConfirmation(button) {
        const itemName = button.dataset.itemName || 'this item';
        const itemType = button.dataset.itemType || 'item';
        const deleteUrl = button.dataset.deleteUrl;
        const redirectUrl = button.dataset.redirectUrl;

        // Create modal HTML
        const modalHtml = `
            <div id="deleteConfirmModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
                <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
                    <div class="p-6">
                        <div class="flex items-center mb-4">
                            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                                <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">Confirm Deletion</h3>
                                <p class="text-sm text-gray-600">This action cannot be undone</p>
                            </div>
                        </div>
                        
                        <div class="mb-6">
                            <p class="text-gray-700">
                                Are you sure you want to delete <strong>"${itemName}"</strong>?
                            </p>
                            <p class="text-sm text-gray-500 mt-2">
                                The ${itemType} will be moved to trash and can be restored later if needed.
                            </p>
                        </div>
                        
                        <div class="flex justify-end space-x-3">
                            <button type="button" id="cancelDelete" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors">
                                Cancel
                            </button>
                            <button type="button" id="confirmDelete" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                                <i class="fas fa-trash mr-2"></i>
                                Yes, Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Add event listeners
        document.getElementById('cancelDelete').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('confirmDelete').addEventListener('click', () => {
            this.performDelete(deleteUrl, redirectUrl, itemName);
        });

        // Close on background click
        document.getElementById('deleteConfirmModal').addEventListener('click', (e) => {
            if (e.target.id === 'deleteConfirmModal') {
                this.closeModal();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    async performDelete(deleteUrl, redirectUrl, itemName) {
        try {
            // Show loading state
            const confirmBtn = document.getElementById('confirmDelete');
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Deleting...';
            confirmBtn.disabled = true;

            // Get CSRF token from cookie or form
            const csrfToken = this.getCSRFToken();

            // Perform delete request
            const response = await fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    'confirm_delete': true
                })
            });

            if (response.ok) {
                const result = await response.json();
                
                // Close modal
                this.closeModal();
                
                // Show success message
                this.showFlashMessage('success', result.message || `"${itemName}" has been deleted successfully.`);
                
                // Redirect or reload
                if (redirectUrl) {
                    setTimeout(() => {
                        window.location.href = redirectUrl;
                    }, 1500);
                } else {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete item');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showFlashMessage('error', error.message || 'An error occurred while deleting the item.');
            
            // Reset button
            const confirmBtn = document.getElementById('confirmDelete');
            confirmBtn.innerHTML = '<i class="fas fa-trash mr-2"></i>Yes, Delete';
            confirmBtn.disabled = false;
        }
    }

    closeModal() {
        const modal = document.getElementById('deleteConfirmModal');
        if (modal) {
            modal.remove();
        }
    }

    getCSRFToken() {
        // Try to get CSRF token from various sources
        let token = null;
        
        // 1. Try to get from form input
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            token = csrfInput.value;
        }
        
        // 2. Try to get from meta tag
        if (!token) {
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                token = csrfMeta.getAttribute('content');
            }
        }
        
        // 3. Try to get from cookie
        if (!token) {
            token = this.getCookie('csrftoken');
        }
        
        return token;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showFlashMessage(type, message) {
        const alertClass = type === 'success' ? 'bg-green-100 border-green-400 text-green-700' : 'bg-red-100 border-red-400 text-red-700';
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        const flashHtml = `
            <div id="flashMessage" class="fixed top-4 right-4 z-50 max-w-md">
                <div class="border-l-4 p-4 rounded-lg shadow-lg ${alertClass}">
                    <div class="flex items-center">
                        <i class="fas ${icon} mr-3"></i>
                        <p class="font-medium">${message}</p>
                        <button type="button" class="ml-auto text-lg font-semibold" onclick="this.parentElement.parentElement.parentElement.remove()">
                            &times;
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', flashHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const flash = document.getElementById('flashMessage');
            if (flash) {
                flash.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SoftDeleteConfirmation();
});