class Ciudad {
    constructor(nombre, pais, gentilicio) {
        this.nombre = nombre;
        this.pais = pais;
        this.gentilicio = gentilicio;
        this.poblacion = 0;
        this.latitud = 0;
        this.longitud = 0;
    }

    rellenarAtributos() {
        // Cortegana: población municipal de 2025 y coordenadas del núcleo
        // principal de 2022, según el Instituto de Estadística de Andalucía.
        this.poblacion = 4616;
        this.latitud = 37.909;
        this.longitud = -6.82;
    }

    getCiudad() {
        return this.nombre;
    }

    getPais() {
        return this.pais;
    }

    getInformacionSecundaria() {
        return `<ul><li>Gentilicio: ${this.gentilicio}</li><li>Población: ${this.poblacion.toLocaleString("es-ES")} habitantes</li></ul>`;
    }

    escribeCoordenadas(seccion) {
        const parrafo = document.createElement("p");
        parrafo.textContent = `Coordenadas del núcleo principal: ${this.latitud}, ${this.longitud}`;
        seccion.appendChild(parrafo);
    }
}

// Se ejecuta al cargar este archivo con defer en meteorologia.html.
(() => {
    const encabezado = Array.from(document.querySelectorAll("main h2"))
        .find((elemento) => elemento.textContent.trim().toLocaleLowerCase("es") === "meteorología");

    if (!encabezado || encabezado.parentElement.querySelector("[data-ciudad-cortegana]")) {
        return;
    }

    const cortegana = new Ciudad("Cortegana", "España", "corteganeses y corteganesas");
    cortegana.rellenarAtributos();

    const seccion = document.createElement("section");
    seccion.dataset.ciudadCortegana = "";

    const titulo = document.createElement("h3");
    titulo.textContent = `${cortegana.getCiudad()} (${cortegana.getPais()})`;
    seccion.appendChild(titulo);
    seccion.insertAdjacentHTML("beforeend", cortegana.getInformacionSecundaria());
    encabezado.insertAdjacentElement("afterend", seccion);
    cortegana.escribeCoordenadas(seccion);
})();
