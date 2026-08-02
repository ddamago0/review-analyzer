// ======================================
// CONFIGURACIÓN
// ======================================

// Backend base URL. The backend always runs at http://127.0.0.1:8000,
// so it must be addressed with an absolute URL regardless of how the
// frontend itself is served (file://, Live Server, nginx, etc.). A
// relative "/api" prefix would resolve against the current origin and
// send requests to the wrong port (e.g. 5500) instead of the backend.
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
const optimizeTokens = document.getElementById("optimizeTokens");

const radios = document.querySelectorAll(
    'input[name="limitType"]'
);

// Dashboard

const tableContainer = document.getElementById("topWordsTable");
const previewContainer = document.getElementById("reviewsPreview");
const tokenAnalysisContainer = document.getElementById("tokenAnalysisContainer");

// Análisis de tokens (una reseña)

const tokenInput = document.getElementById("tokenInput");
const tokenAnalyzeBtn = document.getElementById("tokenAnalyzeBtn");
const tokenResult = document.getElementById("tokenResult");

// Exportaciones

const exportJsonBtn = document.getElementById("exportJson");
const exportCsvBtn = document.getElementById("exportCsv");
const exportExcelBtn = document.getElementById("exportExcel");

// ======================================
// ESTADO
// ======================================

let currentFiles = [];

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
    // Folder uploads may contain non-Excel files; keep only the valid ones.
    currentFiles = [...e.target.files].filter(
        file => /\.(xlsx|xls)$/i.test(file.name)
    );
    renderFiles();
});

radios.forEach(radio => {
    radio.addEventListener("change", () => {
        customLimit.disabled =
            radio.value !== "limit" || !radio.checked;

        if (customLimit.disabled) {
            customLimit.value = "";
        }
    });
});

uploadButton.addEventListener("click", uploadFiles);

tokenAnalyzeBtn.addEventListener("click", analyzeSingleReview);

exportJsonBtn.addEventListener("click", () => exportResults("json"));
exportCsvBtn.addEventListener("click", () => exportResults("csv"));
exportExcelBtn.addEventListener("click", () => exportResults("excel"));

