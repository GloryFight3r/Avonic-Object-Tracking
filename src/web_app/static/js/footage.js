if (document.getElementById("footage")) {
    document.addEventListener("DOMContentLoaded", function(event) {
      socket.on('new-frame', message => {
        document.getElementById('live-footage').setAttribute(
          'src', `data:image/jpeg;base64,${message.base64}`
        );
      });
      // request a frame from server every X ms
      window.setInterval(() => {
        socket.emit('request-frame', {});
      }, 100);
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

    // send a request to navigate the camera to that position
    fetch("/navigate/camera", {
      method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({
        "x-pos": width_percentage, "y-pos": height_percentage
      })
    }).then(function(res) {
      if (res.status !== 200) {
          console.log("Error with navigation")
      } 
    })
});

