var uname = "";
var cont = "mycontainer";
var ws = new WebSocket("ws://www.mvdenk.com:5678");

ws.onopen = function (event) {
    document.getElementById(cont).style.visibility = "visible";
    document.getElementById("username").focus();
}

function authenticate() {
    uname = document.getElementById("username").value;
    console.log(uname);
    var msg = {
        keyword: "AUTHENTICATE-REQUEST",
        data: {
            username: uname,
            browser: navigator.platform
        }
    }
    ws.send(JSON.stringify(msg));
}

ws.onmessage = function (event) {
    var msg = JSON.parse(event.data);
    console.log(msg);

    switch(msg.keyword) {
        case "MAP-RESPONSE":
            show_map(msg.data);
            break;
        case "AUTHENTICATE-RESPONSE":
            show_menu();
            break;
        case "LEARNED_ITEMS-RESPONSE":
            coloured_map = colourise_progress(msg.data);
            show_map(coloured_map);
            break;
        case "LEARN-RESPONSE":
            show_map(flashmap(msg.data));
            break;
        case "NO_MORE_FLASHEDGES":
            done_learning();
            break;
    }
}

function show_map(map) {
    // provide the data in the vis format
    var graph = {
        nodes: map.nodes,
        edges: map.edges
    };

    var options = {
        edges: {
            arrows: {
                to: {enabled: true}
            }
        }
    };
    
    var container =  document.getElementById(cont);
    container.innerHTML = "";

    // initialize your network!
    var network = new vis.Network(container, graph, options);
}

function show_menu() {
    document.getElementById(cont).innerHTML = 
        "<input type='button' onclick='view_learned()' value='View learned items' /><br> \
         <input type='button' onclick='learn()' value='Start learning' /><br> \
         <input type='button' onclick='logout()' value='Logout' /><br>";
}

function colourise_progress(map) {
}

function flashmap(map) {
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) {
            map.edges[i].color = "orange";
            for (j = 0; j < map.nodes.length; j++) {
                if (map.edges[i].to == map.nodes[j].id) {
                    map.nodes[j].color = {background : "orange"};
                    map.nodes[j].true_label = map.nodes[j].label;
                    map.nodes[j].label = "";
                }
            }
        }
    }
    return map;
}

function show_login() {
}

function view_learned() {
}

function learn() {
    var msg = {
        keyword: "LEARN-REQUEST",
        data: {}
    }
    ws.send(JSON.stringify(msg));
}

function done_learning() {
    alert("There is nothing left to learn for now");
}

function logout() {
    ws.close();
    location.reload();
}