// ======================================
// UTILIDADES
// ======================================

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatSize(bytes) {
    if (bytes < 1024)
        return bytes + " B";

    if (bytes < 1024 * 1024)
        return (bytes / 1024).toFixed(1) + " KB";

    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

function formatCurrency(value) {
    return "$" + Number(value || 0).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function setStatus(message, type) {
    status.className = "status" + (type ? " " + type : "");
    status.innerHTML = message;
}

function setLoadingState(button, loading, loadingText, idleText) {
    button.disabled = loading;
    button.innerHTML = loading
        ? `<span class="spinner"></span> ${loadingText}`
        : idleText;
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

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
            📄 <strong>${escapeHtml(file.name)}</strong>
            <br>
            <small>${formatSize(file.size)}</small>
        `;
        selectedFiles.appendChild(div);
    });
}

// ======================================
// SUBIR ARCHIVOS
// ======================================

async function uploadFiles() {
    if (currentFiles.length === 0) {
        alert("Selecciona al menos un archivo.");
        return;
    }

    const formData = new FormData();

    currentFiles.forEach(file => {
        formData.append("files", file);
    });

    if (!customLimit.disabled) {
        formData.append("limit", customLimit.value);
    }

    formData.append("optimize_tokens", optimizeTokens.checked ? "true" : "false");

    try {
        setLoadingState(uploadButton, true, "Procesando...", "🚀 Iniciar análisis");
        setStatus('<div class="loading"><span class="spinner"></span> Analizando archivos...</div>', "info");

        result.innerHTML = "";
        tableContainer.innerHTML = "";
        previewContainer.innerHTML = "";

        const response = await fetch(
            `${API_URL}/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        let data = null;
        try {
            data = await response.json();
        } catch (e) {
            data = null;
        }

        if (!response.ok) {
            const message = data && typeof data.detail === "string"
                ? data.detail
                : `El servidor respondió con el código HTTP ${response.status}.`;
            throw new Error(message);
        }

        if (!data) {
            throw new Error("El servidor devolvió una respuesta vacía o inválida.");
        }

        lastResponse = data;

        setStatus("✅ Análisis completado correctamente.", "success");

        renderStatistics(data);
    } catch (error) {
        setStatus("❌ Error al procesar los archivos.", "error-status");

        result.innerHTML = `
            <div class="error">
                ${escapeHtml(error.message)}
            </div>
        `;
    } finally {
        setLoadingState(uploadButton, false, "Procesando...", "🚀 Iniciar análisis");
    }
}

// ======================================
// ESTADÍSTICAS PRINCIPALES
// ======================================

function renderStatistics(response) {
    const d = response.data;
    const s = response.statistics;

    result.innerHTML = `
        <div class="card">
            <h3>📂 Archivos procesados</h3>
            <p>${Number(response.files_processed).toLocaleString()}</p>
            <small>
                Cantidad de archivos Excel analizados.
            </small>
        </div>

        <div class="card">
            <h3>📄 Reseñas cargadas</h3>
            <p>${Number(d.total_original).toLocaleString()}</p>
            <small>
                Total de reseñas encontradas antes
                del proceso de limpieza.
            </small>
        </div>

        <div class="card">
            <h3>🗑 Duplicados eliminados</h3>
            <p>${Number(d.duplicates_removed).toLocaleString()}</p>
            <small>
                Reseñas repetidas eliminadas
                automáticamente.
            </small>
        </div>

        <div class="card">
            <h3>🚫 Reseñas vacías eliminadas</h3>
            <p>${Number(d.empty_removed).toLocaleString()}</p>
            <small>
                Registros sin contenido.
            </small>
        </div>

        <div class="card">
            <h3>✅ Reseñas procesadas</h3>
            <p>${Number(d.total_clean).toLocaleString()}</p>
            <small>
                Total de reseñas utilizadas
                durante el análisis.
            </small>
        </div>

        <div class="card">
            <h3>📝 Promedio de caracteres por reseña</h3>
            <p>${s.average_length}</p>
            <small>
                Cantidad promedio de caracteres
                por reseña.
            </small>
        </div>

        <div class="card">
            <h3>🔤 Promedio de palabras por reseña</h3>
            <p>${s.average_words}</p>
            <small>
                Cantidad promedio de palabras
                por reseña.
            </small>
        </div>

        <div class="card">
            <h3>📄 Longitud mínima de reseña</h3>
            <p>${s.shortest_review}</p>
            <small>
                Número de caracteres de la
                reseña más corta.
            </small>
        </div>

        <div class="card">
            <h3>📄 Longitud máxima de reseña</h3>
            <p>${s.longest_review}</p>
            <small>
                Número de caracteres de la
                reseña más extensa.
            </small>
        </div>
    `;

    renderWordTable(response.word_frequency);

    renderReviewsPreview(d.reviews);

    renderTokenAnalysis(response.token_analysis);

    enableExportButtons();
}

// ======================================
// TABLA TOP PALABRAS
// ======================================

function renderWordTable(words) {
    if (!words || words.length === 0) {
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

    words.forEach((item, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${escapeHtml(item.word)}</td>
                <td>${Number(item.count).toLocaleString()}</td>
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

function renderReviewsPreview(reviews) {
    if (!reviews || reviews.length === 0) {
        previewContainer.innerHTML = `
            <div class="empty">
                No hay reseñas para mostrar.
            </div>
        `;
        return;
    }

    const preview = reviews.slice(0, 5);

    let html = "";

    preview.forEach((review, index) => {
        html += `
            <div class="review-card">
                <strong>
                    Reseña ${index + 1}
                </strong>
                <p>
                    ${escapeHtml(review)}
                </p>
            </div>
        `;
    });

    previewContainer.innerHTML = html;
}

// ======================================
// OPTIMIZACIÓN DE TOKENS (AGREGADO)
// ======================================

function renderTokenAnalysis(tokenAnalysis) {
    if (!tokenAnalysis || !tokenAnalysis.enabled) {
        tokenAnalysisContainer.innerHTML = `
            <div class="empty">
                Activa la opción
                "Reducir costos por tokens"
                para ver esta sección.
            </div>
        `;
        return;
    }

    const projection = tokenAnalysis.projection || {};

    let errorBadges = "";
    (tokenAnalysis.error_types || []).slice(0, 5).forEach(item => {
        errorBadges += `
            <span class="badge badge-error">
                ${escapeHtml(item[0])} · ${item[1]}
            </span>
        `;
    });

    let componentBadges = "";
    (tokenAnalysis.components || []).slice(0, 5).forEach(item => {
        componentBadges += `
            <span class="badge badge-component">
                ${escapeHtml(item[0])} · ${item[1]}
            </span>
        `;
    });

    tokenAnalysisContainer.innerHTML = `
        <div class="savings-highlight">
            <small>
                Ahorro mensual estimado
                (${projection.reviews_per_day} reseñas/día
                × ${projection.days_per_month} días)
            </small>
            <strong>${formatCurrency(projection.monthly_savings_usd)}</strong>
        </div>

        <div class="token-summary">
            <div class="token-stat">
                <small>Tokens originales (español)</small>
                <strong>${Number(tokenAnalysis.total_original_tokens).toLocaleString()}</strong>
            </div>
            <div class="token-stat">
                <small>Tokens traducidos (inglés)</small>
                <strong>${Number(tokenAnalysis.total_translated_tokens).toLocaleString()}</strong>
            </div>
            <div class="token-stat positive">
                <small>Diferencia de tokens</small>
                <strong>${Number(tokenAnalysis.token_difference).toLocaleString()}</strong>
            </div>
            <div class="token-stat positive">
                <small>Reducción</small>
                <strong>${tokenAnalysis.token_difference_percent}%</strong>
            </div>
        </div>

        <div class="token-pair">
            <div>
                <small>Costo mensual original</small>
                <strong>${formatCurrency(projection.original_monthly_cost_usd)}</strong>
            </div>
            <div>
                <small>Costo mensual traducido</small>
                <strong>${formatCurrency(projection.translated_monthly_cost_usd)}</strong>
            </div>
        </div>

        ${errorBadges ? `
            <div class="extraction-list">
                ${errorBadges}
                ${componentBadges}
            </div>
        ` : ""}
    `;
}

// ======================================
// ANÁLISIS DE TOKENS (UNA RESEÑA)
// ======================================

async function analyzeSingleReview() {
    const text = tokenInput.value.trim();

    if (!text) {
        tokenResult.innerHTML = `
            <div class="error">
                Escribe una reseña para analizar.
            </div>
        `;
        return;
    }

    try {
        setLoadingState(tokenAnalyzeBtn, true, "Analizando...", "🔬 Analizar tokens");
        tokenResult.innerHTML = `
            <div class="loading">
                <span class="spinner"></span>
                Traduciendo y contando tokens...
            </div>
        `;

        const response = await fetch(
            `${API_URL}/analyze`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    review: text,
                    optimize_tokens: true
                })
            }
        );

        let data = null;
        try {
            data = await response.json();
        } catch (e) {
            data = null;
        }

        if (!response.ok) {
            const message = data && typeof data.detail === "string"
                ? data.detail
                : `El servidor respondió con el código HTTP ${response.status}.`;
            throw new Error(message);
        }

        if (!data) {
            throw new Error("El servidor devolvió una respuesta vacía o inválida.");
        }

        renderSingleTokenResult(data.analysis);
    } catch (error) {
        tokenResult.innerHTML = `
            <div class="error">
                ${escapeHtml(error.message)}
            </div>
        `;
    } finally {
        setLoadingState(tokenAnalyzeBtn, false, "Analizando...", "🔬 Analizar tokens");
    }
}

function renderSingleTokenResult(analysis) {
    const projection = analysis.projection || {};

    tokenResult.innerHTML = `
        <div class="compare-block">
            <small>Texto original (español)</small>
            <p>${escapeHtml(analysis.original_text)}</p>
        </div>

        <div class="compare-block">
            <small>Traducción (inglés)</small>
            <p>${escapeHtml(analysis.translated_text)}</p>
        </div>

        <div class="token-metrics">
            <div class="token-stat">
                <small>Tokens originales</small>
                <strong>${analysis.original_tokens}</strong>
            </div>
            <div class="token-stat">
                <small>Tokens traducidos</small>
                <strong>${analysis.translated_tokens}</strong>
            </div>
            <div class="token-stat positive">
                <small>Diferencia</small>
                <strong>${analysis.token_difference}</strong>
            </div>
            <div class="token-stat positive">
                <small>Reducción</small>
                <strong>${analysis.token_difference_percent}%</strong>
            </div>
        </div>

        <div class="savings-highlight">
            <small>
                Proyección mensual
                (${projection.reviews_per_day} reseñas/día
                × ${projection.days_per_month} días)
            </small>
            <strong>${formatCurrency(projection.monthly_savings_usd)}</strong>
        </div>

        <div class="extraction-list">
            <span class="badge badge-error">
                error_type: ${escapeHtml(analysis.extraction.error_type)}
            </span>
            <span class="badge badge-component">
                component: ${escapeHtml(analysis.extraction.component)}
            </span>
        </div>
    `;
}

// ======================================
// ACTIVAR EXPORTACIONES
// ======================================

function enableExportButtons() {
    exportJsonBtn.disabled = false;
    exportCsvBtn.disabled = false;
    exportExcelBtn.disabled = false;
}

// ======================================
// EXPORTACIONES
// ======================================

function exportResults(format) {
    if (!lastResponse) {
        alert("No hay resultados para exportar.");
        return;
    }

    try {
        if (format === "json") {
            exportJson();
        } else if (format === "csv") {
            exportCsv();
        } else if (format === "excel") {
            exportExcel();
        }
    } catch (error) {
        alert("Error al exportar: " + error.message);
    }
}

function exportJson() {
    const blob = new Blob(
        [JSON.stringify(lastResponse, null, 2)],
        { type: "application/json" }
    );
    downloadBlob(blob, "analisis_resenas.json");
}

function exportCsv() {
    const rows = [];

    rows.push(["Sección", "Etiqueta", "Valor"]);
    rows.push(["Resumen", "Archivos procesados", lastResponse.files_processed]);

    const d = lastResponse.data;
    const s = lastResponse.statistics;

    rows.push(["Resumen", "Columna de reseñas", d.column_name]);
    rows.push(["Resumen", "Reseñas cargadas", d.total_original]);
    rows.push(["Resumen", "Duplicados eliminados", d.duplicates_removed]);
    rows.push(["Resumen", "Reseñas vacías eliminadas", d.empty_removed]);
    rows.push(["Resumen", "Reseñas procesadas", d.total_clean]);
    rows.push(["Resumen", "Promedio de caracteres por reseña", s.average_length]);
    rows.push(["Resumen", "Promedio de palabras por reseña", s.average_words]);
    rows.push(["Resumen", "Longitud mínima de reseña", s.shortest_review]);
    rows.push(["Resumen", "Longitud máxima de reseña", s.longest_review]);

    (lastResponse.word_frequency || []).forEach(item => {
        rows.push(["Palabras", item.word, item.count]);
    });

    (d.reviews || []).forEach((review, index) => {
        rows.push(["Reseñas", "Reseña " + (index + 1), review]);
    });

    const csv = rows
        .map(row => row
            .map(cell => {
                const value = String(cell ?? "");
                if (/[",\n]/.test(value)) {
                    return '"' + value.replace(/"/g, '""') + '"';
                }
                return value;
            })
            .join(",")
        )
        .join("\n");

    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    downloadBlob(blob, "analisis_resenas.csv");
}

async function exportExcel() {
    const response = await fetch(
        `${API_URL}/export/xlsx`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ data: lastResponse })
        }
    );

    if (!response.ok) {
        let message = "Error al generar el archivo Excel.";
        try {
            const data = await response.json();
            if (data.detail) {
                message = data.detail;
            }
        } catch (e) {
            // ignore
        }
        throw new Error(message);
    }

    const blob = await response.blob();
    downloadBlob(blob, "analisis_resenas.xlsx");
}
