const boton = document.getElementById("btnTest");
const resultado = document.getElementById("resultado");

boton.addEventListener("click", async () => {

    try {

        const respuesta = await fetch("http://127.0.0.1:8000/");

        const datos = await respuesta.json();

        resultado.innerHTML = `
            <p>${datos.message}</p>
        `;

    } catch (error) {

        resultado.innerHTML = `
            <p>No fue posible conectar con el backend.</p>
        `;

        console.error(error);

    }

});