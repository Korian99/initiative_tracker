function changeReactions(reactions, character_id) {
  const lobby = document.getElementById('lobby-container');
  const characterListUrl = lobby.dataset.characterListUrl;

  if (reactions > 0 && confirm("Use a reaction?")) {
    htmx.ajax(
      "GET",
     characterListUrl,
      {
        target: "#character-list",
        values: { character_id: character_id }, // ✅ correct key is "vals"
        swap: "innerHTML",
      }
    );
  }
}
