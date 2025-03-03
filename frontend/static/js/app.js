document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('preview-container');
    const fileName = document.getElementById('file-name');
    const uploadBtn = document.getElementById('upload-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsArea = document.getElementById('results-area');
    const endpointSelect = document.getElementById('endpoint');

    // API base URL - update this to match your FastAPI server
    const API_BASE_URL = 'http://localhost:8000';

    // Add event listeners for drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle file input change
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    // Click on drop area to open file dialog
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle the selected files
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            // Show preview
            previewContainer.style.display = 'block';
            fileName.textContent = file.name;
            
            // Create object URL for preview
            const objectUrl = URL.createObjectURL(file);
            imagePreview.src = objectUrl;
            
            // Enable upload button
            uploadBtn.disabled = false;
        }
    }

    // Handle the upload button click
    uploadBtn.addEventListener('click', async () => {
        if (fileInput.files.length === 0) {
            return;
        }

        // Show loading spinner
        loadingSpinner.style.display = 'inline-block';
        uploadBtn.disabled = true;

        // Get selected endpoint
        const endpoint = endpointSelect.value;
        
        try {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error('Error uploading file:', error);
            resultsArea.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
        } finally {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            uploadBtn.disabled = false;
        }
    });

    // Function to format and display JSON results
    function displayResults(data) {
        resultsArea.innerHTML = formatJSON(data);
    }

    // Function to format JSON with syntax highlighting
    function formatJSON(obj, indent = 0) {
        const indentStr = '&nbsp;'.repeat(indent * 4);
        
        if (obj === null) {
            return `<span class="null">null</span>`;
        }
        
        if (typeof obj === 'object') {
            if (Array.isArray(obj)) {
                if (obj.length === 0) {
                    return `<span class="array">[]</span>`;
                }
                
                let result = `[\n`;
                
                obj.forEach((item, index) => {
                    result += `${indentStr}&nbsp;&nbsp;&nbsp;&nbsp;${formatJSON(item, indent + 1)}`;
                    if (index < obj.length - 1) {
                        result += ',';
                    }
                    result += '\n';
                });
                
                result += `${indentStr}]`;
                return result;
            } else {
                const keys = Object.keys(obj);
                
                if (keys.length === 0) {
                    return `<span class="object">{}</span>`;
                }
                
                let result = `{\n`;
                
                keys.forEach((key, index) => {
                    result += `${indentStr}&nbsp;&nbsp;&nbsp;&nbsp;<span class="key">"${key}"</span>: ${formatJSON(obj[key], indent + 1)}`;
                    if (index < keys.length - 1) {
                        result += ',';
                    }
                    result += '\n';
                });
                
                result += `${indentStr}}`;
                return result;
            }
        } else if (typeof obj === 'string') {
            return `<span class="string">"${htmlEscape(obj)}"</span>`;
        } else if (typeof obj === 'number') {
            return `<span class="number">${obj}</span>`;
        } else if (typeof obj === 'boolean') {
            return `<span class="boolean">${obj}</span>`;
        }
        
        return String(obj);
    }

    // Escape HTML special characters
    function htmlEscape(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}); 