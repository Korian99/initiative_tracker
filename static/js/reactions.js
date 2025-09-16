function changeReactions(reactions, character_id, role="P") {
  const lobby = document.getElementById('lobby-container');
  const characterListUrl = lobby.dataset.characterListUrl;
  if ((role=='DM' || reactions > 0) && confirm("Use a reaction?")) {
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
