document.addEventListener('DOMContentLoaded', () => {
    const botaoMenu = document.getElementById('menu-mobile-btn');
    const menuNavegacao = document.querySelector('.menu-nav');
    const linksNavegacao = document.querySelectorAll('.link-nav');

    if (botaoMenu && menuNavegacao) {
        botaoMenu.addEventListener('click', () => {
            menuNavegacao.classList.toggle('ativo');
        });

        linksNavegacao.forEach(link => {
            link.addEventListener('click', () => {
                menuNavegacao.classList.remove('ativo');
            });
        });
    }

    const opcoesObservador = {
        threshold: 0.1
    };

    const observador = new IntersectionObserver((entradas) => {
        entradas.forEach(entrada => {
            if (entrada.isIntersecting) {
                entrada.target.classList.add('visivel');
                observador.unobserve(entrada.target);
            }
        });
    }, opcoesObservador);

    const cartoesAnimados = document.querySelectorAll('.cartao-passo, .cartao-item');
    
    cartoesAnimados.forEach(cartao => {
        cartao.style.opacity = '0';
        cartao.style.transform = 'translateY(20px)';
        cartao.style.transition = 'all 0.6s ease-out';
        observador.observe(cartao);
    });

    document.addEventListener('scroll', () => {
        cartoesAnimados.forEach(cartao => {
            const rect = cartao.getBoundingClientRect();
            if(rect.top < window.innerHeight - 100) {
                cartao.style.opacity = '1';
                cartao.style.transform = 'translateY(0)';
            }
        });
    });
});