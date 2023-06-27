function selectFootageTab() {
  document.getElementById("footage-tab").style.display = "none"
  document.getElementById("vis-tab").style.display = "none"
  const selected = document.getElementById("footage-vis-select").value
  document.getElementById(selected).style.display = "block"
  const header = document.getElementById("footage-vis-title")
  switch (selected) {
    case "footage-tab":
      document.getElementById("vis-title").style.display = "block"
      document.getElementById("footage-title").style.display = "none"
      header.innerText = "Footage 🎬"
      break
    case "vis-tab":
      document.getElementById("vis-title").style.display = "none"
      document.getElementById("footage-title").style.display = "block"
      header.innerText = "Visualisation 📺"
      break
    default:
  }
}

if (document.getElementById("footage-tab") !== null) {
  selectFootageTab()
}
