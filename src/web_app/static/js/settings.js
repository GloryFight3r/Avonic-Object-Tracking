/*
 * Modal
 *
 * Pico.css - https://picocss.com
 * Copyright 2019-2023 - Licensed under MIT
 * https://github.com/picocss/examples/blob/master/v1-preview/js/modal.js
 */
const isOpenClass = "modal-is-open";
const openingClass = "modal-is-opening";
const closingClass = "modal-is-closing";
const animationDuration = 400; // ms
let visibleModal = null;

const toggleSettings = () => {
    const modal = document.getElementById("settings")
    typeof modal != "undefined" && modal != null && settingsOpen()
        ? closeSettings()
        : openSettings()
}

const settingsOpen = () => {
    const modal = document.getElementById("settings")
    return modal.hasAttribute("open") && modal.getAttribute("open") !== "false";
}

const openSettings = () => {
    if (isScrollbarVisible()) {
        document.documentElement.style.setProperty("--scrollbar-width", `${getScrollbarWidth()}px`)
    }
    document.documentElement.classList.add(isOpenClass, openingClass)

    // get current settings
    fetch("/settings/get", { method: "get" }).then(async (response) => {
        const d = await response.json()
        document.getElementById("settings-camera-ip").value = d["camera-ip"]
        document.getElementById("settings-camera-port").value = d["camera-port"]
        document.getElementById("settings-camera-http-port").value = d["camera-http-port"]
        document.getElementById("settings-microphone-ip").value = d["microphone-ip"]
        document.getElementById("settings-microphone-port").value = d["microphone-port"]
        document.getElementById("settings-microphone-thresh").value = d["microphone-thresh"]
        document.getElementById("settings-files-path").value = d["filepath"]
    })

    const modal = document.getElementById("settings")
    setTimeout(() => {
        visibleModal = modal;
        document.documentElement.classList.remove(openingClass)
    }, animationDuration);
    modal.setAttribute("open", true)
}

const closeSettings = () => {
    visibleModal = null;
    document.documentElement.classList.add(closingClass);
    const modal = document.getElementById("settings")
    setTimeout(() => {
        document.documentElement.classList.remove(closingClass, isOpenClass);
        document.documentElement.style.removeProperty("--scrollbar-width");
        modal.removeAttribute("open");
    }, animationDuration);
}

const getScrollbarWidth = () => {
    // Creating invisible container
    const outer = document.createElement("div")
    outer.style.visibility = "hidden"
    outer.style.overflow = "scroll" // forcing scrollbar to appear
    outer.style.msOverflowStyle = "scrollbar" // needed for WinJS apps
    document.body.appendChild(outer)

    // Creating inner element and placing it in the container
    const inner = document.createElement("div")
    outer.appendChild(inner)

    // Calculating difference between container's full width and the child width
    const scrollbarWidth = outer.offsetWidth - inner.offsetWidth

    // Removing temporary elements from the DOM
    outer.parentNode.removeChild(outer)

    return scrollbarWidth
}

const isScrollbarVisible = () => {
    return document.body.scrollHeight > screen.height
}

// Custom code
onSuccess = Object.assign({}, onSuccess, {
    "settings-form": closeSettings
})
