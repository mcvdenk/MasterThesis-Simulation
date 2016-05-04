var uname = "";
var cont = "mycontainer";
var ws = new WebSocket("ws://www.mvdenk.com:5678");
var network
var nodes
var edges
var map
var options = {
    nodes: {
        shape: 'box',
    },
    edges: {
        arrows: {
            to: {enabled: true}
        }
    },
    interaction: {
        selectable: false,
        dragNodes: false
    }
};

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
            name: uname,
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

    nodes = new vis.DataSet(map.nodes);
    edges = new vis.DataSet(map.edges);

    var graph = {
        nodes: nodes,
        edges: edges
    };

    
    var container =  document.getElementById(cont);
    container.innerHTML = "";

    // initialize your network!
    network = new vis.Network(container, graph, options);

    network.on('click', function(properties) {
        for (i=0; i < map.edges.length; i++) {
            if ('correct' in map.edges[i]) {
                map.edges[i].correct = !map.edges[i].correct;
                if (map.edges[i].correct) nodes.update([{ id : map.edges[i].to, color: {background: "green"}}]);
                else nodes.update([{ id : map.edges[i].to, color: {background: "red"}}]);
            }
        }
    });
}

function show_menu() {
    document.getElementById(cont).innerHTML = "";
    document.getElementById("menu").style.visibility = "visible";
}

function colourise_progress(data) {
}

function flashmap(data) {
    map = data;
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) {
            map.edges[i].color = "orange";
            for (j = 0; j < map.nodes.length; j++) {
                if (map.edges[i].to == map.nodes[j].id) {
                    map.nodes[j].color = {background : "orange"};
                    map.nodes[j].true_label = map.nodes[j].label;
                    map.nodes[j].label = "______";
                }
            }
        }
    }
    document.getElementById("panel").innerHTML = "<a href='#' onclick='undo()'> Undo </a> <a href='#' onclick='show_answer()'> Show answer </a>";
    return map;
}

function show_answer() {
    var index
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) {
            for (j=0;j < map.nodes.length; j++) {
                if (map.edges[i].to == map.nodes[j].id) index = j;
            }
            nodes.update([{id: map.edges[i].to, color: {background : "green"}}]);
            nodes.update([{id: map.edges[i].to, label: map.nodes[index].true_label}]);
            map.edges[i].correct = true;
        }
    }
    document.getElementById("panel").innerHTML = "<a href='#' onclick='validate()'> Next </a>";
}

function view_learned() {
    var msg = {keyword: "LEARNED_ITEMS-REQUEST", data: {}};
    ws.send(JSON.stringify(msg));
}

function undo() {
    var msg = {keyword: "UNDO", data: {}};
    ws.send(JSON.stringify(msg));
}

function validate() {
    var msg = {keyword: "VALIDATE", data: {}};
    var responses = [];
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) responses.push({id: map.edges[i].id, correct: map.edges[i].correct});
    }
    msg.data.edges = responses;
    ws.send(JSON.stringify(msg));
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
