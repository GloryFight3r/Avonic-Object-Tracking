if (document.getElementById("footage")) {
  document.addEventListener("DOMContentLoaded", function(event) {
    socket.on('new-frame', message => {
      document.getElementById('live-footage').setAttribute(
        'src', `data:image/jpeg;base64,${message.base64}`
      );
    });
    window.setInterval(() => {
      if (document.getElementById("footage-switch").checked) {
        socket.emit('request-frame', {})
      }
    }, 100)
  });
}
