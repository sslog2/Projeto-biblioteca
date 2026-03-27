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
