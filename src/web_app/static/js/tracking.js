onSuccess = Object.assign({}, onSuccess, {
    "tracking-select": selectTracking,
})

function selectTracking() {
    const selected = document.getElementById("tracking-select").value
    const header = document.getElementById("tracking-title")
    switch(selected) {
        case "preset":
            header.innerText = "Following using presets 🔭"
            fetch("/preset/track", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break
        case "calib":
            header.innerText = "Continuous following  with adaptive zooming🔭"
            fetch("/calibration/track", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break
        case "calibnozoom":
            header.innerText = "Continuous following  without adaptive zooming🔭"
            fetch("/calibration/track/no/zoom", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break
        default:
            header.innerText = "Tracking 🔭"
            break
    }
}

const track_type_form = document.getElementById("tracking-select");
if (track_type_form !== null) {
    selectTracking();
}