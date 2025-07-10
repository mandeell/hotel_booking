// Modal Management System
class ModalManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.handleFlashMessages();
    }

    // Show confirmation modal
    showConfirmation(title, message, onConfirm, options = {}) {
        const modal = document.getElementById('confirmationModal');
        const titleEl = document.getElementById('confirmationTitle');
        const messageEl = document.getElementById('confirmationMessage');
        const confirmBtn = document.getElementById('confirmationConfirm');
        const cancelBtn = document.getElementById('confirmationCancel');
        const iconEl = document.getElementById('confirmationIcon');

        titleEl.textContent = title;
        messageEl.textContent = message;

        // Set icon and button colors based on type
        if (options.type === 'danger') {
            iconEl.className = 'fas fa-exclamation-triangle text-red-600 text-xl';
            confirmBtn.className = 'px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-24 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300';
        } else if (options.type === 'warning') {
            iconEl.className = 'fas fa-exclamation-triangle text-yellow-600 text-xl';
            confirmBtn.className = 'px-4 py-2 bg-yellow-500 text-white text-base font-medium rounded-md w-24 hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-300';
        } else {
            iconEl.className = 'fas fa-question-circle text-blue-600 text-xl';
            confirmBtn.className = 'px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-24 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300';
        }

        confirmBtn.textContent = options.confirmText || 'Confirm';

        // Remove existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        // Add new event listeners
        newConfirmBtn.addEventListener('click', () => {
            this.hideModal('confirmationModal');
            if (onConfirm) onConfirm();
        });

        newCancelBtn.addEventListener('click', () => {
            this.hideModal('confirmationModal');
        });

        this.showModal('confirmationModal');
    }

    // Show success modal
    showSuccess(message, onOk = null) {
        const modal = document.getElementById('successModal');
        const messageEl = document.getElementById('successMessage');
        const okBtn = document.getElementById('successOk');

        messageEl.textContent = message;

        // Remove existing event listener
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);

        newOkBtn.addEventListener('click', () => {
            this.hideModal('successModal');
            if (onOk) onOk();
        });

        this.showModal('successModal');
    }

    // Show error modal
    showError(message, onOk = null) {
        const modal = document.getElementById('errorModal');
        const messageEl = document.getElementById('errorMessage');
        const okBtn = document.getElementById('errorOk');

        messageEl.textContent = message;

        // Remove existing event listener
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);

        newOkBtn.addEventListener('click', () => {
            this.hideModal('errorModal');
            if (onOk) onOk();
        });

        this.showModal('errorModal');
    }

    // Show warning modal
    showWarning(message, onOk = null) {
        const modal = document.getElementById('warningModal');
        const messageEl = document.getElementById('warningMessage');
        const okBtn = document.getElementById('warningOk');

        messageEl.textContent = message;

        // Remove existing event listener
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);

        newOkBtn.addEventListener('click', () => {
            this.hideModal('warningModal');
            if (onOk) onOk();
        });

        this.showModal('warningModal');
    }

    // Show info modal
    showInfo(message, onOk = null) {
        const modal = document.getElementById('infoModal');
        const messageEl = document.getElementById('infoMessage');
        const okBtn = document.getElementById('infoOk');

        messageEl.textContent = message;

        // Remove existing event listener
        const newOkBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newOkBtn, okBtn);

        newOkBtn.addEventListener('click', () => {
            this.hideModal('infoModal');
            if (onOk) onOk();
        });

        this.showModal('infoModal');
    }

    // Show user status toggle modal
    showUserStatusModal(username, isActive, onConfirm) {
        const modal = document.getElementById('userStatusModal');
        const titleEl = document.getElementById('userStatusTitle');
        const messageEl = document.getElementById('userStatusMessage');
        const confirmBtn = document.getElementById('userStatusConfirm');
        const cancelBtn = document.getElementById('userStatusCancel');
        const iconEl = document.getElementById('userStatusIcon');

        const action = isActive ? 'deactivate' : 'activate';
        const actionTitle = isActive ? 'Deactivate User' : 'Activate User';
        
        titleEl.textContent = actionTitle;
        messageEl.textContent = `Are you sure you want to ${action} user "${username}"?`;
        confirmBtn.textContent = action.charAt(0).toUpperCase() + action.slice(1);

        // Set icon and colors based on action
        if (isActive) {
            iconEl.className = 'fas fa-user-slash text-orange-600 text-xl';
            confirmBtn.className = 'px-4 py-2 bg-orange-500 text-white text-base font-medium rounded-md w-24 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-300';
        } else {
            iconEl.className = 'fas fa-user-check text-green-600 text-xl';
            confirmBtn.className = 'px-4 py-2 bg-green-500 text-white text-base font-medium rounded-md w-24 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300';
        }

        // Remove existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        // Add new event listeners
        newConfirmBtn.addEventListener('click', () => {
            this.hideModal('userStatusModal');
            if (onConfirm) onConfirm();
        });

        newCancelBtn.addEventListener('click', () => {
            this.hideModal('userStatusModal');
        });

        this.showModal('userStatusModal');
    }

    // Show role remove modal
    showRoleRemoveModal(username, roleName, onConfirm) {
        const modal = document.getElementById('roleRemoveModal');
        const messageEl = document.getElementById('roleRemoveMessage');
        const confirmBtn = document.getElementById('roleRemoveConfirm');
        const cancelBtn = document.getElementById('roleRemoveCancel');

        messageEl.textContent = `Are you sure you want to remove the "${roleName}" role from user "${username}"?`;

        // Remove existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        // Add new event listeners
        newConfirmBtn.addEventListener('click', () => {
            this.hideModal('roleRemoveModal');
            if (onConfirm) onConfirm();
        });

        newCancelBtn.addEventListener('click', () => {
            this.hideModal('roleRemoveModal');
        });

        this.showModal('roleRemoveModal');
    }

    // Show logout confirmation modal
    showLogoutModal(onConfirm) {
        const modal = document.getElementById('logoutModal');
        const confirmBtn = document.getElementById('logoutConfirm');
        const cancelBtn = document.getElementById('logoutCancel');

        // Remove existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        // Add new event listeners
        newConfirmBtn.addEventListener('click', () => {
            this.hideModal('logoutModal');
            if (onConfirm) onConfirm();
        });

        newCancelBtn.addEventListener('click', () => {
            this.hideModal('logoutModal');
        });

        this.showModal('logoutModal');
    }

    // Generic show modal
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    }

    // Generic hide modal
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    }

    // Hide all modals
    hideAllModals() {
        const modals = ['confirmationModal', 'successModal', 'errorModal', 'warningModal', 'infoModal', 'userStatusModal', 'roleRemoveModal', 'logoutModal'];
        modals.forEach(modalId => this.hideModal(modalId));
    }

    // Bind global events
    bindEvents() {
        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('bg-gray-600')) {
                this.hideAllModals();
            }
        });

        // Close modals with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    // Handle existing flash messages and convert them to modals
    handleFlashMessages() {
        const messageContainer = document.querySelector('.space-y-3');
        if (messageContainer) {
            const messages = messageContainer.querySelectorAll('[class*="bg-"]');
            messages.forEach(messageEl => {
                const text = messageEl.textContent.trim();
                const icon = messageEl.querySelector('i');
                
                if (icon) {
                    if (icon.classList.contains('fa-check-circle')) {
                        this.showSuccess(text);
                    } else if (icon.classList.contains('fa-exclamation-circle')) {
                        this.showError(text);
                    } else if (icon.classList.contains('fa-exclamation-triangle')) {
                        this.showWarning(text);
                    } else if (icon.classList.contains('fa-info-circle')) {
                        this.showInfo(text);
                    }
                }
            });
            
            // Hide the original message container
            messageContainer.style.display = 'none';
        }
    }

    // Utility method to submit form after confirmation
    confirmAndSubmit(form, title, message, options = {}) {
        this.showConfirmation(title, message, () => {
            form.submit();
        }, options);
    }

    // Utility method to navigate after confirmation
    confirmAndNavigate(url, title, message, options = {}) {
        this.showConfirmation(title, message, () => {
            window.location.href = url;
        }, options);
    }
}

