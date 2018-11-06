function ensayos() {
          //cambia el texto de id = "titulo_vista",  id"etiqueta" id="reorder"
          // el menu va en el div id="menu"
          $("#titulo_vista").html('Gestion de Ensayos');
          $("#etiqueta").html('Laboratorio');
          $("#reorder").html('<i class="icon-reorder"></i> Registro, Edicion y Busqueda de Ensayos');
          //$("#menu").load("../static/html/menu_ensayo.html");

      }
       function registro_ensayo()
       {
           ensayos(); //empresa se encarga de cambiar los titulos.y colocar el menu de los botones registrar, edicion y busqueda
           $("#formularios").load( "../static/html/ensayos/registro_ensayo.html");
       }

    function listado_ensayo(){
        $("#titulo_vista").html('Visualización y Edición de Ensayos');
        $("#etiqueta").html('Ensayos');
        $("#reorder").html('<i class="icon-reorder"></i> Visualización y Edición de Ensayos');
        $("#menu").html("");

        busqueda = '<div class="row-fluid" id="busqueda_ensayo"></div>';
        tabla = '<div id="lista_ensayo"><table class="table table-hover">';
        thead = '<thead>    <tr>   <th>Codigo</th> <th>Descripción</th> <th>Valor</th> <th>Unidad</th> <th>Metodo</th> <th>Editar</th> </tr>    </thead>';
        tbody = '<tbody id="body_ensayos"></tbody></div>';
        tabla += thead + tbody + '</table>';
        $("#formularios").html(busqueda+tabla);

        $("#busqueda_ensayo").load( "../static/html/ensayos/buscar_ensayos.html");
    }

function editar_ensayo(id){
    ensayo_editar = id;
    console.log(ensayo_editar);

    $("#titulo_vista").html('Edicion de Ensayo');
    $("#etiqueta").html('Ensayo');
    $("#reorder").html('<i class="icon-reorder"></i> Edición de Ensayo');
    $("#menu").html("");

    $("#formularios").load( "../static/html/ensayos/editar_ensayo.html");
}