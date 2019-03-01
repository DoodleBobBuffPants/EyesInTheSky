function post(url, body = {}) {
    console.log("");
    console.log("POST to ", url, " with ", body);
    fetch(url, {
        method: 'POST', body: JSON.stringify(body), headers: {'Content-Type': 'application/json'},
    })
        .then(res => {
            console.log(res.status);
            res.json().then(data => console.log(data))
        })
        .catch(err => console.log(err))
}

function abort() {
    post('/abort')
}

function follow() {
    post('/follow')
}

function stop_follow() {
    post('/stop_follow')
}

function video_start() {
    let vid = document.getElementById("video_feed_block");
    vid.innerHTML = "<img src='/video_feed'>";
    // vid.innerHTML += "<img src='/video_feed1'>";
}

function video_clear() {
    let vid = document.getElementById("video_feed_block");
    vid.innerHTML = "";
}

function connect() {
    post('/connect')
}

function disconnect() {
    post('/disconnect')
}

function takeoff() {
    post('/takeoff')
}

function change() {
    post("/change_rel_coords", {
        'new_x': document.getElementById('new_x').value,
        'new_y': document.getElementById('new_y').value
    })
}

function check_battery(){
    console.log("");
    console.log("POST to battery");
    fetch('/battery', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
    })
        .then(res => {
             res.json().then(data => {console.log(data);document.getElementById("level").innerText = data["battery"]});
        })
        .catch(err => console.log(err))

}
