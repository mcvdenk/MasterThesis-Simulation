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
    },
    physics : {barnesHut: {avoidOverlap: 1}}
};
var show_undo = false;
var question = "";
var answer = "";
var fc_id = "";

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
            if (msg.data.success = "NEW_USERNAME") ask_descriptives();
            else show_menu();
            break;
        case "LEARNED_ITEMS-RESPONSE":
            coloured_map = colourise_progress(msg.data);
            show_map(coloured_map);
            break;
        case "LEARN-RESPONSE(fm)":
            show_map(flashmap(msg.data));
            break;
        case "LEARN-RESPONSE(fc)":
            show_card(msg.data);
            break;
        case "NO_MORE_FLASHEDGES":
            done_learning();
            break;
        case "READ_SOURCE-REQUEST":
            prompt_source_request(msg.data);
            break;
    }
}

function ask_descriptives() {
    document.getElementById(cont).innerHTML = "<object type='text/html' data='descriptives.html' />"
}

function send_descriptives() {
    msg = {keyword: "PROVIDE_DESCRIPTIVES", data: {gender: "male", birthdate: 0}};
    var genderbuttons = document.getElementsByName('gender');
    for (i = 0; i < genderbuttons.length; i++) {
        if (genderbuttons[i].checked) msg.data.gender = genderbuttons[i].value;
        break;
    }
    datestr = document.getElementsByName('birthdate').value;
    var parts = datestr.split("-");
    if (parts.length != 3
            || parseInt(parts[2], 10) < 1900 || parseInt(parts[2], 10) > new Date().getFullYear()
            || parseInt(parts[1], 10) < 1    || parseInt(parts[1], 10) > 12
            || parseInt(parts[0], 10) < 1    || parseInt(parts[0], 10) > 31) {
       document.getELementById(cont).innerHTML += "INVALID DATE"
       return
    }
    var date = new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    msg.data.birthdate = date.getTime();
    if (date.getTime() > new Date().getTime() || msg.data.birthdate == 0) document.getElementById(cont).innerHTML += "INVALID DATE";
    else ws.send(JSON.stringify(msg));
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
    container.style = "height:80%"; 

    // initialize your network!
    network = new vis.Network(container, graph, options);
    setTimeout(network.stopSimulation(), 6000);

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

function show_card(data) {
    question = data.question;
    answer = data.answer;
    fc_id = data.id;
    document.getElementById(cont).innerHTML = question;
    if (show_undo) document.getElementById("panel").innerHTML = "<a href='#' onclick='undo()'> Undo </a> <a href='#' onclick='show_answer_fc()'> Toon antwoord </a>";
    else document.getElementById("panel").innerHTML = "<a href='#' onclick='show_answer_fc()'> Toon antwoord </a>";
}

function show_answer_fc() {
    document.getElementById(cont).innerHTML += "<br><br>" + answer;
    document.getElementById("panel").innerHTML = "<a href='#' onclick='validate_fc(false)'> Incorrect </a><a href='#' onclick='validate_fc(true)'> Correct </a";
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
    if (show_undo) document.getElementById("panel").innerHTML = "<a href='#' onclick='undo()'> Undo </a> <a href='#' onclick='show_answer_fm()'> Toon antwoord </a>";
    else document.getElementById("panel").innerHTML = "<a href='#' onclick='show_answer_fm()'> Toon antwoord </a>";
    return map;
}

function show_answer_fm() {
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
    document.getElementById("panel").innerHTML = "<a href='#' onclick='validate_fm()'> Volgende </a>";
}

function view_learned() {
    var msg = {keyword: "LEARNED_ITEMS-REQUEST", data: {}};
    ws.send(JSON.stringify(msg));
}

function undo() {
    var msg = {keyword: "UNDO", data: {}};
    ws.send(JSON.stringify(msg));
    show_undo = false;
}

function validate_fc(correct) {
    var msg = {keyword: "VALIDATE(fc)", data: {}};
    msg.data.id = fc_id;
    msg.data.correct = correct;
    ws.send(JSON.stringify(msg));
    show_undo = true;
}

function validate_fm() {
    var msg = {keyword: "VALIDATE(fm)", data: {}};
    var responses = [];
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) responses.push({id: map.edges[i].id, correct: map.edges[i].correct});
    }
    msg.data.edges = responses;
    ws.send(JSON.stringify(msg));
    show_undo = true;
}

function learn() {
    var msg = {
        keyword: "LEARN-REQUEST",
        data: {}
    }
    ws.send(JSON.stringify(msg));
}

function done_learning() {
    alert("Je bent klaar voor nu, kom morgen terug voor nieuwe flashcards.");
}

function prompt_source_request(data) {
    document.getElementById(cont).innerHTML = "Heb je paragraaf " + data.source + " al gelezen? Zo nee, lees deze dan nu.";
    document.getElementById("panel").innerHTML = "<a href='#' onclick='confirm_source(" + data.source + ")'> Gelezen </a>";
}

function confirm_source(source_) {
    var msg = {keyword: "READ_SOURCE-RESPONSE", data: { source : source_ }};
    ws.send(JSON.stringify(msg));
}

function logout() {
    ws.close();
    location.reload();
}
