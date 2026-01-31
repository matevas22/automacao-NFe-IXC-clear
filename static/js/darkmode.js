document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("theme-toggle");
  const userTheme = localStorage.getItem("theme");
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (userTheme === "dark" || (!userTheme && systemTheme)) {
    document.documentElement.setAttribute("data-theme", "dark");
    updateIcon(true);
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    updateIcon(false);
  }

  toggleButton.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateIcon(newTheme === "dark");
  });

  function updateIcon(isDark) {
    toggleButton.innerHTML = isDark ? "☀️" : "🌙";
    toggleButton.setAttribute(
      "aria-label",
      isDark ? "Ativar modo claro" : "Ativar modo escuro",
    );
  }
});
