// Toggle sidebar functionality
const toggleSidebar = document.getElementById('toggleSidebar');
const closeSidebar = document.getElementById('closeSidebar');
const sidebar = document.getElementById('sidebar');
const contentArea = document.getElementById('mainContent');
const mobileOverlay = document.getElementById('mobileOverlay');
let sidebarExpanded = true;

// Function to check if we're on mobile
function isMobile() {
    return window.innerWidth < 1024; // lg breakpoint
}

// Function to show sidebar on mobile
function showMobileSidebar() {
    sidebar.classList.remove('-translate-x-full');
    mobileOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Function to hide sidebar on mobile
function hideMobileSidebar() {
    sidebar.classList.add('-translate-x-full');
    mobileOverlay.classList.add('hidden');
    document.body.style.overflow = '';
}

// Function to toggle sidebar on desktop
function toggleDesktopSidebar() {
    sidebarExpanded = !sidebarExpanded;
    if (sidebarExpanded) {
        sidebar.classList.remove('sidebar-mini', 'w-20');
        sidebar.classList.add('w-64');
        contentArea.classList.remove('lg:ml-20');
        contentArea.classList.add('lg:ml-64');
    } else {
        sidebar.classList.add('sidebar-mini', 'w-20');
        sidebar.classList.remove('w-64');
        contentArea.classList.remove('lg:ml-64');
        contentArea.classList.add('lg:ml-20');
    }
}

// Main toggle function
function handleSidebarToggle() {
    if (isMobile()) {
        if (sidebar.classList.contains('-translate-x-full')) {
            showMobileSidebar();
        } else {
            hideMobileSidebar();
        }
    } else {
        toggleDesktopSidebar();
    }
}

// Dropdown functionality
function initializeDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdownId = this.getAttribute('data-dropdown');
            const menu = document.getElementById(dropdownId + '-menu');
            const arrow = this.querySelector('.dropdown-arrow');
            
            if (menu) {
                const isOpen = menu.classList.contains('open');
                
                // For nested dropdowns, don't close parent when opening child
                const isChildDropdown = this.closest('.dropdown-menu');
                
                if (!isChildDropdown) {
                    // Close all other top-level dropdowns
                    document.querySelectorAll('.dropdown-menu').forEach(otherMenu => {
                        if (otherMenu !== menu && !otherMenu.contains(menu)) {
                            otherMenu.classList.remove('open');
                        }
                    });
                    
                    // Close all other arrows that are not parents of current menu
                    document.querySelectorAll('.dropdown-arrow').forEach(otherArrow => {
                        if (otherArrow !== arrow && !otherArrow.closest('.dropdown').contains(menu)) {
                            otherArrow.classList.remove('rotated');
                        }
                    });
                } else {
                    // For child dropdowns, only close sibling dropdowns
                    const parentDropdown = this.closest('.dropdown-menu');
                    parentDropdown.querySelectorAll('.dropdown-menu').forEach(siblingMenu => {
                        if (siblingMenu !== menu) {
                            siblingMenu.classList.remove('open');
                        }
                    });
                    
                    parentDropdown.querySelectorAll('.dropdown-arrow').forEach(siblingArrow => {
                        if (siblingArrow !== arrow) {
                            siblingArrow.classList.remove('rotated');
                        }
                    });
                }
                
                // Toggle current dropdown
                if (isOpen) {
                    menu.classList.remove('open');
                    arrow.classList.remove('rotated');
                    // Close all child dropdowns
                    menu.querySelectorAll('.dropdown-menu').forEach(childMenu => {
                        childMenu.classList.remove('open');
                    });
                    menu.querySelectorAll('.dropdown-arrow').forEach(childArrow => {
                        childArrow.classList.remove('rotated');
                    });
                } else {
                    menu.classList.add('open');
                    arrow.classList.add('rotated');
                }
            }
        });
    });
    
    // Prevent dropdown menus from closing when clicking inside them
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        // Only close if clicking completely outside any dropdown
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('open');
            });
            document.querySelectorAll('.dropdown-arrow').forEach(arrow => {
                arrow.classList.remove('rotated');
            });
        }
    });
}

// Event listeners
if (toggleSidebar) {
    toggleSidebar.addEventListener('click', handleSidebarToggle);
}

if (closeSidebar) {
    closeSidebar.addEventListener('click', hideMobileSidebar);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener('click', hideMobileSidebar);
}

// Handle window resize
window.addEventListener('resize', function() {
    if (!isMobile()) {
        // Reset mobile styles when switching to desktop
        mobileOverlay.classList.add('hidden');
        document.body.style.overflow = '';
        sidebar.classList.remove('-translate-x-full');
    } else {
        // Reset desktop styles when switching to mobile
        sidebar.classList.remove('sidebar-mini', 'w-20');
        sidebar.classList.add('w-64');
        contentArea.classList.remove('lg:ml-20');
        contentArea.classList.add('lg:ml-64');
        // Hide sidebar on mobile by default
        if (!sidebar.classList.contains('-translate-x-full')) {
            hideMobileSidebar();
        }
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (isMobile()) {
        hideMobileSidebar();
    }
    initializeDropdowns();
});