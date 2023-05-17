import { startThread } from "./main.js"

const totalCalibrations = 3
let calibratingSpeakerCount = 1
let isCalibrating = false

function addCalibrationSpeaker() {
    calibratingSpeakerCount++
    isCalibrating = false
    const instructionText = document.getElementById("calibration-instruction")
    const innHTML = instructionText.innerHTML
    instructionText.innerHTML = innHTML.substring(0, innHTML.length-1) + calibratingSpeakerCount
    const body = {method: "get"}
    const button = document.getElementById("calibration-button")
    console.log("Add calibration speaker")
    fetch("/calibration/add_directions_to_speaker", body).then(function (res) {
        if (res.status != 200) {
            onError(button)
        } else {
            if (calibratingSpeakerCount > totalCalibrations) {
                button.disabled = false
                pointCameraCalibration(button)
            } else {
                setTimeout(() => {
                    isCalibrating = true
                }, 1000)
            }
        }
    })
}

async function calibrationIsSet() {
    const body = {method: "get"}
    fetch("/calibration/is_set", body).then(data => data.json()).then((json) => {
        if (json["is_set"]) {
            const button = document.getElementById("calibration-button")
            const instructionText = document.getElementById("calibration-instruction")
            instructionText.innerHTML = "Press the button below to reset the calibration."
            button.innerHTML = "Reset calibration"
            button.onclick = () => resetCalibration(button)
        }
    })
}

async function startCalibration(button) {
    await startThread()
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML = "Please stand somewhere in the room, point the camera at your face and speak up. \nCalibrating point 1"
    button.innerHTML = "Listening..."
    button.disabled = true
    calibratingSpeakerCount = 1
    isCalibrating = true
}

function pointCameraCalibration(button) {
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML = "Please point the camera directly to the microphone."
    button.innerHTML = "Done."
    button.disabled = false
    button.onclick = () => {
    	button.disabled = true
    	const body = {method: "get"}
        fetch("/calibration/add_direction_to_mic", body).then(async function (res) {
            button.disabled = false
            if (res.status != 200) {
                onError(button)
            } else {
                button.disabled = false
                button.innerHTML = "Reset calibration"
    		instructionText.innerHTML = "Don't forget to set the height too. Press below to reset the calibration."
        	button.onclick = () => resetCalibration(button)
            }
        })
    }
}

function resetCalibration(button) {
    const body = {method: "get"}
    fetch("/calibration/reset", body).then(async function (res) {
	    button.disabled = true
	    if (res.status != 200) {
	        onError(button)
	    } else {
        	    const instructionText = document.getElementById("calibration-instruction")
        	    instructionText.innerHTML = "To start calibration, please click below."
	        button.disabled = false
	        button.innerHTML = "Start calibration"
        	    button.onclick = () => startCalibration(button)
	    }
    })
}

export { addCalibrationSpeaker, isCalibrating, calibrationIsSet, startCalibration }
