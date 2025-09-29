let socket;

document.addEventListener("DOMContentLoaded", () => {
  const lobbyEl = document.getElementById("lobby-container");
  const lobbyId = lobbyEl.dataset.lobbyId;
  const lobbyCode = lobbyEl.dataset.lobbyCode;

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        window.location.reload();
      }
    }
  });

  function connect() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(
      `${protocol}://${window.location.host}/ws/lobby/${lobbyId}/`
    );

    socket.onmessage = function (e) {
      const data = JSON.parse(e.data);
      if (data.action === "list") {
        htmx.trigger("#character-list", "refresh");
      } else if (data.action === "lobby") {
        document
          .querySelector(`#join-lobby-${lobbyCode}-form`)
          .submit();
      }
    };

    socket.onclose = function () {
      console.log("Socket closed. Reconnecting in 2s...");
      setTimeout(connect, 2000); // auto-reconnect
    };
  }

  connect();
});
