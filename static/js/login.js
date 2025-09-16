document.addEventListener("DOMContentLoaded", () => {
  const playerInput = document.getElementById("player");
  const form = document.getElementById("player_connect");
  const savedPlayer = localStorage.getItem("player");
  if (savedPlayer) {
    playerInput.value = savedPlayer;

    // Optional: auto-submit the form for auto-login
    // form.submit();
  }

  form.addEventListener("submit", () => {
    localStorage.setItem("player", playerInput.value);
  });
});
