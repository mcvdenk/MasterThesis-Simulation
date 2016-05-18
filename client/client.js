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
        color: {
            border: "#554600",
            background: "#D4C26A",
            highlight: {
                border: "#554600",
                background: "#AA9739"
            }
        },
        font: {
            color: "#554600"
        }
    },
    edges: {
        arrows: {
            to: {enabled: true}
        },
        color: {
            color: "#554600",
            highlight: "#554600"
        },
        font: {
            color: "#554600"
        }
    },
    interaction: {
        selectable: true,
        dragNodes: true
    }
//    physics : {barnesHut: {avoidOverlap: 1}}
};
var show_undo = false;
var question = "";
var answer = "";
var fc_id = "";

ws.onopen = function (event) {
    document.getElementById("instructions").innerHTML = "<p>Je kunt hier inloggen door een al bestaande gebruikersnaam in te vullen, of een nieuw account aanmaken door een nieuwe gebruikersnaam in te vullen. Als dit niet lukt, stuur dan een email naar <a href='mailto:mvdenk@gmail.com'>mvdenk@gmail.com</a>.</p>";
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
            help();
            break;
        case "LEARNED_FLASHMAP-RESPONSE":
            coloured_map = colourise_progress(msg.data);
            show_map(coloured_map);
            break;
        case "LEARNED_FLASHCARDS-RESPONSE":
            show_flashcard_progress(msg.data);
            break;
        case "LEARN-RESPONSE(fm)":
            show_map(flashmap(msg.data, msg.time_up));
            break;
        case "LEARN-RESPONSE(fc)":
            show_card(msg.data, msg.time_up);
            break;
        case "NO_MORE_FLASHEDGES":
            done_learning();
            break;
        case "READ_SOURCE-REQUEST":
            prompt_source_request(msg.data);
            break;
        case "DESCRIPTIVES-REQUEST":
            ask_descriptives();
            break;
        case "TEST-REQUEST":
            test(msg.data);
            break;
    }
}

function ask_descriptives() {
    document.getElementById("instructions").innerHTML = "Voer hier je algemene gegevens in";
    document.getElementById(cont).innerHTML = " \
        <h3> Wat is je geslacht? </h3> \
        <table> \
        <tr> \
        <td> <input type='radio' name='gender' value='male' checked/> </td><td> Mannelijk </td> \
        </tr><tr> \
        <td> <input type='radio' name='gender' value='female' /> </td><td> Vrouwelijk </td> \
        </tr><tr> \
        <td> <input type='radio' name='gender' value='other' /> </td><td> Anders </td> \
        </tr> \
        </table> \
        <h3> Wat is je geboortedatum? </h3> \
        <input type='text' name='birthdate' id='birthdate' /> <br /> (dd-mm-yyyy) \
        <h3> Wat is de code vermeld op de toezeggingsverklaring? </h3> \
        <input type='text' name='code' id='code' /> <br /> \
        <a href='#' onClick='send_descriptives()'>Verstuur</a> \
        <div id='invalid' />";
}

function send_descriptives() {
    msg = {keyword: "DESCRIPTIVES-RESPONSE", data: {gender: "male", birthdate: 0}};
    var genderbuttons = document.getElementsByName('gender');
    for (i = 0; i < genderbuttons.length; i++) {
        if (genderbuttons[i].checked) msg.data.gender = genderbuttons[i].value;
        break;
    }
    msg.data.code = document.getElementById('code').value;
    datestr = document.getElementById('birthdate').value;
    var parts = datestr.split("-");
    if (parts.length != 3
            || parseInt(parts[2], 10) < 1900 || parseInt(parts[2], 10) > new Date().getFullYear()
            || parseInt(parts[1], 10) < 1    || parseInt(parts[1], 10) > 12
            || parseInt(parts[0], 10) < 1    || parseInt(parts[0], 10) > 31) {
       document.getElementById('invalid').innerHTML = "INVALID DATE"
       return
    }
    var date = new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    msg.data.birthdate = date.getTime();
    if (date.getTime() > new Date().getTime() || msg.data.birthdate == 0) document.getElementById(cont).innerHTML += "INVALID DATE";
    else ws.send(JSON.stringify(msg));
}

function test(data) {
    document.getElementById("instructions").innerHTML = "<p> Probeer de onderstaande toets zo goed mogelijk in te vullen. Je mag vragen overslaan als je de antwoorden niet weet. Als dit de eerste toets is en je hebt de papieren versie al gemaakt kun je de toets overslaan door hem leeg te versturen. </p>"
    document.getElementById(cont).innerHTML = ""
    for (i = 0; i < data.flashcards.length; i++) {
        document.getElementById(cont).innerHTML += " \
            <h3>" + data.flashcards[i].question + "</h3> \
            <textarea rows='4' cols='50' class='test' name='flashcard' id='flashcard" + data.flashcards[i].id + "' />";
    }
    for (i = 0; i < data.items.length; i++) {
        document.getElementById(cont).innerHTML += " \
            <h3>" + data.items[i].question + "</h3> \
            <textarea rows='4' cols='50' class='test' name='item' id='item" + data.items[i].id + "' />";
    }
    document.getElementById(cont).innerHTML += "<br /><a href='#' onClick='send_test_results()'>Verstuur</a>";
}

