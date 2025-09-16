const bodyEl = document.body; // use <body> now
const btn = document.getElementById("themeToggle");

btn.addEventListener("click", () => {
  const currentTheme = bodyEl.getAttribute("data-bs-theme") || "light";
  const newTheme = currentTheme === "dark" ? "light" : "dark";

  bodyEl.setAttribute("data-bs-theme", newTheme);
  localStorage.setItem("theme", newTheme);

  btn.innerHTML =
    newTheme === "dark"
      ? '<i class="bi bi-sun"></i> Toggle Light Mode'
      : '<i class="bi bi-moon"></i> Toggle Dark Mode';
});

const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
  bodyEl.setAttribute("data-bs-theme", savedTheme);
  btn.innerHTML =
    savedTheme === "dark"
      ? '<i class="bi bi-sun"></i> Toggle Light Mode'
      : '<i class="bi bi-moon"></i> Toggle Dark Mode';
}
