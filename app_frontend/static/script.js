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
const modalModificarEquipo = document.getElementById('modal_modificar_equipo');

if (modalModificarEquipo) {
    modalModificarEquipo.addEventListener('show.bs.modal', function (event) {
        const boton = event.relatedTarget;
        const idEquipo = boton.getAttribute('data-id');
        const nombreEquipo = boton.getAttribute('data-nombre');
        const idCurso = boton.getAttribute('data-curso');

        modalModificarEquipo.querySelector("#modificar_id_equipo").value = idEquipo;
        modalModificarEquipo.querySelector("#modificar_nombre_equipo").value = nombreEquipo;
        modalModificarEquipo.querySelector("#modificar_id_curso").value = idCurso;
    });
}

// Eliminar equipos
const modalEliminar = document.getElementById('modal_eliminar_equipo');

if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (event) {
        const boton = event.relatedTarget;
        const idEquipo = boton.getAttribute('data-id');
        const inputId = modalEliminar.querySelector("#eliminar_id_equipo");
        
        inputId.value = idEquipo;
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

document.addEventListener("DOMContentLoaded", () => {
    const flash = document.getElementById("flash-success");
    if (flash) {
        setTimeout(() => { flash.style.display = "none"; }, 3000);
    }
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
    // Inicializar todos los módulos de materiales
    initBusqueda();
    initBusquedaAlumno();
    initDropZone();
    initSortable();
    initFiltroCurso();
    initToggleExterno();
    initDetalles();
    initPreviewButton();
    initVolverButton();
    initEditarButtons();
    initEliminarButtons();
});

// =====================
// MATERIALES - COMPARTIDO
// =====================

var datosMaterialActual = null;
var modalDetalles = null;

function mostrarPreview() {
  if (!datosMaterialActual) return;
  document.getElementById('detallesInfo').classList.add('d-none');
  var preview = document.getElementById('detallesPreview');
  preview.classList.remove('d-none');
  document.getElementById('btnVolverDetalles').classList.remove('d-none');

  var id = datosMaterialActual.id_material;
  var tipo = datosMaterialActual.tipo_archivo || '';
  var esExterno = datosMaterialActual.es_externo;

  if (esExterno) {
    preview.innerHTML = '<div class="p-5"><p class="text-muted">Recurso externo. <a href="/material/' + id + '/descargar" class="btn btn-sm btn-campus">Abrir enlace</a></p></div>';
    return;
  }
  if (tipo === 'pdf') {
    preview.innerHTML = '<iframe src="/material/' + id + '/descargar" style="width:100%;height:70vh;border:none;"></iframe>';
  } else if (['jpg','jpeg','png','gif'].indexOf(tipo) !== -1) {
    preview.innerHTML = '<img src="/material/' + id + '/descargar" class="img-fluid" style="max-height:70vh;" alt="' + (datosMaterialActual.titulo || '') + '">';
  } else if (['mp4','webm','ogg'].indexOf(tipo) !== -1) {
    preview.innerHTML = '<video controls style="max-width:100%;max-height:70vh;"><source src="/material/' + id + '/descargar" type="video/' + tipo + '"></video>';
  } else {
    preview.innerHTML = '<div class="p-5"><i class="bi bi-file-earmark icon-empty"></i><p class="mt-2 text-muted">Vista previa no disponible</p></div>';
  }
}

function volverADetalles() {
  document.getElementById('detallesPreview').classList.add('d-none');
  document.getElementById('detallesInfo').classList.remove('d-none');
  document.getElementById('btnVolverDetalles').classList.add('d-none');
}

function llenarModalDetalles(d) {
  if (!d) return;
  datosMaterialActual = d;
  document.getElementById('detallesTitulo').innerHTML = '<i class="bi bi-info-circle"></i> ' + d.titulo;
  document.getElementById('detallesDesc').textContent = d.descripcion || 'Sin descripción';
  document.getElementById('detallesTipo').innerHTML = '<span class="badge bg-secondary bg-opacity-10 text-secondary">' + d.tipo_material + '</span>';
  document.getElementById('detallesTema').textContent = d.tema || '-';
  document.getElementById('detallesFecha').textContent = d.fecha_material || '-';

  var eHtml = '';
  if (d.estado === 'publicado') eHtml = '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Publicado</span>';
  else if (d.estado === 'borrador') eHtml = '<span class="badge bg-warning text-dark"><i class="bi bi-pencil"></i> Borrador</span>';
  else if (d.estado === 'programado') eHtml = '<span class="badge bg-info"><i class="bi bi-clock"></i> Programado</span>';
  else if (d.estado === 'archivado') eHtml = '<span class="badge bg-secondary"><i class="bi bi-archive"></i> Archivado</span>';
  else eHtml = '<span class="badge bg-secondary">' + d.estado + '</span>';
  document.getElementById('detallesEstado').innerHTML = eHtml;

  document.getElementById('detallesProfe').innerHTML = d.profesor_nombre ? '<i class="bi bi-person"></i> ' + d.profesor_nombre : '-';

  var tam = d.tamano_bytes;
  if (tam) {
    if (tam > 1048576) document.getElementById('detallesTamano').textContent = (tam / 1048576).toFixed(1) + ' MB';
    else if (tam > 1024) document.getElementById('detallesTamano').textContent = (tam / 1024).toFixed(0) + ' KB';
    else document.getElementById('detallesTamano').textContent = tam + ' B';
  } else {
    document.getElementById('detallesTamano').textContent = d.es_externo ? 'Enlace externo' : '-';
  }

  document.getElementById('btnDescargarDetalles').href = '/material/' + d.id_material + '/descargar';

  var previewBtn = document.getElementById('btnPreview');
  var tp = d.tipo_archivo || '';
  if (['pdf','jpg','jpeg','png','gif','mp4','webm','ogg'].indexOf(tp) !== -1 || d.es_externo) {
    previewBtn.classList.remove('d-none');
  } else {
    previewBtn.classList.add('d-none');
  }

  document.getElementById('detallesInfo').classList.remove('d-none');
  document.getElementById('detallesPreview').classList.add('d-none');
  document.getElementById('btnVolverDetalles').classList.add('d-none');

  if (!modalDetalles) modalDetalles = new bootstrap.Modal(document.getElementById('modalDetalles'));
  modalDetalles.show();
}

// =====================
// MATERIALES - PROFESOR
// =====================

var ultimaDataMaterial = null;

function buscarFilaProfesor(id) {
  var filas = document.querySelectorAll('#cuerpoTabla .fila-material');
  for (var i = 0; i < filas.length; i++) {
    var d = JSON.parse(filas[i].dataset.material);
    if (d.id_material == id) return { row: filas[i], data: d };
  }
  return null;
}

function initBusqueda() {
  var input = document.getElementById('filtroBusqueda');
  var tipo = document.getElementById('filtroTipo');
  var estado = document.getElementById('filtroEstado');
  if (input) input.addEventListener('input', filtrarMateriales);
  if (tipo) tipo.addEventListener('change', filtrarMateriales);
  if (estado) estado.addEventListener('change', filtrarMateriales);

  function filtrarMateriales() {
    var busqueda = document.getElementById('filtroBusqueda');
    var tipo = document.getElementById('filtroTipo');
    var estado = document.getElementById('filtroEstado');
    var q = busqueda ? busqueda.value.toLowerCase().trim() : '';
    var tv = tipo ? tipo.value : '';
    var ev = estado ? estado.value : '';
    var visibles = 0;
    document.querySelectorAll('#cuerpoTabla .fila-material').forEach(function(row) {
      if (!row.dataset.material) return;
      var d = JSON.parse(row.dataset.material);
      var matchBusq = !q || (d.titulo && d.titulo.toLowerCase().indexOf(q) !== -1) || (d.tema && d.tema.toLowerCase().indexOf(q) !== -1) || (d.descripcion && d.descripcion.toLowerCase().indexOf(q) !== -1);
      var matchTipo = !tv || d.tipo_material === tv;
      var matchEstado = !ev || d.estado === ev;
      var show = matchBusq && matchTipo && matchEstado;
      row.style.display = show ? '' : 'none';
      if (show) visibles++;
    });
    var totalSpan = document.getElementById('totalMateriales');
    if (totalSpan) totalSpan.textContent = visibles;
  }
}

function initBusquedaAlumno() {
  var input = document.getElementById('filtroBusqueda');
  var tipo = document.getElementById('filtroTipo');
  var estado = document.getElementById('filtroEstado');
  if (!input && !tipo && !estado) return;
  var cb = function() { filtrarCards(); };
  if (input) input.addEventListener('input', cb);
  if (tipo) tipo.addEventListener('change', cb);
  if (estado) estado.addEventListener('change', cb);

  function filtrarCards() {
    var busqueda = document.getElementById('filtroBusqueda');
    var tipo = document.getElementById('filtroTipo');
    var estado = document.getElementById('filtroEstado');
    var q = busqueda ? busqueda.value.toLowerCase().trim() : '';
    var tv = tipo ? tipo.value : '';
    var ev = estado ? estado.value : '';
    var totalVisibles = 0;
    document.querySelectorAll('.card-material').forEach(function(card) {
      if (!card.dataset.material) return;
      var d = JSON.parse(card.dataset.material);
      var matchBusq = !q || (d.titulo && d.titulo.toLowerCase().indexOf(q) !== -1) || (d.tema && d.tema.toLowerCase().indexOf(q) !== -1) || (d.descripcion && d.descripcion.toLowerCase().indexOf(q) !== -1);
      var matchTipo = !tv || d.tipo_material === tv;
      var matchEstado = !ev || d.estado === ev;
      var show = matchBusq && matchTipo && matchEstado;
      card.style.display = show ? '' : 'none';
      if (show) totalVisibles++;
    });
    document.querySelectorAll('.card-tema').forEach(function(grupo) {
      var cardsVisibles = grupo.querySelectorAll('.card-material[style*="display: none"]').length;
      var totalCards = grupo.querySelectorAll('.card-material').length;
      grupo.style.display = cardsVisibles === totalCards ? 'none' : '';
    });
    var totalSpan = document.getElementById('totalMateriales');
    if (totalSpan) totalSpan.textContent = totalVisibles;
  }
}

function initDropZone() {
  var dropZone = document.getElementById('dropZone');
  var fileInput = document.getElementById('fileInput');
  if (!dropZone || !fileInput) return;

  dropZone.addEventListener('click', function() { fileInput.click(); });

  fileInput.addEventListener('change', function() {
    if (fileInput.files.length) abrirModalConArchivo(fileInput.files[0]);
  });

  dropZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', function() {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', function(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) abrirModalConArchivo(e.dataTransfer.files[0]);
  });

  function abrirModalConArchivo(archivo) {
    var dt = new DataTransfer();
    dt.items.add(archivo);
    document.getElementById('archivo').files = dt.files;
    document.getElementById('uploadProgress').classList.remove('d-none');
    document.getElementById('fileName').textContent = archivo.name;
    var tam = archivo.size;
    if (tam > 1048576) document.getElementById('fileSize').textContent = (tam / 1048576).toFixed(1) + ' MB';
    else if (tam > 1024) document.getElementById('fileSize').textContent = (tam / 1024).toFixed(0) + ' KB';
    else document.getElementById('fileSize').textContent = tam + ' B';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    new bootstrap.Modal(document.getElementById('modalSubirMaterial')).show();
  }
}

