if (typeof onSuccess !== 'undefined') {
  onSuccess = Object.assign({}, onSuccess, {
    "microphone-get-direction-form": onDirectionGet,
    "microphone-set-direction-form": onMicrophoneDirectionSet,
    "microphone-speaking-form": onSpeaking,
  });
}
else {
  onSuccess = {
    "microphone-get-direction-form": onDirectionGet,
    "microphone-set-direction-form": onMicrophoneDirectionSet,
    "microphone-speaking-form": onSpeaking,
  }
}

async function onMicrophoneDirectionSet(data) {
    const d = (await data)["microphone-direction"];

    document.getElementById("mic-direction-x2").value = d[0].toFixed(5)
    document.getElementById("mic-direction-y2").value = d[1].toFixed(5)
    document.getElementById("mic-direction-z2").value = d[2].toFixed(5)
}

async function onDirectionGet(data) {
    const d = (await data)["microphone-direction"];
    document.getElementById("mic-direction-x").value = d[0].toFixed(5)
    document.getElementById("mic-direction-y").value = d[1].toFixed(5)
    document.getElementById("mic-direction-z").value = d[2].toFixed(5)
}

async function onSpeaking(data) {
    const d = await data;
    const isSpeaking = d["microphone-speaking"]
    document.getElementById("speaking").value = isSpeaking;

    if (isCalibrating && isSpeaking) {
        addCalibrationSpeaker()
    }
}
