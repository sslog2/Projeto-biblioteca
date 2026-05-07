// Função para trocar de página
function showPage(pageId) {
  // Esconde todas as páginas
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.remove("active");
  });

  // Remove classe ativa de todos os itens do menu
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.remove("active");
  });

  // Mostra a página selecionada
  document.getElementById(pageId).classList.add("active");
  event.currentTarget.classList.add("active");
}

function calcularMulta(dias, valorPorDia = 2.5) {
  return (dias * valorPorDia).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

// Máscara para Telefone (00) 00000-0000
function maskPhone(value) {
  if (!value) return "";
  value = value.replace(/\D/g, "");
  value = value.replace(/(\d{2})(\d)/, "($1) $2");
  value = value.replace(/(\d{5})(\d)/, "$1-$2");
  return value.substring(0, 15);
}

document.addEventListener("DOMContentLoaded", () => {
  const phoneInput = document.querySelector('input[name="telefone"]');
  if (phoneInput) {
    phoneInput.addEventListener("input", (e) => {
      e.target.value = maskPhone(e.target.value);
    });
  }
});
