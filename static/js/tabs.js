function activateTab(tabId) {
  var tabElement = document.getElementById(tabId);
  var tab = new bootstrap.Tab(tabElement);
  tab.show();
}