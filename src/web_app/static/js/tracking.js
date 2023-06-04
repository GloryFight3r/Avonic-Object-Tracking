if (typeof onSuccess !== 'undefined') {
    onSuccess = Object.assign({}, onSuccess, {
      "tracking-select": selectTracking,
    });
  }
  else {
    onSuccess = {
      "tracking-select": selectTracking,
    }
  } 

function selectTracking() {
    const selected = document.getElementById("tracking-select").value
    console.log(selected)
    const header = document.getElementById("tracking-title")
    switch(selected) {
        case "untrack":
            header.innerText = "Tracking 🔭"
            fetch("/untrack", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break 
        case "preset":
            header.innerText = "Tracking using presets 🔭"
            fetch("/preset/track", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break
        case "calib":
            header.innerText = "Continuous tracking  🔭"
            fetch("/calibration/track", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break
        default:
            header.innerText = "Tracking 🔭"

    }
}