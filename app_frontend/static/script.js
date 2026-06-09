const title = document.getElementById("titulo")

// title.addEventListener("mouseover", () => {
//     alert("Hola")
// })

// const changeColor = document.getElementById("change-color")

// changeColor.onclick = function (event) {
//     const R = randomNumber().toString()
//     const G = randomNumber().toString()
//     const B = randomNumber().toString()
//     title.style.color = `rgb(${R},${G},${B})`
// }

// function randomNumber() {
//     return (Math.random() * 256).toFixed(0)
// }



// ===============
//   MENÚ ACTIVO
// ===============

const linksNavbar = document.querySelectorAll(".nav-link");

linksNavbar.forEach(function(link) {

    link.addEventListener("click", function() {

        linksNavbar.forEach(function(item) {
            item.classList.remove("active");
        });

        this.classList.add("active");
    });

});



// REPORTES

const botonesReportes = document.querySelectorAll(".btn-reporte");

botonesReportes.forEach(function(boton) {

    boton.addEventListener("mouseover", function() {

        this.classList.add("shadow");

    });

    boton.addEventListener("mouseout", function() {

        this.classList.remove("shadow");

    });

});

const botonesDescarga = document.querySelectorAll(".btn-descargar");

botonesDescarga.forEach(function(boton) {

    boton.addEventListener("click", function() {

        alert("Descargando PDF...");

    });

});

// ASISTENCIA

const modalAsistencia = document.getElementById("modalAsistencia");

const abrirModal = document.querySelectorAll(".abrir-modal");

const cerrarModal = document.getElementById("cerrarModal");

if (abrirModal.length > 0 && modalAsistencia) {

    abrirModal.forEach(function(boton) {

        boton.addEventListener("click", function() {

            modalAsistencia.style.display = "block";

        });

    });

}

if (cerrarModal && modalAsistencia) {

    cerrarModal.addEventListener("click", function() {

        modalAsistencia.style.display = "none";

    });

}

window.addEventListener("click", function(event) {

    if (event.target == modalAsistencia) {

        modalAsistencia.style.display = "none";

    }

});

const filasTabla = document.querySelectorAll(".fila-asistencia");

filasTabla.forEach(function(fila) {

    fila.addEventListener("mouseover", function() {

        this.classList.add("table-primary");

    });

    fila.addEventListener("mouseout", function() {

        this.classList.remove("table-primary");

    });

});

const formulario = document.getElementById("formAsistencia");

if (formulario) {

    formulario.addEventListener("submit", function(event) {

        const alumno = document.getElementById("alumno");
        const fecha = document.getElementById("fecha");

        if (alumno.value === "" || fecha.value === "") {

            event.preventDefault();

            alert("Debe completar todos los campos.");

        }

    });

}


// Modificar equipo
const inputIdModificar = document.getElementById("modificar_id_equipo");
const inputNombreModificar = document.getElementById("modificar_nombre_equipo");
const inputCursoModificar = document.getElementById("modificar_id_curso");

if (inputIdModificar) {
    inputIdModificar.addEventListener("input", function() {
        const idBuscado = this.value;

        if (idBuscado !== "") {
            fetch(`/equipos/datos/${idBuscado}`)
                .then(response => {
                    return response.json().then(data => {
                        if (!response.ok) {
                            throw new Error(data.error || "Error del servidor");
                        }
                        return data;
                    });
                })
                .then(equipo => {
                    inputNombreModificar.value = equipo.nombre_equipo;
                    inputCursoModificar.value = equipo.id_curso;
                })
                .catch(error => {
                    console.warn(`Buscando...: ${error.message}`);
                    inputNombreModificar.value = ""
                    inputCursoModificar.value = ""
                });
        } else {
            inputNombreModificar.value = "";
            inputCursoModificar.value = "";
        }
    });
}

// Modificar alumnos de equipos
const modalAlumnos = document.getElementById('modal_alumnos');

if (modalAlumnos) {
    modalAlumnos.addEventListener('show.bs.modal', function (event) {
        const botonElemento = event.relatedTarget;
        const idEquipo = botonElemento.getAttribute('data-id');
        const inputHiddenEquipo = document.getElementById('modal_alumnos_id_equipo');
        const tituloModal = document.getElementById('titulo_alumnos_modal');
        const grupoLista = document.getElementById('grupo_lista_alumnos');

        inputHiddenEquipo.value = idEquipo;
        tituloModal.innerText = `Alumnos asignados al Equipo ${idEquipo}:`;

        grupoLista.innerHTML = "";
        const moldeCargando = document.getElementById('molde_cargando').content.cloneNode(true);
        grupoLista.appendChild(moldeCargando);

        fetch(`/equipos/datos/${idEquipo}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error del servidor");
                }
                return response.json();
            })
            .then(equipo => {
                grupoLista.innerHTML = "";

                if (!equipo.alumnos || equipo.alumnos.length === 0) {
                    const moldeVacio = document.getElementById('molde_vacio').content.cloneNode(true);
                    grupoLista.appendChild(moldeVacio);
                    return;
                }

                equipo.alumnos.forEach(alumno => {
                    const moldeFila = document.getElementById('molde_alumno_fila').content.cloneNode(true);
                    
                    moldeFila.querySelector('.txt-legajo').innerText = `Padrón: ${alumno.legajo_alumno}`;
                    moldeFila.querySelector('.input-id-miembro').value = alumno.id_miembro;
                    
                    grupoLista.appendChild(moldeFila);
                });
            })
            .catch(error => {
                console.error(error);
                grupoLista.innerHTML = '';
                const moldeError = document.getElementById('molde_error').content.cloneNode(true);
                grupoLista.appendChild(moldeError);
            });
    });
} 

// GENERACION DE QR

function generarQR() {

    const contenedorQR = document.getElementById("qrcode");

    if (!contenedorQR) {
        return;
    }

    const codigoQR = contenedorQR.dataset.qr;

    if (!codigoQR) {
        return;
    }

    new QRCode(
        contenedorQR,
        {
            text: codigoQR,
            width: 250,
            height: 250
        }
    );

}

document.addEventListener(
    "DOMContentLoaded",
    generarQR
);