// Initialize modal manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.modalManager = new ModalManager();
    
    // Initialize AJAX delete handlers
    initAjaxDeleteHandlers();
});

// AJAX Delete Handler for permissions, roles, etc.
function initAjaxDeleteHandlers() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.ajax-delete-btn, .ajax-delete-btn *')) {
            e.preventDefault();
            const button = e.target.closest('.ajax-delete-btn');
            handleAjaxDelete(button);
        }
    });
}

function handleAjaxDelete(button) {
    const itemName = button.dataset.itemName || 'this item';
    const itemType = button.dataset.itemType || 'item';
    const deleteUrl = button.dataset.deleteUrl;
    const redirectUrl = button.dataset.redirectUrl;

    if (window.modalManager) {
        window.modalManager.showConfirmation(
            `Delete ${itemType.charAt(0).toUpperCase() + itemType.slice(1)}`,
            `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
            function() {
                performAjaxDelete(deleteUrl, redirectUrl, itemName, itemType);
            },
            { type: 'danger', confirmText: 'Delete' }
        );
    }
}

async function performAjaxDelete(deleteUrl, redirectUrl, itemName, itemType) {
    try {
        // Get CSRF token
        const csrfToken = getCSRFToken();

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

        const result = await response.json();

        if (response.ok && result.success) {
            // Show success message
            if (window.modalManager) {
                window.modalManager.showSuccess(
                    result.message || `"${itemName}" has been deleted successfully.`,
                    function() {
                        if (redirectUrl) {
                            window.location.href = redirectUrl;
                        } else {
                            window.location.reload();
                        }
                    }
                );
            }
        } else {
            throw new Error(result.message || 'Failed to delete item');
        }
    } catch (error) {
        console.error('Delete error:', error);
        if (window.modalManager) {
            window.modalManager.showError(
                error.message || 'An error occurred while deleting the item.'
            );
        }
    }
}

function getCSRFToken() {
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
        token = getCookie('csrftoken');
    }
    
    return token;
}

function getCookie(name) {
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

// Utility functions for easy access
function showConfirmation(title, message, onConfirm, options = {}) {
    if (window.modalManager) {
        window.modalManager.showConfirmation(title, message, onConfirm, options);
    }
}

function showSuccess(message, onOk = null) {
    if (window.modalManager) {
        window.modalManager.showSuccess(message, onOk);
    }
}

function showError(message, onOk = null) {
    if (window.modalManager) {
        window.modalManager.showError(message, onOk);
    }
}

function showWarning(message, onOk = null) {
    if (window.modalManager) {
        window.modalManager.showWarning(message, onOk);
    }
}

function showInfo(message, onOk = null) {
    if (window.modalManager) {
        window.modalManager.showInfo(message, onOk);
    }
}

function showUserStatusModal(username, isActive, onConfirm) {
    if (window.modalManager) {
        window.modalManager.showUserStatusModal(username, isActive, onConfirm);
    }
}

function showRoleRemoveModal(username, roleName, onConfirm) {
    if (window.modalManager) {
        window.modalManager.showRoleRemoveModal(username, roleName, onConfirm);
    }
}

function showLogoutConfirmation() {
    if (window.modalManager) {
        window.modalManager.showLogoutModal(function() {
            // Redirect to logout URL
            window.location.href = '/admin/logout/';
        });
    }
}