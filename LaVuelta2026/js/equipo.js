class Equipo {
    constructor(nombre, codigoUCI, pais) {
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
        this.director = "";
        this.categoria = "";
        this.paginaWeb = "";
    }

    rellenarAtributos() {
        this.director = "Maxime Monfort";
        this.categoria = "UCI WorldTeam";
        this.paginaWeb = "https://www.lavuelta.es/es/equipo/LTK/lidl-trek";
    }

    datosBasicos() {
        return `${this.nombre} (${this.codigoUCI})`;
    }

    getPais() {
        return this.pais;
    }

    getInformacionSecundaria() {
        return `<ul><li>Director deportivo: ${this.director}</li><li>Categoría: ${this.categoria}</li></ul>`;
    }

    getPaginaWeb(seccion) {
        const parrafo = document.createElement("p");
        const enlace = document.createElement("a");
        enlace.href = this.paginaWeb;
        enlace.textContent = "Ficha oficial de Lidl-Trek en La Vuelta 2026";
        parrafo.appendChild(enlace);
        seccion.appendChild(parrafo);
    }
}

// Se ejecuta al cargar este archivo con defer en equipo.html.
(() => {
    const encabezado = Array.from(document.querySelectorAll("main h2"))
        .find((elemento) => elemento.textContent.trim().toLocaleLowerCase("es") === "lidl-trek");

    if (!encabezado || encabezado.parentElement.querySelector("[data-equipo-lidl-trek]")) {
        return;
    }

    const lidlTrek = new Equipo("Lidl-Trek", "LTK", "Alemania");
    lidlTrek.rellenarAtributos();

    const seccion = document.createElement("section");
    seccion.dataset.equipoLidlTrek = "";

    const titulo = document.createElement("h3");
    titulo.textContent = `${lidlTrek.datosBasicos()} — ${lidlTrek.getPais()}`;
    seccion.appendChild(titulo);
    seccion.insertAdjacentHTML("beforeend", lidlTrek.getInformacionSecundaria());
    lidlTrek.getPaginaWeb(seccion);

    encabezado.insertAdjacentElement("afterend", seccion);
})();
