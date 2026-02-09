// Drag and drop functionality
const uploadArea = document.getElementById('uploadArea');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => {
        uploadArea.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, () => {
        uploadArea.classList.remove('dragover');
    }, false);
});

uploadArea.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadArea.addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

function handleFileUpload(input) {
    if (input.files && input.files[0]) {
        handleFile(input.files[0]);
    }
}

function handleFile(file) {
    const fileName = document.getElementById('fileName');
    const clearBtn = document.getElementById('clearBtn');
    
    fileName.textContent = file.name;
    fileName.style.display = 'block';
    clearBtn.style.display = 'flex';
    
    // Visual feedback
    uploadArea.style.borderColor = '#059669';
    uploadArea.style.background = '#ECFDF5';
}

function clearFile() {
    const fileName = document.getElementById('fileName');
    const clearBtn = document.getElementById('clearBtn');
    const fileInput = document.getElementById('fileInput');
    
    fileInput.value = '';
    fileName.style.display = 'none';
    clearBtn.style.display = 'none';
    
    // Reset visual state
    uploadArea.style.borderColor = '#D1D5DB';
    uploadArea.style.background = '#FAFAFA';
}