function handleFileSelect(input) {
  const file = input.files[0];
  const display = document.getElementById("file-name-display");
  const previewContainer = document.getElementById("pdf-preview");
  const optionsPanel = document.getElementById("page-options-panel");
  const submitBtn = document.getElementById("btn-convert");

  if (file) {
    display.textContent = "Arquivo selecionado: " + file.name;
    document.querySelector(".upload-area h3").textContent = "Arquivo Pronto!";

    optionsPanel.style.display = "block";
    submitBtn.style.display = "inline-block";

    const fileURL = URL.createObjectURL(file);

    previewContainer.innerHTML = "";
    const iframe = document.createElement("iframe");
    iframe.src = fileURL;
    previewContainer.appendChild(iframe);
    previewContainer.style.display = "block";
  }
}

function togglePageInput() {
  const mode = document.querySelector(
    'input[name="conversion_mode"]:checked',
  ).value;
  const inputWrapper = document.getElementById("specific-page-input");

  if (mode === "single") {
    inputWrapper.style.display = "block";
  } else {
    inputWrapper.style.display = "none";
  }
}

const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("pdf_file");

["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

["dragenter", "dragover"].forEach((eventName) => {
  dropArea.addEventListener(eventName, highlight, false);
});

["dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
  dropArea.style.borderColor = "var(--accent-color)";
  dropArea.style.backgroundColor = "#eff6ff";
}

function unhighlight(e) {
  dropArea.style.borderColor = "var(--border-color)";
  dropArea.style.backgroundColor = "var(--input-bg)";
}

dropArea.addEventListener("drop", handleDrop, false);

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  fileInput.files = files;
  handleFileSelect(fileInput);
}
