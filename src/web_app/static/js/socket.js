const socket = io();

socket.on("my response", (args) => {
    console.log(args["data"])
});

socket.on("microphone-update", async (args) => {
    if (onDirectionGet in window) {
        onDirectionGet(args).then()
        onSpeaking(args).then()
    }
})

socket.on("camera-update", async (args) => {
    if (!(hideOff in window)) {
        return
    }
    switch (args["camera-video"]) {
        case "on":
            hideOn();
            break;
        case "off":
            hideOff();
            break;
        default:
            console.log("Camera video is neither on or off.")
    }
    onZoomGet(args).then()
    onPositionGet((await args)["camera-direction"]).then()
});

socket.on("new-camera-zoom", async (args) => {
    if (!(onZoomGet in window)){
        return
    }
    await onZoomGet(args)
});

socket.on("footage-update", async (args) => {
    if (!(onFootageGet in window)){
        return
    }
    onFootageGet(args).then()
})

socket.on("calibration-update", async (args) => {
    if (!(onCameraCoordsGet in window)){
        return
    }
    await onCameraCoordsGet(args)
})

socket.on("connect", () => socket.emit("connected", {}))

socket.on("no-settings", () => openSettings())

socket.on("yes-settings", () => {
    document.getElementById("settings-save-button").ariaBusy = "false"
    closeSettings()
    if (!(requestPresetList in window)) {
        return
    }
    requestPresetList().then()
})