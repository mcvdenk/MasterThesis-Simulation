var uname = "";
var cont = "mycontainer";
var ws = new WebSocket("ws://128.199.49.170:5678");
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
var logged_in = false;

ws.onopen = function (event) {
    document.getElementById("instructions").innerHTML = "<p>Je kunt hier inloggen door een al bestaande gebruikersnaam in te vullen, of een nieuw account aanmaken door een zelbedachte, nieuwe gebruikersnaam in te vullen. Als dit niet lukt, stuur dan een email naar <a href='mailto:mvdenk@gmail.com'>mvdenk@gmail.com</a>.</p>";
    document.getElementById(cont).style.visibility = "visible";
    document.getElementById("username").focus();
}

ws.onclose = function(event) {
    if (logged_in) {
        if (!alert("Connection lost.")) window.location.reload();
    }
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
    if (uname != "questionnaire") logged_in = true;

    switch(msg.keyword) {
        case "ACTIVE_SESSIONS":
            logged_in = false;
            break;
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
            show_map(flashmap(msg.data, msg.time_up, msg.successful_days));
            break;
        case "LEARN-RESPONSE(fc)":
            show_card(msg.data, msg.time_up, msg.successful_days);
            break;
        case "NO_MORE_INSTANCES":
            done_learning(msg.data, msg.successful_days);
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
        case "QUESTIONNAIRE-REQUEST":
            questionnaire(msg.data);
            break;
        case "DEBRIEFING":
            debriefing();
            break;
    }
}

