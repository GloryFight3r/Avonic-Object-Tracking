async function onValueGet(data) {
  const d = await data;
  document.getElementById("thread-value").value = d["value"];
}
