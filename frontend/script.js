const API_URL = "http://localhost:8010/ask"

let session_id = crypto.randomUUID()

const chatBox = document.getElementById("chatBox")

/* ---------------- MESSAGE RENDER ---------------- */

function addMessage(text, type){

    const msg = document.createElement("div")

    msg.className = "message " + type

    if(type === "bot"){
        msg.innerHTML = marked.parse(text)
    }else{
        msg.innerText = text
    }

    chatBox.appendChild(msg)

    chatBox.scrollTop = chatBox.scrollHeight
}


/* ---------------- SEND QUERY ---------------- */

async function sendQuery(){

    const input = document.getElementById("queryInput")
    const query = input.value.trim()

    if(!query) return

    addMessage(query,"user")
    input.value=""

    addMessage("Thinking...","bot")

    const use_context = document.getElementById("contextToggle").checked

    const url = `${API_URL}?query=${encodeURIComponent(query)}&session_id=${session_id}&use_context=${use_context}`

    const res = await fetch(url)
    const data = await res.json()

    chatBox.lastChild.remove()

    addMessage(data.answer,"bot")

    loadSessions()
}


/* ---------------- NEW SESSION ---------------- */

document.getElementById("newSessionBtn").onclick = () => {

    session_id = crypto.randomUUID()

    chatBox.innerHTML = ""

    addMessage("New session started.","bot")

    setTimeout(()=>{
        chatBox.lastChild?.remove()
    },1500)
}


/* ---------------- LOAD ONE SESSION ---------------- */

async function loadSession(sessionId){

    session_id = sessionId

    const res = await fetch(`http://localhost:8010/session/${sessionId}`)
    const data = await res.json()

    chatBox.innerHTML = ""

    data.messages.forEach(msg => {

        // MAP backend roles → frontend classes
        let role = msg.role === "assistant" ? "bot" : "user"

        addMessage(msg.content, role)

    })

}


/* ---------------- LOAD SIDEBAR SESSIONS ---------------- */

async function loadSessions(){

    const res = await fetch("http://localhost:8010/sessions")
    const data = await res.json()

    const list = document.getElementById("sessionsList")
    list.innerHTML = ""

    data.sessions.forEach(s => {

        const div = document.createElement("div")

        div.className = "session-item"
        div.innerText = s.title

        div.onclick = () => loadSession(s.session_id)

        list.appendChild(div)

    })
}


/* ---------------- PAGE LOAD ---------------- */

window.onload = () => {
    loadSessions()
}



div.onclick = () => {
    document.querySelectorAll(".session-item").forEach(el => el.classList.remove("active"))
    div.classList.add("active")
    loadSession(s.session_id)
}

