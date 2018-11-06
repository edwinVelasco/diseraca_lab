function usuario(){
    //cambia el texto de id = "titulo_vista",  id"etiqueta" id="reorder"
    // el menu va en el div id="menu"
    $("#titulo_vista").html('Gestion de Usuarios del Sistema');
    $("#etiqueta").html('Usuarios');
    $("#reorder").html('<i class="icon-reorder"></i> Registro, Edicion y Busqueda de Usuarios');
    //$("#menu").load( "../static/html/menu_usuario.html");

}

function registro_usuario(){
    usuario(); //usuario se encarga de cambiar los titulos.y colocar el menu de los botones registrar, edicion y busqueda
    $("#formularios").load( "../static/html/usuarios/registro_usuario.html");
}

// Pasar a un js llamado laboratorio.js
function get_laboratorio(){
        $.ajax({
            type: 'GET',
            url: 'get_laboratorio',
            data: '',
            success: function (data) {                
                //console.log(data);
                
                $('#laboratorio').append("<option value='0'>Seleccione..</option>");
                for(var i=0; i<data.length; i++)
                {
                    $('#laboratorio').append("<option value='"+data[i].pk+"'>"+data[i].fields.nombre+"</option>");
                } 
                
            },
            error: function(data) {
                alert(data);
            }
        });
}

function listado_user(){
        
        $("#titulo_vista").html('Visualización y Restauración de la Contraseña');
        $("#etiqueta").html('Usuarios');
        $("#reorder").html('<i class="icon-reorder"></i> Visualización y Restauración de la Contraseña');
        $("#menu").html("");
        busqueda = '<div class="row-fluid" id="busqueda_user"></div>'
        tabla = '<div id="lista_usuarios"><table class="table table-hover">';
        thead = '<thead>    <tr>    <th>Nombre</th> <th>Codigo</th><th>Email</th> <th>Restaurar</th>  <th>Editar</th> <th>Desactivar/Activar</tr>    </thead>'
        tbody = '<tbody id="body_user">';
        tbody += '</tbody></div>';
        tabla += thead + tbody + '</table>';

        $("#formularios").html(busqueda+tabla);
        $("#busqueda_user").load( "../static/html/usuarios/buscar_user.html");
    }

function restaurar_pass(id){
    $.ajax({
            type: 'GET',
            url: '../administrador/restaurar_pass',
            data: {'id':id},
            success: function (data) {                
                if (data == 'ok')
                {
                    alert('contraseña restaurada con exito');
                }
                else if(data === 'logout')
                {
                    alert('La Sesión a Caducado, Recuerda Que Caduca Cada 20 Minutos')
                    window.location='logout';
                }
                else
                {
                    alert('no se pudo restaurar la contraseña');
                }
            },
            error: function(data) {
                alert(data);
            }
        });
}

function desactivar_user(id){
        $.ajax({
            type: 'GET',
            url: 'desactivar_user',
            data: {'id':id},
            success: function (data) {
                if (data == 'ok')
                {
                    alert('Usario Desactivado');
                    listado_user()
                }
                else if(data === 'logout')
                {
                    alert('La Sesión a Caducado, Recuerda Que Caduca Cada 20 Minutos')
                    window.location='logout';
                }
                else
                {
                    alert('');
                }
            },
            error: function(data) {
                alert(data);
            }
        });
}

function activar_user(id){
        $.ajax({
            type: 'GET',
            url: 'activar_user',
            data: {'id':id},
            success: function (data) {
                if (data == 'ok')
                {
                    alert('Usario Activado');
                    listado_user()
                }
                else if(data === 'logout')
                {
                    alert('La Sesión a Caducado, Recuerda Que Caduca Cada 20 Minutos')
                    window.location='logout';
                }
                else
                {
                    alert('No se pudo hacer la Operacion, Usuario no Encontrado');
                }
            },
            error: function(data) {
                alert(data);
            }
        });
    }

function editar_usuario(id){
    usuario_editar = id;

    $("#titulo_vista").html('Editar Usuario');
    $("#etiqueta").html('Usuarios');
    $("#reorder").html('<i class="icon-reorder"></i> Edición de Usuario');
    $("#menu").html("");

    $("#formularios").load( "../static/html/usuarios/editar_user.html");
}



    

