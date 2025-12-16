
function connect() {
    const ip = document.getElementById("serverIp").value.trim()
    const user_name = document.getElementById("username").value.trim()
    const port = document.getElementById("serverPort").value.trim()
    socket = new WebSocket(`ws://${ip}:${port}`)
    socket.onopen = () => {
        socket.send(JSON.stringify({ action: 'login', user: user_name }))
        connectionPage.style.display = "none"
        chatPage.style.display = "flex"
        const status_text = document.getElementById("status_text")
        status_text.textContent = "Connecté en tant que " + user_name
    }
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.action === 'message') {
            add_message(data.message);
        } else if (data.action === 'rooms') {
            display_rooms(data.rooms)
        }
    }
}

function display_rooms(rooms) {
    rooms.forEach((room) => {
        add_room(room)
    })

}


function send_message() {
    const message = document.getElementById("messageInput").value
    socket.send(JSON.stringify({ action: 'send_message', message: message }))
}

function add_message(message) {
    const message_input = document.getElementById("messageInput")
    const new_message = document.createElement("div")
    const message_container = document.getElementById("messagesContainer")
    new_message.textContent = message
    message_container.appendChild(new_message)
    message_container.scrollTop = message_container.scrollHeight
    message_input.value = ""
}

function add_room(room) {
    const room_list = document.getElementById("roomList")
    const room_element = document.createElement('div')
    const rooms = document.getElementsByClassName("room-item")
    if (Array.from(rooms).some(item => item.textContent === room)) {
        alert("Ce salon existe déjà")
    }
    else {
        room_element.textContent = room
        room_element.onclick = () => join_room(room)
        room_element.className = "room-item"
        room_list.appendChild(room_element)
    }
}

function create_room(room) {
    const new_room_name = document.getElementById('newRoomName').value.trim()
    if (new_room_name === "") {
        alert("Le nom du salon ne peut pas être vide")
        return
    }
        socket.send(JSON.stringify({ action: 'create_room', room: new_room_name }))
        document.getElementById('newRoomName').value = ""
        add_room(new_room_name)
    }

function join_room(room) {
    const container = document.getElementById("messagesContainer")
    container.innerHTML = ""
    const current_room_name = document.getElementById("currentRoomName")
    current_room_name.textContent = room
    socket.send(JSON.stringify({ action: 'join_room', room: room }))
}
function disconnect() {
    socket.close()
    chatPage.style.display = "none"
    connectionPage.style.display = "block"

}