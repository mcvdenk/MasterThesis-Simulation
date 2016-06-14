var uname = "";
var cont = "mycontainer";
var ws = new WebSocket("ws://www.mvdenk.com:6789");

var logged_in = false;

var current_name = "";
var current_id = "";
var current_isFcard = false;

ws.onopen = function (event) {
    document.getElementById("instructions").innerHTML = "<p>Log hier in met de juiste gebruikersnaam. Als dit niet lukt, stuur dan een email naar <a href='mailto:mvdenk@gmail.com'>mvdenk@gmail.com</a>.</p>";
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
    switch(msg.keyword) {
        case "ACTIVE_SESSIONS":
            logged_in = false;
            break;
        case "AUTHENTICATE-RESPONSE":
            if (valid_name(msg.data)) {
                show_menu();
                request_item();
            }
            break;
        case "NO_MORE_ITEMS":
            no_more_items(msg.data);
            break;
        case "ITEM-RESPONSE":
            show_item(msg.data);
            break;
    }
}

function valid_name(data) {
    if (data.success == "NO_SUCH_USER") {
        document.getElementById("instructions").innerHTML = "<p> Dit is helaas niet een geldige gebruikersnaam. Contacteer <a href='mailto:mvdenk@gmail.com'>mvdenk@gmail.com</a> voor meer informatie";
        return false;
    }
    logged_in = true;
    return true;
}

function request_item() {
    msg = {keyword: "ITEM-REQUEST", data: {}};
    ws.send(JSON.stringify(msg));
}

function no_more_items(data) {
    document.getElementById(cont).innerHTML = "<p>Er zijn geen antwoorden meer om na te kijken. Bedankt voor de medewerking.</p>"
}

function show_menu() {
    document.getElementById("instructions").innerHTML = "";
    document.getElementById(cont).innerHTML = "";
    document.getElementsByTagName("nav")[0].style.visibility = "visible";
}

function show_item(data) {
    document.getElementById("instructions").innerHTML = "<p>Geef aan welke elementen er in het antwoord van de leerling aanwezig zijn.</p>";
    document.getElementById(cont).innerHTML = "";
    document.getElementById(cont).innerHTML += "<p>" + data.question + "</p>";
    document.getElementById(cont).innerHTML += "<p><b>" + data.answer + "</b></p>";
    response_model = "<p>";
    for (i = 0; i < data.response_model.length; i++) {
        response_model += "<input type='checkbox' value='" + data.response_model[i] + "' />" + data.response_model[i] + "<br />";
    }
    document.getElementById(cont).innerHTML += response_model + "</p>";
    document.getElementById("panel").innerHTML = "<a href='#' onClick='undo()'>Vorige</a><a href='#' onClick='send_score()'>Volgende</a>";
    current_name = data.name;
    current_id = data.id;
    current_isFcard = data.fcard;
}

function send_score() {
    msg = {keyword: "ITEM_SCORED", data: {fcard: current_isFcard, name: current_name, id: current_id, response_scores: []}};
    response_model = document.getElementsByTagName("input");
    for (i = 0; i < response_model.length; i++) {
        if (response_model[i].checked) msg.data.response_scores.push(response_model[i].value);
    }
    ws.send(JSON.stringify(msg));
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

function logout() {
    logged_in = false;
    ws.close();
    location.reload();
}
