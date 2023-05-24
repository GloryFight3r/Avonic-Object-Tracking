async function onDirectionGet(data) {
    const d = (await data)["microphone-direction"];
    document.getElementById("mic-direction-x").value = d[0].toFixed(3);
    document.getElementById("mic-direction-y").value = d[1].toFixed(3);
    document.getElementById("mic-direction-z").value = d[2].toFixed(3);
}

async function onSpeaking(data) {
    const d = await data;
    const isSpeaking = d["microphone-speaking"]
    document.getElementById("speaking").value = isSpeaking;

    if (isCalibrating && isSpeaking) {
        addCalibrationSpeaker()
    }
}
