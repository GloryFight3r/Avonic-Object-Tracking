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

async function refreshCalibration() {
    const submitCalButton = document.getElementById("submit-calibration")
    submitCalButton.innerHTML = "Add position"
    submitCalButton.disabled = false
    fetch("/calibration/get_count", {method: "get"}).then(data => data.json()).then(jsonData => {
	const count = parseInt(jsonData["count"])
    	const checks = document.getElementsByClassName("calibration-checkbox")
	console.log(count, checks.length)
    	if (count == checks.length) {
    	    document.getElementById("submit-calibration").disabled = true
    	} else {
    	    document.getElementById("submit-calibration").disabled = false
	}
    	for (let i = 0; i < checks.length; i++) {
	    if (i < count) {
    	    	checks[i].checked = true
	    } else {
    	    	checks[i].checked = false
	    }
    	}
    })
}

function onWaitCalibration() {
    const submitCalButton = document.getElementById("submit-calibration")
    submitCalButton.innerHTML = "Please speak up..."
    submitCalButton.disabled = true
}

onSuccess = {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "microphone-get-direction-form": onDirectionGet,
    "microphone-speaking-form": onSpeaking,
    "thread-value-form": onValueGet,
    "add-calibration-form": refreshCalibration,
    "reset-calibration-form": refreshCalibration
};

onWait = {
    "add-calibration-form": onWaitCalibration
}

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
        b.classList.add("contrast")
        await sleep(350)
        b.classList.remove("contrast")
        await sleep(250)
        b.classList.add("contrast")
        await sleep(350)
        b.classList.remove("contrast")
    }
})

hideOn()
selectMovement()
refreshCalibration()
