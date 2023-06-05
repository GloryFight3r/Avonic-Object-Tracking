if (typeof onSuccess !== 'undefined') {
  onSuccess = Object.assign({}, onSuccess, {
    "thread-value-form": onValueGet,
    "thread-preset" : usePresets
  });
}
else {
  onSuccess = {
    "thread-value-form": onValueGet,
    "thread-preset" : usePresets
  }
} 

async function onValueGet(data) {
  const d = await data;
  document.getElementById("thread-value").value = d["value"];
}

async function usePresets(data) {

  const d = (await data)["preset"];
  
  if(d === 0) {
    document.getElementById("preset-use").value = "Using continuous tracking";
  }
  else if(d === 1){
    document.getElementById("preset-use").value = "Using presets";  
  }
}
