import { addCalibrationSpeaker, isCalibrating, calibrationIsSet, startCalibration } from "./calibration.js"
window.startCalibration = startCalibration

const socket = io()

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

async function onDirectionGet(data) {
    const d = (await data)["microphone-direction"]
    document.getElementById("mic-direction-x").value = d[0].toFixed(3)
    document.getElementById("mic-direction-y").value = d[1].toFixed(3)
    document.getElementById("mic-direction-z").value = d[2].toFixed(3)
}

async function onSpeaking(data) {
    const d = await data
    const isSpeaking = d["microphone-speaking"]
    document.getElementById("speaking").value = isSpeaking

    if (isCalibrating && isSpeaking) {
        addCalibrationSpeaker()
    }
}

async function startThread() {
    const body = {method: "get"}
    fetch("/thread/running", body).then(async function (res) {
	    if (!res["is-running"]) {
	        const post_body = {method: "post", data: {}}
	        fetch("thread/start", post_body)
	    }
    })
}

async function onValueGet(data) {
    const d = await data
    document.getElementById("thread-value").value = d["value"]
}

const onSuccess = {
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

function selectMovement() {
    document.getElementById("camera-move-absolute").style.display = "none"
    document.getElementById("camera-move-relative").style.display = "none"
    document.getElementById("camera-move-vector").style.display = "none"
    document.getElementById(document.getElementById("movement-select").value).style.display = "block"
}

socket.on('my response', (args) => {
    console.log(args["data"])
})

socket.on('microphone-update', async(args) => {
    onDirectionGet(args).then()
    onSpeaking(args).then()
})

socket.on('camera-video-update', (args) => {
    switch(args["state"]) {
        case "on":
            hideOn()
            break
        case "off":
            hideOff()
            break
    }
})

socket.on('new-camera-zoom', async(args) => {
    await onZoomGet(args)
})

hideOn()
selectMovement()
calibrationIsSet()

export { startThread }