function initSortable() {
  document.querySelectorAll('th.sortable').forEach(function(th) {
    th.addEventListener('click', function() {
      var col = this.dataset.order;
      if (!col) return;
      var params = new URLSearchParams(window.location.search);
      var currentOrder = params.get('order_by') || 'fecha_subida';
      var currentDir = params.get('order_dir') || 'DESC';
      if (currentOrder === col) {
        params.set('order_dir', currentDir === 'ASC' ? 'DESC' : 'ASC');
      } else {
        params.set('order_by', col);
        params.set('order_dir', 'ASC');
      }
      params.set('pagina', '1');
      window.location.search = params.toString();
    });
  });
}

function initFiltroCurso() {
  var select = document.getElementById('filtroCurso');
  if (!select) return;
  select.addEventListener('change', function() {
    var id = this.value;
    var params = new URLSearchParams(window.location.search);
    if (id) params.set('curso', id);
    else params.delete('curso');
    params.set('pagina', '1');
    window.location.search = params.toString();
  });
}

function initToggleExterno() {
  var cb = document.getElementById('es_externo');
  if (!cb) return;
  cb.addEventListener('change', function() {
    document.getElementById('campoArchivo').classList.toggle('d-none', this.checked);
    document.getElementById('campoUrl').classList.toggle('d-none', !this.checked);
  });
}

