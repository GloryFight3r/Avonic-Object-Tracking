document.addEventListener("DOMContentLoaded", function(event) {
    socket.on('new-frame', message => {
        document.getElementById('live-footage').setAttribute(
            'src', `data:image/jpeg;base64,${message.base64}`
        );
    });
    window.setInterval(() => {
        socket.emit('request-frame', {});
    }, 100);
});
