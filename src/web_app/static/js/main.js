function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function onError(button) {
    button.classList.add("contrast");
    await sleep(350);
    button.classList.remove("contrast");
    await sleep(250);
    button.classList.add("contrast");
    await sleep(350);
    button.classList.remove("contrast");
}

[...document.forms].filter((f) => f.id !== "preset-form").forEach(
    (f) =>
        (f.onsubmit = async (e) => {
            e.preventDefault();
            const b = f.getElementsByTagName("button")[0]
            b.ariaBusy = "true"
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
            b.ariaBusy = "false"
            if (response.status !== 200) {
                const b = f.getElementsByTagName("button")[0];
                onError(b).then()
            }
        })
);
