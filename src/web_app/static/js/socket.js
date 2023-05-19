const socket = io();

socket.on("my response", (args) => {
    console.log(args["data"])
});

socket.on("microphone-update", async (args) => {
    onDirectionGet(args).then()
    onSpeaking(args).then()

});

socket.on("camera-update", async (args) => {
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
    await onZoomGet(args)
});
