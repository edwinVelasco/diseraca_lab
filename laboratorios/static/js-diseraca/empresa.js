
function registro_empresa() {
    $("#titulo_vista").html('Gestion de Empresas y Personas Naturales');
    $("#etiqueta").html('Laboratorio');
    $("#reorder").html('<i class="icon-reorder"></i> Registro, Edicion y Busqueda de Empresas');
    $("#formularios").load( "../static/html/empresa/registro_empresa.html");
}



function listado_empresas(){

        $("#titulo_vista").html('Visualización y Edición de Empresas');
        $("#etiqueta").html('Empresas');
        $("#reorder").html('<i class="icon-reorder"></i> Visualización y Edición de Empresas');
        $("#menu").html("");

        busqueda = '<div class="row-fluid" id="busqueda_empresa"></div>';
        tabla = '<div id="lista_empresa"><table class="table table-hover">';
        thead = '<thead>    <tr>    <th>Nombre</th> <th>Identificación</th> <th>Email</th> <th>Editar</th> </tr>    </thead>';
        tbody = '<tbody id="body_empresa"></tbody></div>';
        tabla += thead + tbody + '</table>';
        $("#formularios").html(busqueda+tabla);

        $("#busqueda_empresa").load( "../static/html/empresa/buscar_empresa.html");
    }

function listado_empresa_id(){

    $.ajax({
        type: 'GET',
        url: 'listado_empresa_id',
        data: '',
        success: function (data) {

            console.log(data);
            var array_id = [];
            for(var i=0; i<data.length; i++)
                {
                    array_id[i] = data[i].fields.username;
                }

            $('#empresa').autocomplete({
                source: array_id
            });


        },
            error: function(data) {
                alert('Error');
                console.log(data)
            }
        });
}
