document.addEventListener('DOMContentLoaded', function () {
    const formBusca = document.getElementById('form-busca-amigos');
    const inputBusca = document.getElementById('input-busca-amigos');
    const resultadosContainer = document.getElementById('container-resultados-busca');
    
    const urlApi = '/api/buscar-usuarios/'; 

    formBusca.addEventListener('submit', function (event) {
        event.preventDefault(); 
        
        const query = inputBusca.value;

        if (query.length < 2) {
            resultadosContainer.innerHTML = '<p class="sem-resultados">Digite pelo menos 2 caracteres.</p>';
            return;
        }

        resultadosContainer.innerHTML = '<p class="sem-resultados">Buscando...</p>';

        fetch(`${urlApi}?q=${query}`)
            .then(response => response.json())
            .then(data => {
                if (data.resultados.length === 0) {
                    resultadosContainer.innerHTML = '<p class="sem-resultados">Nenhum usuário encontrado.</p>';
                    return;
                }

                let htmlResultados = '';
                data.resultados.forEach(usuario => {
                    htmlResultados += `
                        <div class="pedido-card">
                            <span class="pedido-nome">${usuario.nome_usuario} (${usuario.nome})</span>
                            <div class="pedido-acoes">
                                <form action="/amigos/enviar-pedido/${usuario.id}/" method="POST" class="form-pedido">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                                    <button type="submit" class="botao-link botao-sucesso">Adicionar</button>
                                </form>
                            </div>
                        </div>
                    `;
                });
                
                resultadosContainer.innerHTML = htmlResultados;
            })
            .catch(error => {
                console.error('Erro na busca:', error);
                resultadosContainer.innerHTML = '<p class="sem-resultados">Ocorreu um erro ao buscar.</p>';
            });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});