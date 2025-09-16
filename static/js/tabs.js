function activateTab(tabId) {
  var tabElement = document.getElementById(tabId);
  var tab = new bootstrap.Tab(tabElement);
  tab.show();
}

document.getElementById('switch-tab-btn').addEventListener('click', function() {
    // Find whichever tab nav is visible
    let activeTab = document.querySelector('.nav-link.active');

    if (!activeTab) return; // no tab active, bail

    let targetId = activeTab.getAttribute('id');

    // Logic for Characters/Add Characters
    if (targetId === 'characters-tab') {
        new bootstrap.Tab(document.getElementById('add-characters-tab')).show();
    } else if (targetId === 'add-characters-tab') {
        new bootstrap.Tab(document.getElementById('characters-tab')).show();
    }

    // Logic for Lobbies
    else if (targetId === 'my-lobbies-tab') {
        new bootstrap.Tab(document.getElementById('other-lobbies-tab')).show();
    } else if (targetId === 'other-lobbies-tab') {
        new bootstrap.Tab(document.getElementById('my-lobbies-tab')).show();
    }
});
