function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function hideOff() {
    document.getElementById("camera-off-form").style.display = "none"
    document.getElementById("camera-on-form").style.display = "block"
}

function hideOn() {
    document.getElementById("camera-off-form").style.display = "block"
    document.getElementById("camera-on-form").style.display = "none"
}

async function onZoomGet (data) {
    const d = await data
    document.getElementById("zoom-value").value = d["zoom-value"]
}

function selectMovement() {
    document.getElementById("camera-move-absolute").style.display = "none"
    document.getElementById("camera-move-relative").style.display = "none"
    document.getElementById("camera-move-vector").style.display = "none"
    document.getElementById(document.getElementById("movement-select").value).style.display = "block"
}

async function onDirectionGet(data) {
    const d = (await data)["microphone-direction"]
    document.getElementById("mic-direction-x").value = d[0]
    document.getElementById("mic-direction-y").value = d[1]
    document.getElementById("mic-direction-z").value = d[2]
}

async function onValueGet(data) {
    const d = await data
    document.getElementById("thread-value").value = d["value"]
}

async function onSpeaking(data) {
    const d = await data
    document.getElementById("speaking").value = d["microphone-speaking"]
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
    const instructionText = document.getElementById("calibration-instruction")
    instructionText.innerHTML = "Please stand somewhere in the room and speak up."
    button.innerHTML = "Listening..."
    button.disabled = true
    const body = {method: "get"}
    fetch("/calibration/add_directions_to_speaker", body).then(async function (res) {
	button.disabled = false
	if (res.status != 200) {
	    onError(button)
	} else {
    	    button.disabled = true
	    setTimeout(() => {
		pointCameraCalibration(button)
	    }, 500)
	}
    })
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

onSuccess = {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "microphone-get-direction-form": onDirectionGet,
    "microphone-speaking-form": onSpeaking,
    "thread-value-form": onValueGet
};

[...document.forms].forEach(f => f.onsubmit = async(e) => {
    e.preventDefault()
    const method = f.method
    let body = {}
    switch(method) {
        case "get":
            body = {method: method}
            break
        case "post":
            body = {method: method, body: new FormData(f)}
            break
    }
    const response = await fetch(f.action, body)
    const fun = onSuccess[f.id]
    if (response.status === 200 && fun !== undefined) {
        fun(response.json())
    }
    if (response.status !== 200) {
        const b = f.getElementsByTagName("button")[0]
	onError(b)
    }
})

async function onError(button) {
    button.classList.add("contrast")
    await sleep(350)
    button.classList.remove("contrast")
    await sleep(250)
    button.classList.add("contrast")
    await sleep(350)
    button.classList.remove("contrast")
}

hideOn()
selectMovement()
calibrationIsSet()
