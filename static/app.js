// Add User
function addUser() {

    fetch("/api/add-user", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            name: document.getElementById("name").value,

            email: document.getElementById("email").value,

            city: document.getElementById("city").value   // 👈 NEW

        })

    })
    .then(res => res.json())
    .then(data => show(data));
}


// Fetch Users
function fetchUsers() {

    fetch("/api/users")

        .then(res => res.json())

        .then(data => {

            document.getElementById("users").innerText =
                JSON.stringify(data, null, 2);

        });
}


// Run SQL
function runQuery() {

    fetch("/api/sql", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            query: document.getElementById("query").value
        })

    })
    .then(res => res.json())
    .then(data => show(data));
}


// Call Metrics
function callApi(url) {

    fetch(url)

        .then(res => res.text())

        .then(data => show(data));
}


// Volume
function writeVolume() {

    fetch("/api/volume/write")

        .then(res => res.json())

        .then(data => show(data));
}


function readVolume() {

    fetch("/api/volume/read")

        .then(res => res.json())

        .then(data => show(data));
}


// Show Response
function show(data) {

    document.getElementById("response").innerText =
        JSON.stringify(data, null, 2);
}