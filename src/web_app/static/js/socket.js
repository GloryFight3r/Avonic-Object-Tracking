socket.on("my response", (args) => {
  console.log(args["data"]);
});

socket.on("microphone-update", async (args) => {
  onDirectionGet(args).then();
  onSpeaking(args).then();
});

socket.on("camera-video-update", (args) => {
  switch (args["state"]) {
    case "on":
      hideOn();
      break;
    case "off":
      hideOff();
      break;
  }
});

socket.on("new-camera-zoom", async (args) => {
  await onZoomGet(args);
});
