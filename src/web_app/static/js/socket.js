const socket = io();

socket.on("my response", (args) => {
    console.log(args["data"])
});

socket.on("microphone-update", async (args) => {
    if (onDirectionGet !== undefined) {
        onDirectionGet(args).then()
        onSpeaking(args).then()
    }
})

socket.on("camera-update", async (args) => {
    if (hideOff === undefined) {
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
    if (!(onZoomGet === undefined)){
        return
    }
    await onZoomGet(args)
});

socket.on("footage-update", async (args) => {
    if (!(onFootageGet === undefined)){
        return
    }
    onFootageGet(args).then()
})

socket.on("calibration-update", async (args) => {
    if (!(onCameraCoordsGet === undefined)){
        return
    }
    await onCameraCoordsGet(args)
})

socket.on("connect", () => socket.emit("connected", {}))

socket.on("no-settings", () => openSettings())

socket.on("yes-settings", () => {
    document.getElementById("settings-save-button").ariaBusy = "false"
    closeSettings()
    if (!(requestPresetList === undefined)) {
        return
    }
    requestPresetList().then()
})