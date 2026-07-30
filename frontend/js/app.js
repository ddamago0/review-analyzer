const API_URL = "http://127.0.0.1:8000/api";


// ======================================
// ELEMENTOS DEL DOM
// ======================================

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

// Dashboard

const chartCanvas = document.getElementById("wordsChart");
const tableContainer = document.getElementById("topWordsTable");
const previewContainer = document.getElementById("reviewsPreview");

// Exportaciones

const exportJsonBtn = document.getElementById("exportJson");
const exportCsvBtn = document.getElementById("exportCsv");
const exportExcelBtn = document.getElementById("exportExcel");

// ======================================

let currentFiles = [];

let chart = null;

let lastResponse = null;

// ======================================
// EVENTOS
// ======================================

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

// ======================================

radios.forEach(radio => {

    radio.addEventListener("change", () => {

        customLimit.disabled =
            radio.value !== "limit" || !radio.checked;

        if (customLimit.disabled) {

            customLimit.value = "";

        }

    });

});

// ======================================

uploadButton.addEventListener(

    "click",

    uploadFiles

);

// ======================================
// MOSTRAR ARCHIVOS
// ======================================

function renderFiles() {

    if (currentFiles.length === 0) {

        selectedFiles.innerHTML = `

            <div class="empty">

                Ningún archivo seleccionado.

            </div>

        `;

        return;

    }

    selectedFiles.innerHTML = "";

    currentFiles.forEach(file => {

        const div = document.createElement("div");

        div.className = "file-item";

        div.innerHTML = `

            📄 <strong>${file.name}</strong>

            <br>

            <small>${formatSize(file.size)}</small>

        `;

        selectedFiles.appendChild(div);

    });

}

// ======================================

function formatSize(bytes) {

    if (bytes < 1024)
        return bytes + " B";

    if (bytes < 1024 * 1024)
        return (bytes / 1024).toFixed(1) + " KB";

    return (bytes / (1024 * 1024)).toFixed(2) + " MB";

}

// ======================================
// SUBIR ARCHIVOS
// ======================================

async function uploadFiles() {

    if (currentFiles.length === 0) {

        alert(

            "Selecciona al menos un archivo."

        );

        return;

    }

    const formData = new FormData();

    currentFiles.forEach(file => {

        formData.append(

            "files",

            file

        );

    });

    if (!customLimit.disabled) {

        formData.append(

            "limit",

            customLimit.value

        );

    }

    try {

        uploadButton.disabled = true;

        uploadButton.innerHTML = "Procesando...";

        status.innerHTML = "📤 Analizando archivos...";

        result.innerHTML = "";

        tableContainer.innerHTML = "";

        previewContainer.innerHTML = "";

        if (chart) {

            chart.destroy();

        }

        const response = await fetch(

            `${API_URL}/upload`,

            {

                method: "POST",

                body: formData

            }

        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(

                data.detail

            );

        }

        lastResponse = data;

        status.innerHTML =

            "✅ Análisis completado correctamente.";

        renderStatistics(data);

    }

    catch (error) {

        status.innerHTML = "❌ Error";

        result.innerHTML = `

            <div class="error">

                ${error.message}

            </div>

        `;

    }

    finally {

        uploadButton.disabled = false;

        uploadButton.innerHTML =

            "🚀 Iniciar análisis";

    }

}

// ======================================
// ESTADÍSTICAS PRINCIPALES
// ======================================

