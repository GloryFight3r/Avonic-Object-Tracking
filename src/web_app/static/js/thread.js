onSuccess = Object.assign({}, onSuccess, {
    "thread-preset" : usePresets
})

async function usePresets(data) {
    const d = (await data)["preset"];

    if(d === 0) {
        document.getElementById("preset-use").value = "Using continuous tracking";
    }
    else if(d === 1){
        document.getElementById("preset-use").value = "Using presets";
    }
}
