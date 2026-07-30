const API_URL = "http://127.0.0.1:8000/api";

// ============================
// ELEMENTOS
// ============================

const filesInput = document.getElementById("files");
const folderInput = document.getElementById("folder");

const btnFiles = document.getElementById("btnFiles");
const btnFolder = document.getElementById("btnFolder");

const uploadButton = document.getElementById("uploadButton");

const selectedFiles = document.getElementById("selectedFiles");
const status = document.getElementById("status");
const result = document.getElementById("result");

const customLimit = document.getElementById("customLimit");

const radios = document.querySelectorAll(
    'input[name="limitType"]'
);

let currentFiles = [];

// ============================
// EVENTOS
// ============================

btnFiles.addEventListener("click", () => {

    filesInput.click();

});

btnFolder.addEventListener("click", () => {

    folderInput.click();

});

filesInput.addEventListener("change", e => {

    currentFiles = [...e.target.files];

    renderFiles();

});

folderInput.addEventListener("change", e => {

    currentFiles = [...e.target.files];

    renderFiles();

});

radios.forEach(radio => {

    radio.addEventListener("change", () => {

        customLimit.disabled =
            radio.value !== "limit" || !radio.checked;

        if(customLimit.disabled){

            customLimit.value="";

        }

    });

});

uploadButton.addEventListener(

    "click",

    uploadFiles

);

// ============================
// MOSTRAR ARCHIVOS
// ============================

function renderFiles(){

    if(currentFiles.length===0){

        selectedFiles.innerHTML=`

            <div class="empty">

                Ningún archivo seleccionado.

            </div>

        `;

        return;

    }

    selectedFiles.innerHTML="";

    currentFiles.forEach(file=>{

        const div=document.createElement("div");

        div.className="file-item";

        div.innerHTML=`

            📄 <strong>${file.name}</strong>

            <br>

            <small>${formatSize(file.size)}</small>

        `;

        selectedFiles.appendChild(div);

    });

}

// ============================

function formatSize(bytes){

    if(bytes<1024)

        return bytes+" B";

    if(bytes<1024*1024)

        return (bytes/1024).toFixed(1)+" KB";

    return (bytes/(1024*1024)).toFixed(2)+" MB";

}

// ============================
// SUBIR
// ============================

async function uploadFiles(){

    if(currentFiles.length===0){

        alert(

            "Selecciona al menos un archivo."

        );

        return;

    }

    const formData=new FormData();

    currentFiles.forEach(file=>{

        formData.append(

            "files",

            file

        );

    });

    if(!customLimit.disabled){

        formData.append(

            "limit",

            customLimit.value

        );

    }

    try{

        uploadButton.disabled=true;

        uploadButton.textContent="Procesando...";

        status.innerHTML="📤 Subiendo archivos...";

        result.innerHTML="";

        const response=await fetch(

            `${API_URL}/upload`,

            {

                method:"POST",

                body:formData

            }

        );

        const data=await response.json();

        if(!response.ok){

            throw new Error(

                data.detail

            );

        }

        status.innerHTML=

            "✅ Análisis finalizado correctamente.";

        renderStatistics(data);

    }

    catch(error){

        status.innerHTML="❌ Error";

        result.innerHTML=`

            <div class="error">

                ${error.message}

            </div>

        `;

    }

    finally{

        uploadButton.disabled=false;

        uploadButton.innerHTML="🚀 Analizar reseñas";

    }

}

// ============================
// ESTADISTICAS
// ============================

function renderStatistics(response) {

    const d = response.data;
    const s = response.statistics;
    const words = response.word_frequency;

    let wordsHtml = "";

    words.forEach(item => {

        wordsHtml += `
            <tr>
                <td>${item.word}</td>
                <td>${item.count.toLocaleString()}</td>
            </tr>
        `;

    });

    result.innerHTML = `

        <div class="card">
            <h3>📂 Archivos</h3>
            <p>${response.files_processed}</p>
        </div>

        <div class="card">
            <h3>📄 Originales</h3>
            <p>${d.total_original.toLocaleString()}</p>
        </div>

        <div class="card">
            <h3>🗑 Duplicadas</h3>
            <p>${d.duplicates_removed.toLocaleString()}</p>
        </div>

        <div class="card">
            <h3>🚫 Vacías</h3>
            <p>${d.empty_removed.toLocaleString()}</p>
        </div>

        <div class="card">
            <h3>✅ Finales</h3>
            <p>${d.total_clean.toLocaleString()}</p>
        </div>

        <div class="card">
            <h3>📝 Longitud promedio</h3>
            <p>${s.average_length}</p>
        </div>

        <div class="card">
            <h3>🔤 Palabras promedio</h3>
            <p>${s.average_words}</p>
        </div>

        <div class="card">
            <h3>📉 Más corta</h3>
            <p>${s.shortest_review}</p>
        </div>

        <div class="card">
            <h3>📈 Más larga</h3>
            <p>${s.longest_review}</p>
        </div>

        <div class="table-card">

            <h2>🔤 Top 20 palabras más frecuentes</h2>

            <table class="word-table">

                <thead>

                    <tr>

                        <th>Palabra</th>

                        <th>Frecuencia</th>

                    </tr>

                </thead>

                <tbody>

                    ${wordsHtml}

                </tbody>

            </table>

        </div>

    `;

}