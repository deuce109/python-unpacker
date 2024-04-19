// import { io } from "https://cdn.socket.io/4.7.4/socket.io.esm.min.js";
// const { io } = require("socket.io-client");
let selectedLibrary = null

let selectedFiles = []

let debug = false

let progressContainer = null

async function isDebug() {
    const response = await fetch("/debug")
    const response_text = await response.text()
    debug = response_text.trim().toLowerCase() === "true"
}

isDebug()

const socket = io("/")

function log(message, error=false) {
    if (debug) {
        if (error) {
            console.error(message)
        } else {
            console.log(message)
        }
    }
}

socket.on("connect_error", (err) => {
        log(`connect_error due to ${err.message}`, true);
  });

socket.on("connect", () => {    
    log("Connected")
})

socket.connect()

function getUUID() {
    let uuid = ""
    if (crypto.randomUUID)
        uuid = crypto.randomUUID()
    else
        uuid = "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
      );
      return uuid
}

function createProgressBar(file_id, file) {

    if (!progressContainer)
        progressContainer = document.getElementById("progress-bar-container")

    const wrapper = document.createElement("div")

    wrapper.className = "progress-bar-wrapper"

    const label = document.createElement("label")
    label.setAttribute("for", `progress-${file_id}`)
    label.innerText = `${file.name}`

    const bar = document.createElement("progress", {
        id: `progress-${file_id}`,
        value: "0",
        max: "100"
    })

    bar.setAttribute("id", `progress-${file_id}`)
    bar.setAttribute("value", "0")
    bar.setAttribute("max", file.size.toString())

    const percentageText = document.createElement("p")

    percentageText.innerText = "0%"
    percentageText.class = "progress-percentage-text"

    wrapper.appendChild(label)
    wrapper.appendChild(bar)
    wrapper.appendChild(percentageText)
    progressContainer.appendChild(wrapper)
    return {bar, percentageText, wrapper, label}
}

function removeElements(selectedFile) {
    progressContainer.removeChild(selectedFile.wrapper)
}

function loadFilesSocket() {
    const _selectedFiles = document.getElementById("fileSelector").files;

    selectedFiles.forEach(removeElements)

    selectedFiles = []
    for (let i = 0; i < _selectedFiles.length; i++) {
        const file = _selectedFiles[i]
        const uuid = getUUID()
        const {label, bar, percentageText, wrapper} = createProgressBar(uuid, file)
        selectedFiles.push(
            {
                file,
                fileUUID: uuid, 
                bar,
                label, 
                wrapper, 
                percentageText, 
            }
        )
    }

    checkSubmitable()
}

function optionSelected(target) {
    let selected = document.getElementsByClassName("library-option selected")[0]
    if (selected) {
        selected.className = "library-option"
    }
    target.className = "library-option selected"

    selectedLibrary = target.getAttribute('aria-valuetext').toLowerCase()
    checkSubmitable()
}

function checkSubmitable() {
    document.getElementById("submitButton").disabled = !(selectedLibrary && selectedFiles)
}

function _handleUpload(selectedFile) {

    const {fileUUID, percentageText} = selectedFile

    socket.on(`cleanup_finished-${fileUUID}`, () => {

        percentageText.innerText = 'Completed'
        log(`cleanup_finished-${fileUUID}`)
    })

    // socket.on(`initialized-${fileUUID}`, () => {
        
    // })

    processFile(selectedFile)

    // socket.emit("intialize", fileUUID)
}

function toHexString(byteArray) {
    return Array.from(byteArray, function(byte) {
      return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('')
  }

function processFile(selectedFile, fileCursor = 0) {

    const {fileUUID, percentageText, file, bar} = selectedFile
    log(fileCursor)
    log(file.size)
    const blob = file.slice(fileCursor, fileCursor + (10485760))
    let _fileCursor
    var reader = new FileReader();
    reader.onload = function(event) {
      // The file's text will be printed here
      const buffer = event.target.result
        
      _fileCursor = fileCursor + buffer.byteLength

      socket.on(`data_recieved-${fileUUID}`, () => {
            log(`data_recieved-${fileUUID}`)
            bar.setAttribute("value", _fileCursor )
            bar.innerText = Math.floor((file.size / _fileCursor) * 100) + "%" 
            percentageText.innerText = bar.innerText 
            log(_fileCursor === file.size)
            if (_fileCursor === file.size) {
                socket.emit("cleanup", fileUUID, selectedLibrary)
            } else {
                processFile(selectedFile, _fileCursor)
            }
      })

      socket.emit("upload", fileUUID, new Uint8Array(buffer))

    };

    // reader.readAsBinaryString(blob)
    reader.readAsArrayBuffer(blob)

}

async function submitSocket() {
    document.getElementById("submitButton").disabled = true

    await Promise.all(selectedFiles.map(_handleUpload))
}


function init(){
    document.getElementById("submitButton").disabled = true
    if (typeof(window.FileReader)=="undefined") {
        alert("Please use a browser that supports the FileReader API (i.e. newest versions of Firefox, Edge, Chrome)")
    }
}
window.onload = init;