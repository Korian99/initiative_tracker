function deleteChar(e) {
  if (!confirm("Are you sure?")) {
    e.preventDefault();
  } else {
    myModal.hide();
  }
}
