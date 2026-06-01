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
