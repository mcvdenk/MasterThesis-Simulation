var socket = new WebSocket("ws://www.mvdenk.com/thesis:8765");
var container = document.getElementById("container");

function authenticate(form) {
    var msg = JSON.stringify({
        keyword: "AUTHENTICATE-REQUEST",
        data: {
            username: form.elements["username"].value,
            password: form.elements["password"].value,
            browser: navigator.appVersion,
        }
    });
    while (socket.readyState != 1) {}
    socket.send(msg);
    socket.onmessage = function (event) {
        msg = JSON.parse(event.data);
        if (msg.keyword == "AUTHENTICATE-RESPONSE") {
            switch(msg.data) {
                case "LOGGED_IN":
                    menu();
                    break;
                case "PASSWORD_INCORRECT":
                    incorrect_password();
                    break;
                case "NEW_USERNAME":
                    new_user();
                    break;
            }
        }
    }
}

function password_incorrect() {
}

function new_user() {
}

function menu() {
    container.innerHTML = " \
                           <h3>Menu</h3> \
                           <button onclick=\'learn()\'> Learn </button> \
                           <button onclick=\'overview()\'> Overview </button> \
                           <button onclick=\'change_userdata()\'> Change user data </button> \
                           <button onclick=\'logout()\'> Log out </button>";
}

function learn() {
    var msg = JSON.stringify({
        keyword: "LEARN-REQUEST",
        data: ""
    });
    socket.send(msg);
    socket.onmessage = function(event) {
        msg = JSON.parse(event.data);
        if (msg.keyword == "LEARN-RESPONSE") {
            container.innerHTML = "";
            var parserOptions = {
                edges: {
                    inheritColors: true
                },
                nodes: {
                    fixed: false,
                    parseColor: true
                }
            }
            var parsed = vis.network.convertGephi(msg.data, parserOptions);

            var data = {
                nodes = parsed.nodes;
                edges = parsed.edges;
            }

            var network = new vis.Network(container, data);
        }
    }
}

function overview() {
    var msg = JSON.stringify({
        keyword: "LEARNED_EDGES-REQUEST",
        data: ""
    });
    socket.send(msg);
    socket.onmessage = function(event) {
        msg = JSON.parse(event.data);
        if (msg.keyword == "LEARNED_EDGES-RESPONSE") {
            container.innerHTML = "";
            var parserOptions = {
                edges: {
                    inheritColors: true
                },
                nodes: {
                    fixed: false,
                    parseColor: true
                }
            }
            var parsed = vis.network.convertGephi(msg.data, parserOptions);

            var data = {
                nodes = parsed.nodes;
                edges = parsed.edges;
            }

            var network = new vis.Network(container, data);
        }
    }
}

function validate(edges) {
}

function change_userdata() {
}

function logout() {
}
