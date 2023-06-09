if (document.getElementById("footage")) {
    document.addEventListener("DOMContentLoaded", function() {
        socket.on('new-frame', message => {
            document.getElementById('live-footage').setAttribute(
                'src', `data:image/jpeg;base64,${message.base64}`
            );
        });
        window.setInterval(() => {
            const img = document.getElementById("live-footage")
            if (document.getElementById("footage-switch").checked) {
                if (img.style.display === "none") {
                    img.style.display = "block"
                }
                socket.emit('request-frame', {})
            } else {
                img.style.display = "none"
            }
        }, 100)
    });
}