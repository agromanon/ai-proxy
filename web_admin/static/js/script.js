// AI Proxy Admin JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle form submissions with confirmation
    var confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var message = form.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Handle delete buttons with confirmation
    var deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var message = button.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (confirm(message)) {
                // Create a form to submit the delete request
                var form = document.createElement('form');
                form.method = 'POST';
                form.action = button.href;
                
                // Add CSRF token if needed
                var csrfToken = document.querySelector('meta[name="csrf-token"]');
                if (csrfToken) {
                    var tokenInput = document.createElement('input');
                    tokenInput.type = 'hidden';
                    tokenInput.name = '_token';
                    tokenInput.value = csrfToken.content;
                    form.appendChild(tokenInput);
                }
                
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
    
    // Handle test buttons
    var testButtons = document.querySelectorAll('[data-action="test"]');
    testButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var buttonOriginalText = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
            button.disabled = true;
            
            // Make AJAX request to test endpoint
            fetch(button.href, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    alert('Test successful!');
                } else {
                    alert('Test failed: ' + data.message);
                }
            })
            .catch(function(error) {
                alert('Test failed: ' + error.message);
            })
            .finally(function() {
                button.innerHTML = buttonOriginalText;
                button.disabled = false;
            });
        });
    });
    
    // Handle copy to clipboard buttons
    var copyButtons = document.querySelectorAll('[data-action="copy"]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var target = button.getAttribute('data-target');
            var text = document.querySelector(target).innerText;
            
            navigator.clipboard.writeText(text).then(function() {
                var originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                setTimeout(function() {
                    button.innerHTML = originalText;
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
            });
        });
    });
    
    // Handle dynamic form fields (for headers, etc.)
    var addFieldButtons = document.querySelectorAll('[data-action="add-field"]');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var container = document.querySelector(button.getAttribute('data-target'));
            var template = button.getAttribute('data-template');
            
            // Create new field from template
            var newField = document.createElement('div');
            newField.innerHTML = template;
            newField.className = 'row mb-2';
            
            // Add remove button
            var removeButton = document.createElement('div');
            removeButton.className = 'col-md-1';
            removeButton.innerHTML = '<button type="button" class="btn btn-danger btn-sm" data-action="remove-field"><i class="bi bi-trash"></i></button>';
            newField.appendChild(removeButton);
            
            container.appendChild(newField);
            
            // Add event listener to remove button
            var removeBtn = newField.querySelector('[data-action="remove-field"]');
            removeBtn.addEventListener('click', function() {
                newField.remove();
            });
        });
    });
    
    // Handle form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Utility functions
function showAlert(message, type) {
    var alertContainer = document.getElementById('alert-container') || document.querySelector('.container-fluid');
    if (alertContainer) {
        var alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = message + 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

function togglePasswordVisibility(fieldId) {
    var field = document.getElementById(fieldId);
    var icon = document.querySelector('[data-target="#' + fieldId + '"] i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'bi bi-eye';
    }
}