function send_test_results() {
    msg = {keyword: "TEST-RESPONSE", data: {flashcards : [], items : []}}
    var flashcards = document.getElementsByName('flashcard');
    for (i = 0; i < flashcards.length; i++) {
        msg.data.flashcards.push({id : flashcards[i].id.slice(9), answer : flashcards[i].value});
    }
    var items = document.getElementsByName('item');
    for (i = 0; i < items.length; i++) {
        msg.data.items.push({id : items[i].id.slice(4), answer : items[i].value});
    }
    ws.send(JSON.stringify(msg));
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
    container.style= "height:100%";

    // initialize your network!
    network = new vis.Network(container, graph, options);

    network.on('click', function(properties) {
        for (i=0; i < map.edges.length; i++) {
            if ('correct' in map.edges[i] && properties.nodes[0] == map.edges[i].to) {
                map.edges[i].correct = !map.edges[i].correct;
                if (map.edges[i].correct) {
                    edges.update([{ id: map.edges[i].id, color: {color: "#0F640F", highlight: "#0F640F"}, font: {color: "#0F640F"}}])
                    nodes.update([{ id : map.edges[i].to, color: {border: "#0F640F", background: "#55AA55", highlight: {border: "#0F640F", background: "#55AA55"}}, font: {color: "#0F640F"}}]);
                }
                else {
                    edges.update([{ id: map.edges[i].id, color: {color: "#550000", highlight: "#550000"}, font: {color: "#550000"}}])
                    nodes.update([{ id : map.edges[i].to, color: {border: "#550000", background: "#AA3939", highlight: {border: "#550000", background: "#AA3939"}}, font: {color: "#550000"}}]);
                }
            }
        }
    });
}

function show_menu() {
    document.getElementById("instructions").innerHTML = "";
    document.getElementById(cont).innerHTML = "";
    document.getElementsByTagName("nav")[0].style.visibility = "visible";
}

function colourise_progress(data) {
    return data
}

function show_flashcard_progress(data) {
    document.getElementById(cont).innerHTML = " \
        <p> Klaar om nu geleerd te worden: " + data.due +" </p> \
        <p> Nog niet gezien: " + data.not_seen + " </p> \
        <p> Nieuw: " + data.new + " </p> \
        <p> Lerende: " + data.learning + " </p> \
        <p> Geleerd: " + data.learned + " </p>"
}

function show_card(data, time_up) {
    document.getElementById("instructions").innerHTML = "<p> Probeer de onderstaande vraag te beantwoorden </p>";
    if (time_up) document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd!! </p>";
    question = data.question;
    answer = data.answer;
    fc_id = data.id;
    document.getElementById(cont).innerHTML = question;
    if (show_undo) document.getElementById("panel").innerHTML = "<a href='#' onclick='undo()'> Undo </a> <a href='#' onclick='show_answer_fc()'> Toon antwoord </a>";
    else document.getElementById("panel").innerHTML = "<a href='#' onclick='show_answer_fc()'> Toon antwoord </a>";
}

function show_answer_fc() {
    document.getElementById("instructions").innerHTML = "<p> Geef aan of het door jou bedachte antwoord correct of incorrect was </p>";
    document.getElementById(cont).innerHTML += "<br><br>" + answer;
    document.getElementById("panel").innerHTML = "<a href='#' onclick='validate_fc(false)'> Incorrect </a><a href='#' onclick='validate_fc(true)'> Correct </a";
}

function flashmap(data, time_up) {
    document.getElementById("instructions").innerHTML = "<p> Probeer te bedenken wat er in de oranje lege velden moet komen te staan. </p>";
    if (time_up) document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd!! </p>";
    question = data.question;
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
    document.getElementById("instructions").innerHTML = "<p> Geef aan of jouw antwoord goed of fout was. Als je op de velden klikt, veranderen ze van kleur, waarbij groen een goed antwoord is en rood een fout antwoord. </p>";
    var index
    for (i = 0; i < map.edges.length; i++) {
        if (map.edges[i].learning) {
            for (j=0;j < map.nodes.length; j++) {
                if (map.edges[i].to == map.nodes[j].id) index = j;
            }
            edges.update([{ id: map.edges[i].id, color: {color: "#0F640F", highlight: {color: "#0F640F"}}, font: {color: "#0F640F"}}])
            nodes.update([{id: map.edges[i].to, color: {border: "#0F640F", background : "#55AA55"}}]);
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

function help() {
    document.getElementById(cont).innerHTML = "<p>Dankjewel voor het meedoen aan het experiment. Hier kun je iedere dag met de flashcards oefenen om je zo goed voor te kunnen bereiden op de toets over Nederlandse literatuur uit de 17de eeuw.</p><p>Het flashcard systeem is het meest effectief als je iedere dag tijd eraan besteed. Bovendien krijg je de waardebon alleen als je iedere dag het systeem gebruikt voor 15 minuten, of totdat de flashcards voor die dag op zijn. Op het moment dat je op een bepaalde dag klaar bent krijg je vanzelf een popup die aangeeft dat je klaar bent voor vandaag.</p>";
}

function logout() {
    ws.close();
    location.reload();
}
