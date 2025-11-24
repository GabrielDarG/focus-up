document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('.avatar-upload-input input[type="file"]');
    const fileNameDisplay = document.getElementById('file-name-display');

    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0] ? e.target.files[0].name : 'Nenhum arquivo selecionado';
            fileNameDisplay.textContent = fileName;
        });
    }
});