document.body.addEventListener("htmx:beforeRequest", function(evt) {
  // Check if it's a specific request
  if (evt.target && evt.target.matches(".show-spinner")) {
    document.getElementById("htmx-overlay").classList.remove("d-none");
  }
});

document.body.addEventListener("htmx:afterRequest", function(evt) {
  document.getElementById("htmx-overlay").classList.add("d-none");
});