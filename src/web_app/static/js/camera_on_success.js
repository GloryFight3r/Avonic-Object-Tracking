if (typeof onSuccess !== 'undefined') {
  onSuccess = Object.assign({}, onSuccess, {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "camera-position-get-form": onPositionGet,
    "presets-camera-position-set-form": onPositionSet,
    "presets-camera-zoom-set-form": onZoomSet,
    "camera-coords-get-form": onCameraCoordsGet
  });
}
else {
  onSuccess = {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "camera-position-get-form": onPositionGet,
    "presets-camera-position-set-form": onPositionSet,
    "presets-camera-zoom-set-form": onZoomSet,
    "camera-coords-get-form": onCameraCoordsGet
  }
}

function hideOff() {
  document.getElementById("camera-off-form").style.display = "none"
  document.getElementById("camera-on-form").style.display = "block"
}

function hideOn() {
  document.getElementById("camera-off-form").style.display = "block"
  document.getElementById("camera-on-form").style.display = "none"
}

async function onZoomGet(data) {
  document.getElementById("zoom-value-get").value = (await data)["zoom-value"]
}

async function onPositionGet(data) {
  const d = await data
  document.getElementById("position-alpha-value").value =
    d["position-alpha-value"].toFixed(5)
  document.getElementById("position-beta-value").value =
    d["position-beta-value"].toFixed(5)
}

async function onPositionSet(data) {
  const d = await data
  document.getElementById("camera-direction-alpha").value =
    d["position-alpha-value"].toFixed(5)
  document.getElementById("camera-direction-beta").value =
    d["position-beta-value"].toFixed(5)
}

async function onZoomSet(data) {
  document.getElementById("camera-zoom-value").value =
    (await data)["zoom-value"]
}

async function onCameraCoordsGet(data) {
    const d = (await data)["camera-coords"]
    document.getElementById("camera-coords-x").value = d[0].toFixed(5)
    document.getElementById("camera-coords-y").value = d[1].toFixed(5)
    document.getElementById("camera-coords-z").value = d[2].toFixed(5)
}

if (document.getElementById("presets") !== null) {
  selectCaliTab()
}
if (document.getElementById("calibration-button") !== null) {
  calibrationIsSet().then()
}

function selectMovement() {
  document.getElementById("camera-move-absolute").style.display = "none"
  document.getElementById("camera-move-relative").style.display = "none"
  document.getElementById("camera-move-vector").style.display = "none"
  document.getElementById(
    document.getElementById("movement-select").value
  ).style.display = "block"
}

if(document.getElementById("camera-off-form") !== null) {
  hideOn()
}
if(document.getElementById("camera-move-absolute") !== null) {
  selectMovement()
}