function renderStatistics(response){

    const d = response.data;

    const s = response.statistics;

    result.innerHTML = `

        <div class="card">

            <h3>📂 Archivos procesados</h3>

            <p>${response.files_processed}</p>

            <small>

                Cantidad de archivos Excel analizados.

            </small>

        </div>

        <div class="card">

            <h3>📄 Reseñas cargadas</h3>

            <p>${d.total_original.toLocaleString()}</p>

            <small>

                Total de reseñas encontradas antes
                del proceso de limpieza.

            </small>

        </div>

        <div class="card">

            <h3>🗑 Duplicados eliminados</h3>

            <p>${d.duplicates_removed.toLocaleString()}</p>

            <small>

                Reseñas repetidas eliminadas
                automáticamente.

            </small>

        </div>

        <div class="card">

            <h3>🚫 Reseñas vacías eliminadas</h3>

            <p>${d.empty_removed.toLocaleString()}</p>

            <small>

                Registros sin contenido.

            </small>

        </div>

        <div class="card">

            <h3>✅ Reseñas procesadas</h3>

            <p>${d.total_clean.toLocaleString()}</p>

            <small>

                Total de reseñas utilizadas
                durante el análisis.

            </small>

        </div>

        <div class="card">

            <h3>📝 Promedio de caracteres</h3>

            <p>${s.average_length}</p>

            <small>

                Cantidad promedio de caracteres
                por reseña.

            </small>

        </div>

        <div class="card">

            <h3>🔤 Promedio de palabras</h3>

            <p>${s.average_words}</p>

            <small>

                Cantidad promedio de palabras
                por reseña.

            </small>

        </div>

        <div class="card">

            <h3>📄 Longitud mínima</h3>

            <p>${s.shortest_review}</p>

            <small>

                Número de caracteres de la
                reseña más corta.

            </small>

        </div>

        <div class="card">

            <h3>📄 Longitud máxima</h3>

            <p>${s.longest_review}</p>

            <small>

                Número de caracteres de la
                reseña más extensa.

            </small>

        </div>

    `;

    //renderWordChart(response.word_frequency);

    renderWordTable(response.word_frequency);

    renderReviewsPreview(d.reviews);

    enableExportButtons();

}

// ======================================
// GRÁFICO DE PALABRAS
// ======================================

function renderWordChart(words){

    if(!words || words.length===0){

        return;

    }

    if(chart){

        chart.destroy();

    }

    const labels = words.map(item => item.word);

    const values = words.map(item => item.count);

    chart = new Chart(

        chartCanvas,

        {

            type:"bar",

            data:{

                labels:labels,

                datasets:[

                    {

                        label:"Frecuencia",

                        data:values,

                        borderWidth:1,

                        borderRadius:8,

                        backgroundColor:[

                            "#2563eb",
                            "#3b82f6",
                            "#60a5fa",
                            "#93c5fd",
                            "#1d4ed8",
                            "#2563eb",
                            "#3b82f6",
                            "#60a5fa",
                            "#93c5fd",
                            "#1d4ed8",
                            "#2563eb",
                            "#3b82f6",
                            "#60a5fa",
                            "#93c5fd",
                            "#1d4ed8",
                            "#2563eb",
                            "#3b82f6",
                            "#60a5fa",
                            "#93c5fd",
                            "#1d4ed8"

                        ]

                    }

                ]

            },

            options:{

                responsive:false,

                maintainAspectRatio:true,

                animation:false,

                plugins:{

                    legend:{
                        display:false
                    }

                }

            }

        }

    );

}

// ======================================
// TABLA TOP PALABRAS
// ======================================

function renderWordTable(words){

    if(!words || words.length===0){

        tableContainer.innerHTML = `

            <div class="empty">

                No hay palabras para mostrar.

            </div>

        `;

        return;

    }

    let html = `

        <table class="word-table">

            <thead>

                <tr>

                    <th>#</th>

                    <th>Palabra</th>

                    <th>Frecuencia</th>

                </tr>

            </thead>

            <tbody>

    `;

    words.forEach((item,index)=>{

        html += `

            <tr>

                <td>${index+1}</td>

                <td>${item.word}</td>

                <td>${item.count.toLocaleString()}</td>

            </tr>

        `;

    });

    html += `

            </tbody>

        </table>

    `;

    tableContainer.innerHTML = html;

}

// ======================================
// VISTA PREVIA DE RESEÑAS
// ======================================

function renderReviewsPreview(reviews){

    if(!reviews || reviews.length===0){

        previewContainer.innerHTML = `

            <div class="empty">

                No hay reseñas para mostrar.

            </div>

        `;

        return;

    }

    const preview = reviews.slice(0,5);

    let html = "";

    preview.forEach((review,index)=>{

        html += `

            <div class="review-card">

                <strong>

                    Reseña ${index+1}

                </strong>

                <p>

                    ${review}

                </p>

            </div>

        `;

    });

    previewContainer.innerHTML = html;

}

// ======================================
// ACTIVAR EXPORTACIONES
// ======================================

function enableExportButtons(){

    exportJsonBtn.disabled = false;

    exportCsvBtn.disabled = false;

    exportExcelBtn.disabled = false;

}