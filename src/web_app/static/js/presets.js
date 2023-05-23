async function refreshPresetList(data) {
    const d = (await data)["preset-list"];
    const presetList = document.getElementById("preset-select");
    presetList.innerHTML = "";
    d.forEach((preset_ind) => presetList.add(new Option(preset_ind, preset_ind)));

    if (d.length !== 0) {
        changePreset();
    }
}

async function setNewPreset(data) {
    const d = (await data)["microphone-direction"];
    const d2 = await data;

    document.getElementById("mic-direction-x2").value = d[0];
    document.getElementById("mic-direction-y2").value = d[1];
    document.getElementById("mic-direction-z2").value = d[2];

    document.getElementById("camera-direction-alpha").value =
        d2["position-alpha-value"];

    document.getElementById("camera-direction-beta").value =
        d2["position-beta-value"];

    document.getElementById("camera-zoom-value").value =
        d2["zoom-value"];
}

async function changePreset() {
    document.getElementById("preset-name").value =
        document.getElementById("preset-select").value;
    const response = await fetch("/preset/get_preset_info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            "preset-select": document.getElementById("preset-select").value,
        }),
    });
    if (response.status === 200) {
        setNewPreset(response.json());
    }
}
