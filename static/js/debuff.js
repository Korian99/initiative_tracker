
document.body.addEventListener("htmx:configRequest", (event) => {
  var token = document
  .querySelector("meta[name='csrf-token']")
  .getAttribute("content");
  event.detail.headers["X-CSRFToken"] = token;
});

document
.getElementById("debuffCharacterModal")
.addEventListener("shown.bs.modal", function () {
  const input = document.querySelector("#debuff");
  if (input) {
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length); // Move cursor to end
  }
});

function setDebuffAction(event, actionType) {
  event.preventDefault(); // Prevent the default form submission
  const form = document.getElementById("debuffCharacterForm");
  const actionInput = form.querySelector('input[name="action"]');
  const debuffInput = form.querySelector('input[name="debuff"]');

  if (actionType === "remove") {
    actionInput.value = "delete";
    debuffInput.value = "";
  } else if (actionType === "add_edit") {
    const userInput = debuffInput.value.trim();
    actionInput.value = "add_edit";
    debuffInput.value = userInput || "Debuffed";
  }
  htmx.trigger(form, "submit");
  myModal.hide();
}