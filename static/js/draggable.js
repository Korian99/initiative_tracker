(function () {
  const lobby = document.getElementById("character-list-container");

  const playerId = lobby.dataset.playerId;
  const csrfToken = lobby.dataset.csrfToken;
  const characterListUrl = lobby.dataset.characterListUrl;
  const moveCharacterUrl = lobby.dataset.moveCharacterUrl;

  window.sortableManager = {
    init: function () {
      const container = document.getElementById("characters");
      if (container) {
        if (window.sortableManager.instance) {
          window.sortableManager.instance.destroy();
        }
        let dragInProgress = false;
        document.body.addEventListener("htmx:beforeSwap", function (evt) {
          if (dragInProgress && evt.target.id === "character-list") {
            evt.preventDefault(); // block update if dragging
          }
        });
        window.sortableManager.instance = new Sortable(container, {
          animation: 150,
          ghostClass: "bg-secondary",
          handle: ".drag-handle",
          filter: ".btn, .current_turn",
          preventOnFilter: false,
          forceFallback: true, // Important for mobile
          fallbackTolerance: 3, // Pixel tolerance for drag start
          onStart: function () {
            dragInProgress = true;
            document.body.classList.add("dragging-active");
          },
          onEnd: function (evt) {
            dragInProgress = false;
            document.body.classList.remove("dragging-active");
            if (!confirm("Are you sure?")) {
              htmx.ajax("GET", characterListUrl, {
                values: {
                  player_id: playerId,
                  csrfmiddlewaretoken: csrfToken,
                },
                swap: "innerHTML",
                target: "#character-list",
              });
            } else {
              const characterIds = Array.from(container.children).map(
                (li) => li.dataset.id
              );
              htmx.ajax("POST", moveCharacterUrl, {
                values: {
                  player_lobby_id: playerId,
                  order: characterIds,
                  csrfmiddlewaretoken: csrfToken,
                },
                swap: "innerHTML",
                target: "#character-list",
              });
            }
          },
        });
      }
    },
  };

  function showToast() {
    const reminderChar = document.querySelector("li.current_turn");
    if (reminderChar) {
      const reminder = reminderChar.querySelector('input[name="reminder"]'); // 3rd span is reminder
      if (reminder && reminder.value.trim()) {
        const toast = document.createElement("div");
        toast.innerText = reminder.value.trim();
        toast.style.position = "fixed";
        toast.style.width = "50%";
        toast.style.textAlign = "center";
        toast.style.top = "100px";
        toast.style.left = "50%";
        toast.style.transform = "translateX(-50%)";
        toast.style.backgroundColor = "#343a40";
        toast.style.color = "#fff";
        toast.style.padding = "10px 20px";
        toast.style.borderRadius = "8px";
        toast.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
        toast.style.zIndex = 1054;
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.5s";

        document.body.appendChild(toast);

        setTimeout(() => (toast.style.opacity = "1"), 100);
        setTimeout(() => {
          toast.style.opacity = "0";
          setTimeout(() => toast.remove(), 500);
        }, 5000);
      }
    }
  }

  // Initial initialization
  document.addEventListener("DOMContentLoaded", function () {
    window.sortableManager.init();
    showToast();
  });

  // Reinitialize after HTMX updates
  document.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target.id === "character-list") {
      window.sortableManager.init();
      showToast();
    }
  });
})();
