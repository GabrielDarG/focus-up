document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.amigos-toggle-btn');
    const contentSections = document.querySelectorAll('.amigos-secao-conteudo');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            
            toggleButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');

            contentSections.forEach(section => {
                if (section.id === targetId.substring(1)) {
                    section.classList.add('active');
                } else {
                    section.classList.remove('active');
                }
            });
        });
    });
});