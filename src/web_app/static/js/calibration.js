const totalCalibrations = 3
let calibratingSpeakerCount = 1
let isCalibrating = false

function addCalibrationSpeaker() {
    calibratingSpeakerCount++
    isCalibrating = false
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML = "Click below to calibrate point " + calibratingSpeakerCount
    const body = {method: "get"}
    const button = document.getElementById("calibration-button")
    fetch("/calibration/add_directions_to_speaker", body).then(function (res) {
        if (res.status !== 200) {
            onError(button)
        } else {
            button.disabled = false
            if (calibratingSpeakerCount > totalCalibrations) {
                calibratingSpeakerCount = 1
                pointCameraCalibration(button)
            } else {
                button.innerHTML = "Next point"
                button.onclick = () => startCalibration(button)
            }
        }
    })
}

function pointCameraCalibration(button) {
    const instructionText = document.getElementById("calibration-instruction");
    instructionText.innerHTML =
        "Please point the camera directly to the microphone.";
    button.innerHTML = "Done.";
    button.disabled = false;
    button.onclick = () => {
        button.disabled = true;
        const body = { method: "get" };
        fetch("/calibration/add_direction_to_mic", body).then(async function (res) {
            button.disabled = false;
            if (res.status !== 200) {
                onError(button);
            } else {
                button.disabled = false;
                button.innerHTML = "Reset calibration";
                instructionText.innerHTML =
                    "Don't forget to set the height too. Press below to reset the calibration.";
                button.onclick = () => resetCalibration(button);
            }
        });
    };
}

async function calibrationIsSet() {
    const body = { method: "get" };
    fetch("/calibration/is_set", body)
        .then((data) => data.json())
        .then((json) => {
            if (json["is_set"]) {
                const button = document.getElementById("calibration-button");
                const instructionText = document.getElementById(
                    "calibration-instruction"
                );
                instructionText.innerHTML =
                    "Press the button below to reset the calibration.";
                button.innerHTML = "Reset calibration";
                button.onclick = () => resetCalibration(button);
            }
        });
}

async function startCalibration(button) {
    const post_body = { method: "post", data: {} };
    fetch("/info-thread/start", post_body);
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML =
        "Please stand somewhere in the room, point the camera at your face and speak up."
    button.innerHTML = "Listening..."
    button.disabled = true
    isCalibrating = true
}

function resetCalibration(button) {
    const body = { method: "get" };
    fetch("/calibration/reset", body).then(async function (res) {
        button.disabled = true;
        if (res.status !== 200) {
            onError(button);
        } else {
            const instructionText = document.getElementById(
                "calibration-instruction"
            );
            instructionText.innerHTML = "To start calibration, please click below.";
            button.disabled = false;
            button.innerHTML = "Start calibration";
            button.onclick = () => startCalibration(button);
        }
    });
}

function selectCaliTab() {
    document.getElementById("presets").style.display = "none"
    document.getElementById("cal").style.display = "none"
    const selected = document.getElementById("presets-cali-select").value
    document.getElementById(selected).style.display = "block"
    const header = document.getElementById("presets-cali-title")
    switch(selected) {
        case "presets":
            header.innerText = "Presets 🔖"
            break
        case "cal":
            header.innerText = "Calibration 🧰"
            break
        default:
            header.innerText = "Presets 🔖"

    }
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
