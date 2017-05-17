//setup

var page = require('webpage').create();
page.viewportSize = { width: 1024, height: 768};
page.content = '<html>\
        <body>\
            <div id="wrapper">\
                <header>\
                    <nav> <a><a><a><a><a> </nav>\
                    <div id="instructions"></div>\
                </header>\
            <div id="mycontainer"></div>\
        <footer>\
            <div id="panel"></div>\
        </footer>\
        </body>\
    </html>';

var wrapper = page.evaluate(function () {
    return document.getElementById('wrapper');
});

var instructions = page.evaluate(function () {
    return document.getElementById('instructions');
});

var cont = page.evaluate(function () {
    return document.getElementById('mycontainer');
});

var panel = page.evaluate(function () {
    return document.getElementById('panel');
});

page.onError = function (msg, trace) {
    console.log(msg);
    trace.forEach(function(item) {
        console.log('  ', item.file, ':', item.line);
    });
};

var logged_in = false;

var users = [];

var current_user = 0

for (i = 0; i<100; i++) {
    users[i] = "sim_user_"+i;
}

//simulation

var ws = new WebSocket("ws://128.199.49.170:5678");

ws.onopen = function (event) {
    var msg = {
        keyword: "AUTHENTICATE-REQUEST",
        data: {
            name: users[current_user],
            browser: navigator.platform
        }
    }
    ws.send(JSON.stringify(msg));
}

ws.onmessage = function (event) {
    var msg = JSON.parse(event.data);
    console.log(msg.keyword);
    logged_in = true;

    switch(msg.keyword) {
        case "AUTHENTICATE-RESPONSE":
            ws.close();
            phantom.exit();
            break;
        case "LEARNED_ITEMS-RESPONSE":
            ws.close();
            phantom.exit();
            break;
        case "LEARN-RESPONSE":
            ws.close();
            phantom.exit();
            break;
        case "NO_MORE_INSTANCES":
            ws.close();
            phantom.exit();
            break;
        case "READ_SOURCE-REQUEST":
            ws.close();
            phantom.exit();
            break;
        case "DESCRIPTIVES-REQUEST":
            ask_descriptives();
            send_descriptives();
            break;
        case "TEST-REQUEST":
            ws.close();
            phantom.exit();
            break;
        case "QUESTIONNAIRE-REQUEST":
            ws.close();
            phantom.exit();
            break;
        case "DEBRIEFING-REQUEST":
            ws.close();
            phantom.exit();
            break;
    }
}

function ask_descriptives() {
    panel.innerHTML = "";
    instructions.innerHTML = "Voer hier je algemene gegevens in. Ben je je code kwijt? Stuur dan even een email met je gebruikersnaam en echte naam naar mvdenk@gmail.com";
    cont.innerHTML = " \
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
        <input type='text' name='birthdate' id='birthdate' value='"+current_user%30+"-01-2000'/> <br /> (dd-mm-yyyy) \
        <h3> Wat is de code vermeld op de toezeggingsverklaring? </h3> \
        <input type='text' name='code' id='code' value='"+current_user"' /> <br /> \
        <a href='#'>Verstuur</a> \
        <div id='invalid' />";
}

function send_descriptives() {
    msg = {keyword: "DESCRIPTIVES-RESPONSE", data: {gender: "male", birthdate: 0}};
    var genderbuttons = page.evaluate (function () {
        return document.getElementsByName('gender');
    });
    for (i = 0; i < genderbuttons.length; i++) {
        if (genderbuttons[i].checked) msg.data.gender = genderbuttons[i].value;
    }
    msg.data.code = page.evaluate (function () {
        return document.getElementById('code').value;
    });
    datestr = page.evaluate (function () {
        return document.getElementById('birthdate').value;
    });
    var parts = datestr.split("-");
    if (parts.length != 3
            || parseInt(parts[2], 10) < 1900 || parseInt(parts[2], 10) > new Date().getFullYear()
            || parseInt(parts[1], 10) < 1    || parseInt(parts[1], 10) > 12
            || parseInt(parts[0], 10) < 1    || parseInt(parts[0], 10) > 31) {
       return
    }
    msg.data.birthdate = new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    if (msg.data.birthdate > new Date()) cont.innerHTML += "INVALID DATE";
    else ws.send(JSON.stringify(msg));
}
