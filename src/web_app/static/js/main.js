function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

onSuccess = {
    "camera-off-form": hideOff,
    "camera-on-form": hideOn,
    "camera-zoom-get-form": onZoomGet,
    "camera-position-get-form": onPositionGet,
    "camera-position-set-form": onPositionSet,
    "microphone-get-direction-form": onDirectionGet,
    "microphone-set-direction-form": onMicrophoneDirectionSet,
    "microphone-speaking-form": onSpeaking,
    "thread-value-form": onValueGet,
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

[...document.forms].filter((f) => f.id != "preset-form").forEach(
    (f) =>
        (f.onsubmit = async (e) => {
            e.preventDefault();
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
            if (response.status !== 200) {
                const b = f.getElementsByTagName("button")[0];
                onError(b).then()
            }
        })
);

