async function onValueGet(data) {
  const d = await data;
  document.getElementById("thread-value").value = d["value"];
}

async function startThread() {
  const body = { method: "get" };
  fetch("/thread/running", body).then(async function (res) {
    console.log(res);
    if (!res["is-running"]) {
      const post_body = { method: "post", data: {} };
      fetch("thread/start", post_body);
    }
  });
}
