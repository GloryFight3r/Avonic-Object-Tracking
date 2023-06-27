const totalCalibrations = 3
let calibratingSpeakerCount = 0
let isCalibrating = false

function addCalibrationSpeaker() {
    if(calibratingSpeakerCount === totalCalibrations)
        return;

    isCalibrating = false
    const instructionText = document.getElementById("calibration-instruction")

    // after the last point has been calibrated, change the instruction text
    if (calibratingSpeakerCount === totalCalibrations - 1) {
        instructionText.innerHTML =
            "Please point the camera directly to the microphone.";
    } else {
        instructionText.innerHTML = "Click below to calibrate point " + (calibratingSpeakerCount + 2) +
            " or point the camera towards the microphone and finish the calibration."
    }

    const body = {method: "post"}
    const button = document.getElementsByClassName("calibration-button")[calibratingSpeakerCount]
    fetch("/calibration/add_directions_to_speaker", body).then(function (res) {
        if (res.status !== 200) {
            onError(button)
        } else {
            calibratingSpeakerCount++
            button.innerHTML = "Set"
            if (calibratingSpeakerCount > totalCalibrations) {
                calibratingSpeakerCount = totalCalibrations
            }
            // after at least one calibration point, the calibration process can be finished
            if (calibratingSpeakerCount >= 1) {
                document.getElementById("camera-direction-button").disabled = false
            }
            const nextButton = button.parentNode.children[calibratingSpeakerCount]
            nextButton.disabled = false
        }
    })
}

// Add camera -> mic vector
function pointCameraCalibration(button) {
    const instructionText = document.getElementById("calibration-instruction");
    button.disabled = true;
    const body = { method: "post", data: {}};
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
            getCalibrationState()
        }
    });
}

async function calibrationIsSet() {
    const body = { method: "get" };
    const reset_button = document.getElementById("camera-direction-button")
    fetch("/calibration/is_set", body)
        .then((data) => data.json())
        .then((json) => {
            if (json["is_set"]) {
                const instructionText = document.getElementById(
                    "calibration-instruction"
                );
                instructionText.innerHTML =
                    "Press the button below to reset the calibration.";
                
                reset_button.innerHTML = "Reset calibration";
                reset_button.disabled = false;
                reset_button.onclick = () => resetCalibration(reset_button);
            } else if(calibratingSpeakerCount >= 1){
                reset_button.disabled = false;
                reset_button.innerHTML = "Submit current camera direction.";
                reset_button.onclick = () => pointCameraCalibration(reset_button);
            } else {
                reset_button.disabled = true;
                reset_button.innerHTML = "Submit current camera direction.";
                reset_button.onclick = () => pointCameraCalibration(reset_button);
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
    addCalibrationSpeaker()
}


function resetCalibration(reset_button) {
    const body = { method: "post", data: {}};
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
    getCalibrationState()
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

async function getCalibrationState() {
    const body = { method: "get", data: {} };
    fetch("/calibration/number-of-calibrated", body)
        .then((data) => data.json())
        .then((json) => {
            if (json["speaker-points-length"]) {
                let actual_length = json["speaker-points-length"]
                if(actual_length > totalCalibrations)
                    actual_length = totalCalibrations

                calibratingSpeakerCount = actual_length
                // Set all buttons with id lower to disabled
                const buttons = document.getElementsByClassName("calibration-button");
                for(let i = 0; i < actual_length; i++) {
                    buttons[i].innerHTML = "Set"
                    buttons[i].disabled = true
                }
                if(calibratingSpeakerCount !== totalCalibrations)
                    buttons[calibratingSpeakerCount].disabled = false
            }
        });
}

if (document.getElementById("presets") !== null) {
    selectCaliTab()
}

if (document.getElementById("cal") !== null) {
    getCalibrationState().then(calibrationIsSet().then())
}
