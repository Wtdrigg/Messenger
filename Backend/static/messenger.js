import {io} from "https://cdn.socket.io/4.4.1/socket.io.esm.min.js"
window.submitName = submitName
window.submitMessage = submitMessage

const SOCKET = io();
let user_name;

createEventListeners();

//submits the users name from the entrybox to the server when the funtion is called. This is usally called by clicking the submit name button.
//Users name will be assigned to their socketID and will track when they go online or offline.
export function submitName(){
    user_name = document.getElementById('userbox').value
    let topHolder = document.getElementById('topholder')
    let midHolder = document.getElementById('midholder')
    let botHolder = document.getElementById('bottomholder')

    topHolder.innerHTML = "User-Name: " + user_name
    midHolder.className = 'visible'
    botHolder.className = 'visible'

    let loginObj = {user: user_name, time: new Date().toLocaleString(), message: ":Login"}

    SOCKET.emit('join', loginObj);
}

//sends the message in the entrybox to the server when the function is called. This is usually called on clicking the submit button.
export function submitMessage(){
    let input = document.getElementById('entrybox').value;
    let messageObj = {user: user_name, time: new Date().toLocaleString(), message: input};
    SOCKET.emit('submitmessage', messageObj);
    document.getElementById('entrybox').value = ""
}

//reads the JSON messages received from the server and updates the displaybox HTML to display the user and message for each.
function updateHTML(broadcastContent){
    let outputWindow = document.getElementById('textbox')
    if (broadcastContent['message'] == ":Login"){
        var node = document.createTextNode("--" + broadcastContent['user'] + " has joined the server--")
    }
    else if (broadcastContent['message'] == ':Disconnect'){
        var node = document.createTextNode("--" + broadcastContent['user'] + " has left the server--")
    }
    else{
        var node = document.createTextNode(broadcastContent['user'] + ": " + broadcastContent['message'])
    }
    let lineBreak = document.createElement('br')
    outputWindow.appendChild(node)
    outputWindow.appendChild(lineBreak)
}

//creates all custom event listeners used by
function createEventListeners(){
    //calls when the Enter key is pressed in the username box
    let nameInput = document.getElementById('userbox')
    nameInput.addEventListener('keypress', function(event){
        if (event.key == "Enter"){
            document.getElementById('namebutton').click()
        }
    })

    //calls when the Enter key is pressed in the message box
    let submitInput = document.getElementById('entrybox')
    submitInput.addEventListener('keypress', function(event){
        if (event.key == "Enter"){
            document.getElementById('submitbutton').click()
        }
    })

    //calls when a 'serverbroadcast' event is received from the server
    SOCKET.on('serverbroadcast', function(broadcastContent){
        updateHTML(broadcastContent)
    })

    //calls when a 'clearmessages' event is received from the server
    SOCKET.on('clearmessages', function(){
        document.getElementById('textbox').innerHTML = ""
    })
}