function ask_descriptives() {
    document.getElementById("panel").innerHTML = "";
    document.getElementById("instructions").innerHTML = "Voer hier je algemene gegevens in. Ben je je code kwijt? Stuur dan even een email met je gebruikersnaam en echte naam naar mvdenk@gmail.com";
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
    document.getElementById("panel").innerHTML = "";
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

function questionnaire(data) {
    document.getElementById("panel").innerHTML = "";
    document.getElementById("instructions").innerHTML = "<p>Hieronder staan stellingen waarbij je aan kunt geven of je het er mee eens of oneens bent. Dit is voor mij om te kunnen bepalen of je het flashcard systeem nuttig vond en makkelijk te gebruiken.</p>";
    container = document.getElementById(cont);
    container.innerHTML = "";
    container_text = "";
    var form = "";
    for (i = 0; i < data.perceived_usefulness.length; i++) {
        if (data.perceived_usefulness[i].formulation == "positive") form = "+";
        else form = "-";
        item_text = " \
            <h3>" + data.perceived_usefulness[i].item + "</h3> \
            <table style='text-align:center;'> \
                <tr> \
                    <td>Zeer mee oneens</td><td>Mee oneens</td><td>Noch mee eens, <br />noch mee oneens</td><td>Mee eens</td><td>Zeer mee eens</td> \
                </tr><tr>";
        for (j=-2; j <= 2; j++) {
            item_text += "<td><input type='radio' class='useful' name='useful"+form+data.perceived_usefulness[i].id+"' value='"+j+"' /></td>";
        }
        item_text += "</tr></table>";
        container_text += item_text;
    }
    for (i = 0; i < data.perceived_ease_of_use.length; i++) {
        if (data.perceived_ease_of_use[i].formulation == "positive") form = "+";
        else form = "-";
        item_text = " \
            <h3>" + data.perceived_ease_of_use[i].item + "</h3> \
            <table style='text-align:center;'> \
                <tr> \
                    <td>Zeer mee oneens</td><td>Mee oneens</td><td>Noch mee eens, <br />noch mee oneens</td><td>Mee eens</td><td>Zeer mee eens</td> \
                </tr><tr>";
        for (j=-2; j <= 2; j++) {
            item_text += "<td><input type='radio' class='ease' name='ease"+form+data.perceived_ease_of_use[i].id+"' value='"+j+"' /></td>";
        }
        item_text += "</tr></table>"
        container_text += item_text;
    }
    container_text += " \
        <h3>Wat vond je goed aan het flashcard systeem?</h3> \
        <textarea rows='4' cols='50' class='questionnaire' name='goed' id='goed'></textarea> \
        <h3>Wat zijn eventuele verbeteringen die gemaakt zouden kunnen worden?</h3> \
        <textarea rows='4' cols='50' class='questionnaire' name='kan_beter' id='kan_beter'></textarea>";
    container_text += "<br /><p>Als je bereid bent om later ge&iuml;nterviewd te worden over het flashcard systeem, vul dan hieronder je emailadres in.</p> \
                       <input type='text' id='email'/>";
    container_text += "<br /><a href='#' onClick='send_questionnaire_results()'>Verstuur</a>";
    container.innerHTML = container_text;
}

function send_questionnaire_results() {
    msg = {keyword: "QUESTIONNAIRE-RESPONSE", data: {perceived_usefulness : { positive : [], negative : []}, perceived_ease_of_use : { positive : [], negative : []}, goed: "", kan_beter: "", email: ""}}
    var useful = document.getElementsByClassName('useful');
    for (i = 0; i < useful.length; i++) {
        if (useful[i].checked) {
            if (useful[i].name.charAt(6) == '+') msg.data.perceived_usefulness.positive.push({id: useful[i].name.slice(7), value: useful[i].value});
            else msg.data.perceived_usefulness.negative.push({id: useful[i].name.slice(7), value: useful[i].value});
        }    
    }
    var ease = document.getElementsByClassName('ease');
    for (i = 0; i < ease.length; i++) {
        if (ease[i].checked) {
            console.log(ease[i].name);
            if (ease[i].name.charAt(4) == '+') msg.data.perceived_ease_of_use.positive.push({id: ease[i].name.slice(5), value: ease[i].value});
            else msg.data.perceived_ease_of_use.negative.push({id: ease[i].name.slice(5), value: ease[i].value});
        }    
    }
    msg.data.goed = document.getElementById("goed").value;
    msg.data.kan_beter = document.getElementById("kan_beter").value;
    msg.data.email = document.getElementById("email").value;
    console.log(JSON.stringify(msg));
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
    document.getElementById("panel").innerHTML = "";
    return data
}

function show_flashcard_progress(data) {
    document.getElementById("panel").innerHTML = "";
    document.getElementById(cont).innerHTML = " \
        <p> Klaar om nu geleerd te worden: " + data.due +" </p> \
        <p> Nog niet gezien: " + data.not_seen + " </p> \
        <p> Nieuw: " + data.new + " </p> \
        <p> Lerende: " + data.learning + " </p> \
        <p> Geleerd: " + data.learned + " </p>"
}

function show_card(data, time_up, successful_days) {
    document.getElementById("instructions").innerHTML = "<p> Probeer de onderstaande vraag te beantwoorden </p>";
    if (time_up) {
        if (successful_days < 6) {
            document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd, nog "+ (6 - successful_days).toString() +" dagen te gaan. </p>";
        }
        if (successful_days == 6) {
            document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd, kom morgen terug voor de laatste kennistoets en de enquete. </p>";
        }
    }
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

function flashmap(data, time_up, successful_days) {
    document.getElementById("instructions").innerHTML = "<p> Probeer te bedenken wat er in de oranje lege velden moet komen te staan. </p>";
    if (time_up) {
        if (successful_days < 6) {
            document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd, nog "+ (6 - successful_days).toString() +" dagen te gaan. </p>";
        }
        if (successful_days == 6) {
            document.getElementById("instructions").innerHTML = "<p style='color:red;'> Je hebt vandaag 15 minuten geleerd, kom morgen terug voor de laatste kennistoets en de enquete. </p>";
        }
    }
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

function done_learning(data, successful_days) {
    if (data.source != "") {
        if (successful_days < 6) document.getElementById(cont).innerHTML = "<p>Er zijn geen flashcards meer behorende tot de paragrafen die je gelezen hebt. Je bent daarmee klaar voor vandaag, en je hebt nog "+ (6 - successful_days).toString() +" dagen te gaan. Als je paragraaf " + data.source + " gelezen kun je verder met de volgende flashcards.</p><a href='#' onclick='confirm_source(\"" + data.source + "\")'> Verder </a>";
        else if (successful_days == 6) document.getElementById(cont).innerHTML = "<p>Er zijn geen flashcards meer behorende tot de paragrafen die je gelezen hebt. Je bent daarmee klaar voor vandaag, kom morgen terug voor de laatste kennistoets en de enquete. Als je paragraaf " + data.source + " gelezen kun je verder met de volgende flashcards.</p><a href='#' onclick='confirm_source(\"" + data.source + "\")'> Verder </a>";
        else document.getElementById(cont).innerHTTML = document.getElementById(cont).innerHTML = "<p>Er zijn geen flashcards meer behorende tot de paragrafen die je gelezen hebt. Je bent daarmee klaar voor vandaag. Als je paragraaf " + data.source + " gelezen kun je verder met de volgende flashcards.</p><a href='#' onclick='confirm_source(\"" + data.source + "\")'> Verder </a>";
    }
    else {
        if (successful_days < 6) document.getElementById(cont).innerHTML ="<p>Er zijn geen flashcards meer voor nu, en daarmee ben je klaar voor vandaag. Je hebt nog "+ (6 - successful_days).toString() +" dagen te gaan.</p>";
        else if (successful_days == 6) document.getElementById(cont).innerHTML ="<p>Er zijn geen flashcards meer voor nu, en daarmee ben je klaar voor vandaag. Kom morgen terug voor de laatste kennistoets en de enquete.</p>";
        else document.getElementById(cont).innerHTML ="<p>Er zijn geen flashcards meer voor nu, en daarmee ben je klaar voor vandaag.</p>";
    }
    document.getElementById("panel").innerHTML = "";
}

function prompt_source_request(data) {
    document.getElementById(cont).innerHTML = "Heb je paragraaf " + data.source + " al gelezen? Zo nee, lees deze dan nu.";
    document.getElementById("panel").innerHTML = "<a href='#' onclick='confirm_source(\"" + data.source + "\")'> Gelezen </a>";
}

function confirm_source(source_) {
    var msg = {keyword: "READ_SOURCE-RESPONSE", data: { source : source_ }};
    ws.send(JSON.stringify(msg));
}

function help() {
    document.getElementById("instructions").innerHTML = "";
    document.getElementById("panel").innerHTML = "";
    document.getElementById(cont).innerHTML = "<p>Dankjewel voor het meedoen aan het experiment. Hier kun je iedere dag met de flashcards oefenen om je zo goed voor te kunnen bereiden op de toets over Nederlandse literatuur uit de 17de eeuw.</p><p>Het flashcard systeem is het meest effectief als je iedere dag tijd eraan besteed. Bovendien krijg je de waardebon alleen als je iedere dag het systeem gebruikt voor 15 minuten, of totdat de flashcards voor die dag op zijn. Op het moment dat je op een bepaalde dag klaar bent krijg je vanzelf een popup die aangeeft dat je klaar bent voor vandaag.</p>";
}

function debriefing() {
    document.getElementById("instructions").innerHTML = "";
    document.getElementById("panel").innerHTML = "";
    document.getElementById(cont).innerHTML = "<p>Hartelijk bedankt voor het meedoen aan het onderzoek, en gefeliciteerd met de waardebon. Je zult deze binnenkort van je leraar ontvangen als je de toezeggingsverklaring hebt ingeleverd. Verder staat het je vrij om gebruik te blijven maken van het flashcard systeem, het is goed om de kennis die je geleerd hebt vers te houden tot de toets. De resultaten van dit onderzoek kun je op verzoek ter inzage bij mij aanvragen. Als je net je email adres hebt ingevuld krijg je binnenkort een mail om een datum in te plannen voor het interview. Verder wens ik je nog veel succes voor dit vak. Als je nog vragen hebt kun je me altijd nog een email sturen (mvdenk@gmail.com).</p><a href='#' onclick='acc_debriefing()'>Gelezen</a>";
}

function acc_debriefing() {
    ws.send(JSON.stringify({keyword: "DEBRIEFING-RESPONSE", data: {}}));
}

function logout() {
    logged_in = false;
    ws.close();
    location.reload();
}
