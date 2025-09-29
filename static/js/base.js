var myModal=null;

function longPress(el, callback, message) {
  let pressTimer;

  el.addEventListener("touchstart", () => {
    pressTimer = setTimeout(() => {
      if (confirm(message)) {
        callback(el);
      }
    }, 1000);
  });

  el.addEventListener("touchend", () => clearTimeout(pressTimer));
  el.addEventListener("touchmove", () => clearTimeout(pressTimer));
}

function confirmClick(e, msg="Are you sure?") {
  if (!confirm(msg)) {
    e.preventDefault();
  }
}

function initCreatureSelect(ctx = document, id) {
  const theme = document.body.getAttribute("data-bs-theme");
  const $el = $(ctx).find(id);
  let dropdownParent = null;
  if (id === "#stat_block_edit") {
    dropdownParent = $("#editCharacterModal");
  }
  if ($el.length && !$el.data("select2")) {
    $el.select2({
      width: "100%",
      placeholder: "Search for a Stat Block",
      allowClear: true,
      dropdownParent: dropdownParent,
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initCreatureSelect();
  document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.target && e.target.id === "select_creature") {
      initCreatureSelect(e.target, "#stat_block_add");
    } else if (e.target && e.target.id === "edit_creature") {
      initCreatureSelect(e.target, "#stat_block_edit");
    }
  });

  document.body.addEventListener("htmx:configRequest", (event) => {
    var token = document
      .querySelector("meta[name='csrf-token']")
      .getAttribute("content");
    event.detail.headers["X-CSRFToken"] = token;
  });
  document.addEventListener("htmx:afterSwap", (evt) => {
    if (
      evt.detail.target &&
      evt.detail.target.classList.contains("modal-container")
    ) {
      const triggeringEl = evt.detail.requestConfig.elt;

      if (triggeringEl && triggeringEl.classList.contains("open-modal")) {
        const modalId = triggeringEl.dataset.modalId;
        if (modalId) {
          const modalEl = document.getElementById(modalId);
          if (modalEl) {
            myModal = new bootstrap.Modal(modalEl);
            myModal.show();
          }
        }
      }
    }
  });
});