function initDetalles() {
  var tabla = document.getElementById('cuerpoTabla');
  if (tabla) {
    tabla.addEventListener('click', function(e) {
      var link = e.target.closest('[data-detalles-id]');
      if (!link) return;
      e.preventDefault();
      var id = parseInt(link.dataset.detallesId);
      var encontrado = buscarFilaProfesor(id);
      if (encontrado) llenarModalDetalles(encontrado.data);
    });
  }
  var cards = document.querySelector('.card-material');
  if (cards) {
    document.addEventListener('click', function(e) {
      var link = e.target.closest('[data-detalles-id]');
      if (!link) return;
      e.preventDefault();
      var id = parseInt(link.dataset.detallesId);
      var cards = document.querySelectorAll('.card-material');
      for (var i = 0; i < cards.length; i++) {
        var d = JSON.parse(cards[i].dataset.material);
        if (d.id_material == id) { llenarModalDetalles(d); break; }
      }
    });
  }
}

function initPreviewButton() {
  var btn = document.getElementById('btnPreview');
  if (btn) btn.addEventListener('click', mostrarPreview);
}

function initVolverButton() {
  var btn = document.getElementById('btnVolverDetalles');
  if (btn) btn.addEventListener('click', volverADetalles);
}

function initEditarButtons() {
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.btn-editar');
    if (!btn) return;
    var id = parseInt(btn.dataset.id);
    var encontrado = buscarFilaProfesor(id);
    if (!encontrado) return;
    var d = encontrado.data;
    document.getElementById('editar_titulo').value = d.titulo || '';
    document.getElementById('editar_descripcion').value = d.descripcion || '';
    document.getElementById('editar_tipo').value = d.tipo_material || '';
    document.getElementById('editar_tema').value = d.tema || '';
    document.getElementById('editar_estado').value = d.estado || 'publicado';
    document.getElementById('editar_es_libre').checked = !!d.es_libre;
    document.getElementById('formEditar').action = '/material/' + id + '/editar';
    new bootstrap.Modal(document.getElementById('modalEditarMaterial')).show();
  });
}

