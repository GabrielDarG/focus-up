document.addEventListener('DOMContentLoaded', () => {
    
    // Animação de Entrada (Serve para Login e Cadastro)
    const cartao = document.querySelector('.cartao-login, .cartao-cadastro');
    if (cartao) {
        setTimeout(() => {
            cartao.classList.add('visivel');
        }, 100);
    }

    // Lógica de Mostrar/Esconder Senha (Múltiplos Campos)
    const toggleBtns = document.querySelectorAll('.toggle-senha');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = targetId 
                ? document.getElementById(targetId) 
                : btn.previousElementSibling;

            if (input) {
                const tipoAtual = input.getAttribute('type');
                const novoTipo = tipoAtual === 'password' ? 'text' : 'password';
                input.setAttribute('type', novoTipo);

                // Troca ícone
                btn.classList.toggle('bi-eye-slash');
                btn.classList.toggle('bi-eye');
            }
        });
    });
});