function initHome() {
  const reportForm = document.getElementById("reportForm");
  const textarea = document.getElementById("ids_notas");
  const counter = document.getElementById("lineCount");

  if (!reportForm) return;

  function updateCount() {
    const text = textarea.value;
    const lines = text
      .split(/\r\n|\r|\n/)
      .filter((line) => line.trim() !== "").length;
    counter.textContent = `${lines} ${lines === 1 ? "nota" : "notas"}`;
  }

  if (textarea && counter) {
    textarea.removeEventListener("input", updateCount);
    textarea.addEventListener("input", updateCount);
    updateCount();
  }

  const newForm = reportForm.cloneNode(true);
  reportForm.parentNode.replaceChild(newForm, reportForm);

  newForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const modal = document.getElementById("loadingModal");
    const form = this;
    const successCard = document.getElementById("successCard");
    const formData = new FormData(form);
    const submitBtn = form.querySelector("button");

    if (modal) modal.style.display = "flex";
    if (submitBtn) submitBtn.disabled = true;

    try {
      const response = await fetch("/", {
        method: "POST",
        body: formData,
      });

      const contentType = response.headers.get("content-type");

      if (
        contentType &&
        contentType.includes(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
      ) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        let filename = "relatorio.xlsx";
        const disposition = response.headers.get("content-disposition");

        if (disposition && disposition.indexOf("attachment") !== -1) {
          const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(
            disposition,
          );
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, "");
          }
        }

        if (filename === "relatorio.xlsx") {
          const selectedProvider = formData.get("provider");
          const providerName = selectedProvider
            ? selectedProvider.charAt(0).toUpperCase() +
              selectedProvider.slice(1)
            : "Relatorio";
          filename = `relatorio_notas_${providerName}.xlsx`;
        }

        const fileNameDisplay = document.getElementById("fileNameDisplay");
        if (fileNameDisplay) fileNameDisplay.textContent = filename;

        const downloadBtn = document.getElementById("downloadBtn");
        if (downloadBtn) {
          downloadBtn.onclick = function () {
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          };
        }

        const resetBtn = document.getElementById("resetBtn");
        if (resetBtn) {
          resetBtn.onclick = function () {
            window.URL.revokeObjectURL(url);
            successCard.style.display = "none";
            form.style.display = "block";
            if (submitBtn) submitBtn.disabled = false;
          };
        }

        if (modal) modal.style.display = "none";
        form.style.display = "none";
        if (successCard) successCard.style.display = "block";
      } else {

        const text = await response.text();
        alert("Erro no servidor ou resposta inesperada.");
        console.log(text);
        if (modal) modal.style.display = "none";
        if (submitBtn) submitBtn.disabled = false;
      }
    } catch (error) {
      console.error("Erro:", error);
      alert("Ocorreu um erro ao conectar com o servidor.");
      if (modal) modal.style.display = "none";
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}


document.addEventListener("DOMContentLoaded", () => {
  initHome();
  initSpaNavigation();
});

function initSpaNavigation() {
  document.body.addEventListener("click", (e) => {
    const link = e.target.closest("a");

    if (
      link &&
      link.href.startsWith(window.location.origin) && 
      !link.hasAttribute("download") && 
      link.target !== "_blank" && 
      !link.getAttribute("href").startsWith("#") 
    ) {
      e.preventDefault();
      navigateTo(link.href);
    }
  });

  window.addEventListener("popstate", () => {
    loadPage(window.location.href);
  });
}

async function navigateTo(url) {
  history.pushState(null, null, url);
  await loadPage(url);
}

async function loadPage(url) {
  const container = document.querySelector(".main-content");
  if (!container) return; // Segurança

  container.style.opacity = "0.5";
  container.style.pointerEvents = "none";

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Erro ao carregar página");

    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    document.title = doc.title;

    updateStyles(doc);

    const newContent = doc.querySelector(".main-content").innerHTML;
    container.innerHTML = newContent;

    executeScripts(container);

    initHome();

    updateActiveMenu(url);
  } catch (error) {
    console.error("Falha na navegação SPA:", error);

    window.location.href = url;
  } finally {
    container.style.opacity = "1";
    container.style.pointerEvents = "auto";
  }
}

function updateStyles(newDoc) {
  const currentHead = document.head;
  const newHead = newDoc.head;

  const currentLinks = Array.from(
    currentHead.querySelectorAll('link[rel="stylesheet"]')
  );
  const newLinks = Array.from(
    newHead.querySelectorAll('link[rel="stylesheet"]')
  );

  const newHrefs = newLinks.map((link) => link.getAttribute("href"));
  const currentHrefs = currentLinks.map((link) => link.getAttribute("href"));

  currentLinks.forEach((link) => {
    if (!newHrefs.includes(link.getAttribute("href"))) {
      link.remove();
    }
  });

  newLinks.forEach((link) => {
    if (!currentHrefs.includes(link.getAttribute("href"))) {
      const newLink = link.cloneNode(true);
      currentHead.appendChild(newLink);
    }
  });
}

function executeScripts(container) {
  const scripts = container.querySelectorAll("script");
  scripts.forEach((oldScript) => {
    const newScript = document.createElement("script");
    Array.from(oldScript.attributes).forEach((attr) =>
      newScript.setAttribute(attr.name, attr.value),
    );
    newScript.appendChild(document.createTextNode(oldScript.innerHTML));
    oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}

function updateActiveMenu(url) {
  const links = document.querySelectorAll(".nav-links a");
  links.forEach((link) => {
    if (link.href === url) {
      link.classList.add("active"); 
    } else {
      link.classList.remove("active");
    }
  });
}
