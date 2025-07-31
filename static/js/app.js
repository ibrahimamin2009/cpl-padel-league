// CPL - Chiniot Padel League Management System
// JavaScript for interactive features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Add smooth scrolling
    addSmoothScrolling();
    
    // Add card hover effects
    addCardHoverEffects();
    
    // Add flash message auto-dismiss
    addFlashMessageDismiss();
    
    // Initialize mobile navigation
    initMobileNavigation();
}

function addSmoothScrolling() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function addCardHoverEffects() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.stat-card, .match-card, .team-card, .admin-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
        });
    });
}

function addFlashMessageDismiss() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    // Add to page
    const container = document.querySelector('.flash-messages') || document.querySelector('.main-content');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto-dismiss
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}

function initMobileNavigation() {
    // Mobile navigation toggle functionality
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileNavToggle && navMenu) {
        mobileNavToggle.addEventListener('click', function() {
            navMenu.classList.toggle('mobile-active');
            
            // Change icon
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('mobile-active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !mobileNavToggle.contains(e.target)) {
                navMenu.classList.remove('mobile-active');
                const icon = mobileNavToggle.querySelector('i');
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close mobile menu when clicking on a link
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('mobile-active');
                const icon = mobileNavToggle.querySelector('i');
                icon.className = 'fas fa-bars';
            });
        });
    }
}

// Global function for mobile nav toggle (for onclick)
function toggleMobileNav() {
    const navMenu = document.getElementById('nav-menu');
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    
    if (navMenu && mobileNavToggle) {
        navMenu.classList.toggle('mobile-active');
        
        // Change icon
        const icon = mobileNavToggle.querySelector('i');
        if (navMenu.classList.contains('mobile-active')) {
            icon.className = 'fas fa-times';
        } else {
            icon.className = 'fas fa-bars';
        }
    }
}

// Export functions for global use
window.CPL = {
    showNotification
}; 