onSuccess = Object.assign({}, onSuccess, {
    "tracking-select": selectTracking,
})

async function selectTracking() {
    const selected = document.getElementById("tracking-select").value
    const header = document.getElementById("tracking-title")
    let url
    switch(selected) {
        case "preset":
            header.innerText = "Following using presets 🔭"
            url = "/track/preset"
            break
        case "calib":
            header.innerText = "Continuous following  with adaptive zooming🔭"
            url = "/track/calibration"
            break
        case "hybrid":
            header.innerText = "Hybrid tracking  🔭"
            url = "/track/hybrid"
            break
        case "object":
            header.innerText = "Continuous object tracking  🔭"
            url = "/track/object"
            break;
        case "calibnozoom":
            header.innerText = "Continuous following  without adaptive zooming🔭"
            url = "/track/calibration-no-zoom"
            break
        default:
            header.innerText = "Tracking 🔭"
            break
    }
     const response = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    })
    if (response.status !== 200) {
        alert((await response.json())["message"])
    }
}

const track_type_form = document.getElementById("tracking-select");
if (track_type_form !== null) {
    selectTracking();
}
