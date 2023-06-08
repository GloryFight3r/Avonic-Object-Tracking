if (document.getElementById("footage")) {
  document.addEventListener("DOMContentLoaded", function(event) {
    socket.on('new-frame', message => {
      document.getElementById('live-footage').setAttribute(
        'src', `data:image/jpeg;base64,${message.base64}`
      );
    });
    window.setInterval(() => {
      socket.emit('request-frame', {});
    }, 50);
  });
}

const footage_img = document.getElementById("live-footage")

footage_img.addEventListener("click", function(event) {
  var x = event.pageX - this.offsetLeft;
  var y = event.pageY - this.offsetTop;

  var width = footage_img.width;
  var height = footage_img.height;
  //alert("X Coordinate: " + x + " Y Coordinate: " + y);
  p1 = Math.min(1, x / width);
  p2 = Math.min(1, y / height);

  fetch("/navigate/camera", {
    method:"POST",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify({
      "x-pos": p1, "y-pos": p2
    })
  }).then(function(res) {
    if (res.status !== 200) {
      //onError(button)
    } else {

    }
  })
});

