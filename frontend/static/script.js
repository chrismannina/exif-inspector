document.addEventListener('DOMContentLoaded', function() {
    // Form submission handlers
    setupFormHandler('exifForm', '/api/v1/exif/analyze');
    setupFormHandler('recipeForm', '/api/v1/exif/fuji');
    setupFormHandler('filenameForm', '/api/v1/exif/rename');
    setupFormHandler('batchForm', '/api/v1/exif/batch');

    // Clear results button
    document.getElementById('clearResults').addEventListener('click', function() {
        document.getElementById('results').innerHTML = 'No results yet. Use one of the forms above to analyze images.';
    });
});

function setupFormHandler(formId, endpoint) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        // Get form data
        const formData = new FormData();
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            if (fileInput.multiple) {
                // For batch processing, append multiple files
                for (let i = 0; i < fileInput.files.length; i++) {
                    formData.append('files', fileInput.files[i]);
                }
            } else {
                // For single file uploads
                formData.append('file', fileInput.files[0]);
            }
        }
        
        // Add any other form fields
        const otherInputs = form.querySelectorAll('input:not([type="file"])');
        otherInputs.forEach(input => {
            if (input.value) {
                formData.append(input.name, input.value);
            }
        });
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');
        submitBtn.disabled = true;
        if (spinner) spinner.style.display = 'inline-block';
        
        // Clear previous results
        const resultsArea = document.getElementById('results');
        resultsArea.innerHTML = 'Processing...';
        
        // Make API request
        fetch(endpoint, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Format and display the results
            resultsArea.innerHTML = formatJsonOutput(data);
        })
        .catch(error => {
            resultsArea.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        })
        .finally(() => {
            // Reset loading state
            submitBtn.disabled = false;
            if (spinner) spinner.style.display = 'none';
        });
    });
}

function formatJsonOutput(obj) {
    // Function to syntax highlight JSON
    const json = JSON.stringify(obj, null, 2);
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, 
        function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
} 