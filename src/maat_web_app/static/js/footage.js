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

const footage_img = document.getElementById("live-footage")

/** Navigates the camera so that the location where we clicked on is centered
 * 
 * @class
 * @classdesc 
 */
footage_img.addEventListener("click", function(event) {
    // location of click
    var x = event.pageX - this.offsetLeft;
    var y = event.pageY - this.offsetTop;

    // width and height of the footage container
    var width = footage_img.width;
    var height = footage_img.height;

    // get position of the clicked location as a percentage of the total container
    width_percentage = Math.min(1, x / width);
    height_percentage = Math.min(1, y / height);

    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/camera/navigate");

    var x_input = document.createElement("input");
    x_input.setAttribute("name", "x-pos")
    x_input.setAttribute("value", width_percentage);

    var y_input = document.createElement("input");
    y_input.setAttribute("name", "y-pos")
    y_input.setAttribute("value", height_percentage);

    form.append(x_input)
    form.append(y_input)

    // send a request to navigate the camera to that position
    fetch(form.action, body = { method: form.method, body: new FormData(form) })
    .then(function(res) {
      if (res.status !== 200) {
          console.log("Error with navigation")
      } 
    })
});