function initEliminarButtons() {
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.btn-eliminar');
    if (!btn) return;
    var id = parseInt(btn.dataset.id);
    var encontrado = buscarFilaProfesor(id);
    if (!encontrado) return;
    document.getElementById('eliminarTitulo').textContent = encontrado.data.titulo || '';
    document.getElementById('btnConfirmarEliminar').href = '/material/' + id + '/eliminar';
    new bootstrap.Modal(document.getElementById('modalEliminarMaterial')).show();
  });
}

// Editar_cursos - abrir modal con datos
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.btn-editar-curso').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const tr = btn.closest('tr');
      const id = tr.getAttribute('data-id');
      const anio = tr.getAttribute('data-anio');
      const cuatri = tr.getAttribute('data-cuatri');
            
      document.getElementById('id_curso_modal').value = tr.dataset.id;
      document.getElementById('anio_modal').value = tr.dataset.anio;
      document.getElementById('cuatrimestre_modal').value = tr.dataset.cuatri;
      new bootstrap.Modal(document.getElementById('modal_modificar_curso')).show();

      elModal.addEventListener('hidden.bs.modal', function () {
        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
        document.body.style.overflow = 'auto';
        document.body.classList.remove('modal-open');
      });
    });
  });
});

// Eliminar curso
const modalEliminarCurso = document.getElementById('modal_eliminar_curso');

if (modalEliminarCurso) {
    modalEliminarCurso.addEventListener('show.bs.modal', function (event) {
        const boton = event.relatedTarget;
        const idCurso = boton.getAttribute('data-id');
        const inputId = modalEliminarCurso.querySelector("#eliminar_id_curso");
        
        inputId.value = idCurso;
    });
}