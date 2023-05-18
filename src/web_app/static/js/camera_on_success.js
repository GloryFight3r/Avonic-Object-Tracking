function hideOff() {
    document.getElementById("camera-off-form").style.display = "none"
    document.getElementById("camera-on-form").style.display = "block"
}

function hideOn() {
    document.getElementById("camera-off-form").style.display = "block"
    document.getElementById("camera-on-form").style.display = "none"
}

async function onZoomGet(data) {
    document.getElementById("zoom-value-get").value = await data["zoom-value"]
}

async function onPositionGet(data) {
    const d = await data
    document.getElementById("position-alpha-value").value =
        d["position-alpha-value"]
    document.getElementById("position-beta-value").value =
        d["position-beta-value"]
}

async function onPositionSet(data) {
    const d = await data
    document.getElementById("camera-direction-alpha").value =
        d["position-alpha-value"]

    document.getElementById("camera-direction-beta").value =
        d["position-beta-value"]
}

function selectMovement() {
    document.getElementById("camera-move-absolute").style.display = "none"
    document.getElementById("camera-move-relative").style.display = "none"
    document.getElementById("camera-move-vector").style.display = "none"
    document.getElementById(
        document.getElementById("movement-select").value
    ).style.display = "block"
}
