if (document.getElementById("footage")) {
  document.addEventListener("DOMContentLoaded", function(event) {
    socket.on('new-frame', message => {
      console.log(message.base64)
      document.getElementById('live-footage').setAttribute(
        'src', `data:image/jpeg;base64,${message.base64}`
      );
    });
    window.setInterval(() => {
      socket.emit('request-frame', {});
    }, 1000);
  });
}
