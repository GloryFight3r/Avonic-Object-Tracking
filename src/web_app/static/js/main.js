function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

onSuccess = {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "camera-position-get-form": onPositionGet,
    "presets-camera-position-set-form": onPositionSet,
    "presets-camera-zoom-set-form": onZoomSet,
    "microphone-get-direction-form": onDirectionGet,
    "microphone-set-direction-form": onMicrophoneDirectionSet,
    "microphone-speaking-form": onSpeaking,
    "thread-value-form": onValueGet,
    "preset-get-list-form": refreshPresetList,
    "camera-coords-get-form": onCameraCoordsGet
};

async function onError(button) {
    button.classList.add("contrast");
    await sleep(350);
    button.classList.remove("contrast");
    await sleep(250);
    button.classList.add("contrast");
    await sleep(350);
    button.classList.remove("contrast");
}

[...document.forms].forEach(
    (f) =>
        (f.onsubmit = async (e) => {
            e.preventDefault();
            const b = f.getElementsByTagName("button")[0]
            b.ariaBusy = "true"
            const method = f.method;
            let body = {};
            switch (method) {
                case "get":
                    body = { method: method };
                    break;
                case "post":
                    body = { method: method, body: new FormData(f) };
                    break;
            }
            const response = await fetch(f.action, body);
            const fun = onSuccess[f.id];
            if (response.status === 200 && fun !== undefined) {
                fun(response.json());
            }
            b.ariaBusy = "false"
            if (response.status !== 200) {
                const b = f.getElementsByTagName("button")[0];
                onError(b).then()
            }
        })
);

const presetform = document.getElementById("preset-form");

presetform.onsubmit = async (e) => {
    e.preventDefault();
    const b = f.getElementsByTagName("button")[0]
    b.ariaBusy = "true"
    const button_id = e.submitter.id;
    let body = {};
    switch (button_id) {
        case "add-preset-button":
            presetform.setAttribute("method", "POST");
            presetform.action = "/preset/add";
            body = { method: presetform.method, body: new FormData(presetform) };
            break;
        case "edit-preset-button":
            presetform.setAttribute("method", "POST");
            presetform.action = "/preset/edit";
            body = { method: presetform.method, body: new FormData(presetform) };
            break;
        case "remove-preset-button":
            presetform.setAttribute("method", "POST");
            presetform.action = "/preset/remove";
            body = { method: presetform.method, body: new FormData(presetform) };
            break;
        case "point-to-closest":
            presetform.setAttribute("method", "GET");
            presetform.action = "/preset/point";
            body = { method: presetform.method };
            break;
    }
    const response = await fetch(presetform.action, body);
    if (response.status === 200) {
        document.getElementById("reload-preset-button").click();
    }
    b.ariaBusy = "false"
    if (response.status !== 200) {
        const b = e.submitter;
        onError(b).then();
    }
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

hideOn()
selectMovement()
selectCaliTab()
calibrationIsSet().then()
