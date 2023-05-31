const totalCalibrations = 3
let calibratingSpeakerCount = 0
let isCalibrating = false

function addCalibrationSpeaker() {
    isCalibrating = false
    const instructionText = document.getElementById("calibration-instruction")

    // after the last point has been calibrated, change the instruction text
    if (calibratingSpeakerCount === totalCalibrations - 1) {
        instructionText.innerHTML =
            "Please point the camera directly to the microphone.";
    } else {
        instructionText.innerHTML = "Click below to calibrate point " + (calibratingSpeakerCount+2) +
            " or point the camera towards the microphone and finish the calibration."
    }

    const body = {method: "get"}
    const button = document.getElementsByClassName("calibration-button")[calibratingSpeakerCount]
    fetch("/calibration/add_directions_to_speaker", body).then(function (res) {
        if (res.status !== 200) {
            onError(button)
        } else {
            calibratingSpeakerCount++
            button.innerHTML = "Set"
            if (calibratingSpeakerCount >= totalCalibrations) {
                calibratingSpeakerCount = 1
            } else {
                // after at least one calibration point, the calibration process can be finished
                if (calibratingSpeakerCount == 1) {
                    document.getElementById("camera-direction-button").disabled = false
                }
                const nextButton = button.parentNode.children[calibratingSpeakerCount]
                nextButton.disabled = false
            }
        }
    })
}

function pointCameraCalibration(button) {
    const instructionText = document.getElementById("calibration-instruction");
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
            document.getElementsByClassName("calibration-button")[calibratingSpeakerCount].disabled = true
        }
    });
}

async function calibrationIsSet() {
    const body = { method: "get" };
    fetch("/calibration/is_set", body)
        .then((data) => data.json())
        .then((json) => {
            if (json["is_set"]) {
                const buttons = document.getElementsByClassName("calibration-button");
                buttons[0].disabled = true
                for (button in buttons) {
                    button.innerHTML = "Set"
                }
                const instructionText = document.getElementById(
                    "calibration-instruction"
                );
                instructionText.innerHTML =
                    "Press the button below to reset the calibration.";
                const reset_button = document.getElementById("camera-direction-button")
                reset_button.innerHTML = "Reset calibration";
                reset_button.disabled = false;
                reset_button.onclick = () => resetCalibration(reset_button);
            }
        });
}

async function startCalibration(button) {
    const post_body = { method: "post", data: {} };
    fetch("thread/start/false", post_body);
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML =
        "Please stand somewhere in the room, point the camera at your face and speak up."
    button.innerHTML = "Listening..."
    button.disabled = true
    isCalibrating = true
}


function resetCalibration(reset_button) {
    const body = { method: "get" };
    fetch("/calibration/reset", body).then(async function (res) {
        if (res.status !== 200) {
            onError(button);
        } else {
            reset_button.disabled = true;
            reset_button.innerHTML = "Submit current camera direction.";
            reset_button.onclick = () => pointCameraCalibration(reset_button);
            const instructionText = document.getElementById(
                "calibration-instruction"
            );
            instructionText.innerHTML =
                "Set the height, then click below to calibrate point 1";
            const buttons = document.getElementsByClassName("calibration-button")
            buttons[0].disabled = false
            for (const buttonId in buttons) {
                buttons[buttonId].innerHTML = "Start " + (parseInt(buttonId)+1);
            }
            calibratingSpeakerCount = 0
        }
    });
}

async function onCameraCoordsGet(data) {
    const d = (await data)["camera-coords"]
    document.getElementById("camera-coords-x").value = d[0].toFixed(5)
    document.getElementById("camera-coords-y").value = d[1].toFixed(5)
    document.getElementById("camera-coords-z").value = d[2].toFixed(5)
}
