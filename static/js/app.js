// Malawi School Reporting System - JavaScript Functions

// Global utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content area
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-MW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function resetForm(formId) {
    const form = document.getElementById(formId);
    form.reset();
    
    // Remove validation classes
    const inputs = form.querySelectorAll('.is-invalid, .is-valid');
    inputs.forEach(input => {
        input.classList.remove('is-invalid', 'is-valid');
    });
}

// API helper functions
async function makeApiRequest(url, data, method = 'POST') {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

async function downloadFile(url, data, filename) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Download failed');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        return true;
    } catch (error) {
        console.error('Download failed:', error);
        throw error;
    }
}

// Navigation highlighting
function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Form validation styling
function addFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required')) {
                    if (this.value.trim()) {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    } else {
                        this.classList.remove('is-valid');
                        this.classList.add('is-invalid');
                    }
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    });
}

// Loading states
function setButtonLoading(buttonElement, isLoading, originalText = null) {
    if (isLoading) {
        if (!originalText) {
            originalText = buttonElement.innerHTML;
        }
        buttonElement.setAttribute('data-original-text', originalText);
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        buttonElement.disabled = true;
    } else {
        const original = buttonElement.getAttribute('data-original-text');
        if (original) {
            buttonElement.innerHTML = original;
            buttonElement.removeAttribute('data-original-text');
        }
        buttonElement.disabled = false;
    }
}

// Keyboard shortcuts
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save/update settings
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const updateButton = document.querySelector('button[onclick*="updateSettings"]');
            if (updateButton) {
                updateButton.click();
            }
        }
        
        // Ctrl+Enter to generate reports
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            const generateButtons = document.querySelectorAll('button[onclick*="generate"]');
            if (generateButtons.length > 0) {
                generateButtons[0].click();
            }
        }
        
        // Escape to clear outputs
        if (e.key === 'Escape') {
            const outputs = document.querySelectorAll('[id*="Output"]');
            outputs.forEach(output => {
                if (output.innerHTML.trim()) {
                    output.innerHTML = '<p class="text-muted">Output cleared...</p>';
                }
            });
        }
    });
}

// Auto-save functionality for settings
function enableAutoSave() {
    const settingsInputs = document.querySelectorAll('#settingsForm input');
    
    settingsInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Save to localStorage
            localStorage.setItem(this.id, this.value);
        });
        
        // Load from localStorage
        const savedValue = localStorage.getItem(input.id);
        if (savedValue) {
            input.value = savedValue;
        }
    });
}

// Print functionality
function printReport(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Malawi School Report</title>
                <style>
                    body { font-family: 'Courier New', monospace; margin: 20px; }
                    pre { white-space: pre-wrap; font-size: 12px; }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    highlightActiveNavItem();
    addFormValidation();
    addKeyboardShortcuts();
    enableAutoSave();
    
    // Add print buttons to report outputs
    const reportOutputs = document.querySelectorAll('[id*="Output"]');
    reportOutputs.forEach(output => {
        if (output.id) {
            const printButton = document.createElement('button');
            printButton.className = 'btn btn-outline-secondary btn-sm mt-2';
            printButton.innerHTML = '<i class="fas fa-print me-1"></i>Print';
            printButton.onclick = () => printReport(output.id);
            output.parentNode.appendChild(printButton);
        }
    });
    
    // Show welcome message on dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        setTimeout(() => {
            showNotification('Welcome to Malawi School Reporting System v2.0! 🇲🇼', 'success');
        }, 1000);
    }
});

// Export functions for global use
window.MalawiSchoolSystem = {
    showNotification,
    formatDateTime,
    validateForm,
    resetForm,
    makeApiRequest,
    downloadFile,
    setButtonLoading,
    printReport
};