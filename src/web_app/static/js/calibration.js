const totalCalibrations = 3
let calibratingSpeakerCount = 1
let isCalibrating = false

function addCalibrationSpeaker() {
    calibratingSpeakerCount++
    isCalibrating = false
    const instructionText = document.getElementById("calibration-instruction")
    const innHTML = instructionText.innerHTML
    instructionText.innerHTML = "Click below to calibrate point " + calibratingSpeakerCount
    const body = {method: "get"}
    const button = document.getElementById("calibration-button")
    fetch("/calibration/add_directions_to_speaker", body).then(function (res) {
        if (res.status != 200) {
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

//async function refreshCalibration() {
//    const submitCalButton = document.getElementById("submit-calibration");
//    submitCalButton.innerHTML = "Add position";
//    submitCalButton.disabled = false;
//    fetch("/calibration/get_count", { method: "get" })
//        .then((data) => data.json())
//        .then((jsonData) => {
//            const count = parseInt(jsonData["count"]);
//            const checks = document.getElementsByClassName("calibration-checkbox");
//            console.log(count, checks.length);
//            document.getElementById("submit-calibration").disabled = count === checks.length;
//            for (let i = 0; i < checks.length; i++) {
//                checks[i].checked = i < count;
//            }
//        });
//}

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
    fetch("thread/start", post_body);
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML =
        "Please stand somewhere in the room, point the camera at your face and speak up."
    button.innerHTML = "Listening..."
    button.disabled = true
    isCalibrating = true
}


//function onWaitCalibration() {
//    const submitCalButton = document.getElementById("submit-calibration");
//    submitCalButton.innerHTML = "Please speak up...";
//    submitCalButton.disabled = true;
//}

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
