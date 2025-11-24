document.addEventListener("DOMContentLoaded", function () {
  console.log("homejs.js Carregado! (v105 - Menu Centralizado e Fixo)");
  
  const botaoMenuMobile = document.getElementById("botao-menu-mobile");
  const menuMobileOverlay = document.getElementById("menu-mobile-overlay");
  
  const dropdownTrigger = document.getElementById("profile-dropdown-trigger");
  const profileDropdown = document.getElementById("profile-dropdown");
  
  const dropdownTriggerMobile = document.getElementById("profile-dropdown-trigger-mobile");
  const profileDropdownMobile = document.getElementById("profile-dropdown-mobile");

  if (botaoMenuMobile && menuMobileOverlay) {
    botaoMenuMobile.addEventListener("click", () => {
      botaoMenuMobile.classList.toggle("aberto");
      menuMobileOverlay.classList.toggle("aberto");
      document.body.classList.toggle("menu-aberto-sem-scroll");
      
      if (!menuMobileOverlay.classList.contains("aberto") && profileDropdownMobile) {
          profileDropdownMobile.classList.remove("aberto");
      }
    });
  }

  if (dropdownTrigger && profileDropdown) {
    
    function posicionarDropdown() {
        const rect = dropdownTrigger.getBoundingClientRect(); 
        const dropdownWidth = 220; 
        
        let leftPos = rect.left + (rect.width / 2) - (dropdownWidth / 2);
        
        let topPos = rect.bottom + 10;

        profileDropdown.style.top = `${topPos}px`;
        profileDropdown.style.left = `${leftPos}px`;
    }

    dropdownTrigger.addEventListener("click", (e) => {
      e.stopPropagation(); 
      e.preventDefault();
      
      if (!profileDropdown.classList.contains("aberto")) {
          posicionarDropdown();
      }
      
      profileDropdown.classList.toggle("aberto");
    });
    
    window.addEventListener('resize', () => {
        if (profileDropdown.classList.contains("aberto")) {
            posicionarDropdown();
        }
    });
    
    profileDropdown.addEventListener("click", (e) => {
        e.stopPropagation();
    });
  }

  if (dropdownTriggerMobile && profileDropdownMobile) {
    dropdownTriggerMobile.addEventListener("click", (e) => {
      e.stopPropagation();
      profileDropdownMobile.classList.toggle("aberto");
    });
  }

  document.addEventListener("click", (e) => {
    if (profileDropdown && profileDropdown.classList.contains("aberto")) {
        if (dropdownTrigger && !dropdownTrigger.contains(e.target)) {
            profileDropdown.classList.remove("aberto");
        }
    }
  });

  const btnResgatar = document.getElementById("btn-resgatar-foco");
  const jsDataElement = document.getElementById("js-data");

  if (btnResgatar && jsDataElement) {
    const jsData = JSON.parse(jsDataElement.textContent);
    const resgatarFocoUrl = jsData.resgatarFocoUrl;
    const csrfToken = jsData.csrfToken;

    btnResgatar.addEventListener("click", function () {
      btnResgatar.disabled = true;
      btnResgatar.textContent = "Processando...";

      fetch(resgatarFocoUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken, 
        },
        body: JSON.stringify({}), 
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(err => { throw new Error(err.message || 'Erro de rede'); });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          const dadosFormatados = {
              nivel_usuario: data.nivel,
              xp_total_usuario: data.xp_atual,
              xp_proximo_nivel: data.xp_proximo_nivel
          };
          atualizarBarraDeXP(dadosFormatados);
          const diasFocoDisplay = document.getElementById("dias-foco-display");
          if (diasFocoDisplay) diasFocoDisplay.textContent = data.dias_foco;
          btnResgatar.textContent = "Foco resgatado!";
        } else {
          throw new Error(data.message || "Não foi possível resgatar.");
        }
      })
      .catch(error => {
        console.error("Erro ao resgatar foco:", error);
        if (error.message.includes("já resgatou")) {
              btnResgatar.textContent = "Foco resgatado!";
              btnResgatar.disabled = true;
        } else {
              btnResgatar.textContent = "Resgatar Foco (20xp)";
              btnResgatar.disabled = false;
        }
      });
    });
  } 

  function atualizarBarraDeXP(data) {
      const badgesNivel = document.querySelectorAll(".level-badge-display");
      if (badgesNivel.length > 0 && data.nivel_usuario !== undefined) {
          badgesNivel.forEach(badge => { badge.textContent = data.nivel_usuario; });
      }
      const progressoLevelTexto = document.getElementById("progresso-level-texto");
      const progressoXpAtual = document.getElementById("progresso-xp-atual");
      const progressoXpNecessario = document.getElementById("progresso-xp-necessario");
      const barraPreenchimento = document.getElementById("progresso-barra-preenchimento");

      if (data.xp_total_usuario !== undefined && data.xp_proximo_nivel !== undefined && data.nivel_usuario !== undefined) {
          if (progressoLevelTexto && progressoXpAtual && progressoXpNecessario && barraPreenchimento) {
              progressoLevelTexto.textContent = `Progresso Nível ${data.nivel_usuario}`;
              progressoXpAtual.textContent = `${data.xp_total_usuario} XP`;
              progressoXpNecessario.textContent = `${data.xp_proximo_nivel} XP`;
              let percentual = 0;
              if (data.xp_proximo_nivel > 0) {
                  percentual = (data.xp_total_usuario / data.xp_proximo_nivel) * 100;
              }
              percentual = Math.min(percentual, 100);
              barraPreenchimento.style.width = `${percentual}%`;
              barraPreenchimento.textContent = `${percentual.toFixed(0)}%`;
          }
      }
      const xpTotalDisplay = document.getElementById("xp-total-display");
      if (xpTotalDisplay && data.xp_total_usuario !== undefined) {
          xpTotalDisplay.textContent = data.xp_total_usuario;
      }
  }

    const freezerMessage = document.querySelector('.mensagem.popup-congelador');
    if (freezerMessage) {
        const messageText = freezerMessage.innerText;
        const messagesContainer = document.querySelector('.mensagens-container');
        if (messagesContainer) messagesContainer.style.display = 'none';
        const modal = document.getElementById('congelador-modal');
        const modalText = document.getElementById('congelador-text');
        if (modal && modalText) { 
            modalText.innerText = messageText;
            modal.style.display = 'flex'; 
            setTimeout(() => { modal.style.display = 'none'; }, 7000); 
        }
    }
});