onSuccess = Object.assign({}, onSuccess, {
    "tracking-select": selectTracking,
})

function selectTracking() {
    const selected = document.getElementById("tracking-select").value
    const header = document.getElementById("tracking-title")
    switch(selected) {
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
        case "object":
            header.innerText = "Continuous object tracking  🔭"
            fetch("/object/track", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
            break;
        default:
            header.innerText = "Tracking 🔭"
            break
    }
}

const track_type_form = document.getElementById("tracking-select");
if (track_type_form !== null) {
    selectTracking();
}
