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

function confirmClick(e) {
  if (!confirm("Are you sure?")) {
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
