function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function hideOff() {
  document.getElementById("camera-off-form").style.display = "none";
  document.getElementById("camera-on-form").style.display = "block";
}

function hideOn() {
  document.getElementById("camera-off-form").style.display = "block";
  document.getElementById("camera-on-form").style.display = "none";
}

async function onZoomGet(data) {
  const d = await data;
  document.getElementById("zoom-value").value = d["zoom-value"];
}

async function onPositionGet(data) {
  const d = await data;
  document.getElementById("position-alpha-value").value =
    d["position-alpha-value"];
  document.getElementById("position-beta-value").value =
    d["position-beta-value"];
}

async function onPositionSet(data) {
  const d = await data;
  document.getElementById("camera-direction-alpha").value =
    d["position-alpha-value"];

  document.getElementById("camera-direction-beta").value =
    d["position-beta-value"];
}

function selectMovement() {
  document.getElementById("camera-move-absolute").style.display = "none";
  document.getElementById("camera-move-relative").style.display = "none";
  document.getElementById("camera-move-vector").style.display = "none";
  document.getElementById(
    document.getElementById("movement-select").value
  ).style.display = "block";
}

async function refreshPresetList(data) {
  const d = (await data)["preset-list"];
  const presetList = document.getElementById("preset-select");
  presetList.innerHTML = "";
  d.forEach((preset_ind) => presetList.add(new Option(preset_ind, preset_ind)));

  if (d.length != 0) {
    changePreset();
  }
}

async function onDirectionGet(data) {
  const d = (await data)["microphone-direction"];
  document.getElementById("mic-direction-x").value = d[0];
  document.getElementById("mic-direction-y").value = d[1];
  document.getElementById("mic-direction-z").value = d[2];
}

async function onMicrophoneDirectionSet(data) {
  const d = (await data)["microphone-direction"];

  document.getElementById("mic-direction-x2").value = d[0];
  document.getElementById("mic-direction-y2").value = d[1];
  document.getElementById("mic-direction-z2").value = d[2];
}

async function onValueGet(data) {
  const d = await data;
  document.getElementById("thread-value").value = d["value"];
}

async function onSpeaking(data) {
  const d = await data;
  document.getElementById("speaking").value = d["microphone-speaking"];
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
}

async function refreshCalibration() {
  const submitCalButton = document.getElementById("submit-calibration");
  submitCalButton.innerHTML = "Add position";
  submitCalButton.disabled = false;
  fetch("/calibration/get_count", { method: "get" })
    .then((data) => data.json())
    .then((jsonData) => {
      const count = parseInt(jsonData["count"]);
      const checks = document.getElementsByClassName("calibration-checkbox");
      console.log(count, checks.length);
      if (count == checks.length) {
        document.getElementById("submit-calibration").disabled = true;
      } else {
        document.getElementById("submit-calibration").disabled = false;
      }
      for (let i = 0; i < checks.length; i++) {
        if (i < count) {
          checks[i].checked = true;
        } else {
          checks[i].checked = false;
        }
      }
    });
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
  if (response.status == 200) {
    setNewPreset(response.json());
  }
}

function onWaitCalibration() {
  const submitCalButton = document.getElementById("submit-calibration");
  submitCalButton.innerHTML = "Please speak up...";
  submitCalButton.disabled = true;
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
  "add-calibration-form": refreshCalibration,
  "reset-calibration-form": refreshCalibration,
  "preset-get-list-form": refreshPresetList,
};

onWait = {
  "add-calibration-form": onWaitCalibration,
};

[...document.forms].forEach(
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
        b.classList.add("contrast");
        await sleep(350);
        b.classList.remove("contrast");
        await sleep(250);
        b.classList.add("contrast");
        await sleep(350);
        b.classList.remove("contrast");
      }
    })
);

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
  }
  const response = await fetch(presetform.action, body);
  if (response.status === 200) {
    document.getElementById("reload-preset-button").click();
  }
  if (response.status !== 200) {
    const b = e.submitter;
    b.classList.add("contrast");
    await sleep(350);
    b.classList.remove("contrast");
    await sleep(250);
    b.classList.add("contrast");
    await sleep(350);
    b.classList.remove("contrast");
  }
};

hideOn();
selectMovement();
refreshCalibration();
