//var DOTstring = 'dinetwork {1 -- 2; 2 -- 3; 2 -- 4 }';

var container = document.getElementById('container');

var parsedData;

var network;

var data;

var options = {
    nodes: {
        shape: 'box',
        mass: 2
    },
    interaction: {
        dragNodes: true
    },
    layout: {
        hierarchical: {
            enabled: false,
            levelSeparation: 400,
            direction: 'LR',
            sortMethod: 'directed',
            blockShifting: false,
            edgeMinimization: false
        }
    },
    physics: {
        repulsion: {
            springLength: 500
        }
    }
};

var reader = new XMLHttpRequest() || new ActiveXObject('MSXML2.XMLHTTP');

loadFile();

function loadFile() {
    reader.open('get', 'plan.txt', true); 
    reader.onreadystatechange = setupContents;
    reader.send(null);
}

function setupContents() {
    if(reader.readyState==4) {
        parsedData = vis.network.convertDot(reader.responseText);
        data = {
            nodes: parsedData.nodes,
            edges: parsedData.edges
        };
        network = new vis.Network(container, data, options);
    }
}
