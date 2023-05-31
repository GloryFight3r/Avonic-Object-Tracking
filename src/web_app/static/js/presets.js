if (typeof onSuccess !== 'undefined') {
  onSuccess = Object.assign({}, onSuccess, {
    "preset-get-list-form": refreshPresetList,
    "camera-position-get-form": onPositionGet
  });
}
else {
  onSuccess = {
    "preset-get-list-form": refreshPresetList,
    "camera-position-get-form": onPositionGet
  }
} 

async function refreshPresetList(data) {
  const d = (await data)["preset-list"];
  const presetList = document.getElementById("preset-select");
  presetList.innerHTML = "";
  d.forEach((preset_ind) => presetList.add(new Option(preset_ind, preset_ind)));

  if (d.length !== 0) {
    changePreset();
  }
}

const set_mic_button = document.getElementById("set-mic-button")

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
  document.getElementById("preset-name").value = document.getElementById("preset-select").value;
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

async function onMicrophoneDirectionSet(data) {
    const d = (await data)["microphone-direction"];

    document.getElementById("mic-direction-x2").value = d[0];
    document.getElementById("mic-direction-y2").value = d[1];
    document.getElementById("mic-direction-z2").value = d[2];

    set_mic_button.ariaBusy = false
}

async function requestPresetList() {
  const response = await fetch("/preset/get_list", {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  refreshPresetList(response.json());
}

async function changePreset() {
    document.getElementById("preset-name").value =
        document.getElementById("preset-select").value;
    const response = await fetch("/preset/info/" + document.getElementById("preset-select").value, {
        method: "GET"
    });
    if (response.status === 200) {
        setNewPreset(response.json());
    }
}

set_mic_button.onclick = async () => {
  set_mic_button.ariaBusy = true
}

const presetform = document.getElementById("preset-form");

presetform.onsubmit = async (e) => {
  e.preventDefault();
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
    requestPresetList();
  }
  if (response.status !== 200) {
    const b = e.submitter;
    onError(b).then();
  }
}

function loadPresets() {
  requestPresetList();
}

if (presetform !== null) {
  loadPresets();
}
