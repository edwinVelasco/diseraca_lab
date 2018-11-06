/**
 * Created by diseraca on 11/05/15.
 */

function get_maquinas(){
    $("#titulo_vista").html('Visualización y Edición de Maquinas');
    $("#etiqueta").html('Maquinas y Escalas Tn');
    $("#reorder").html('<i class="icon-reorder"></i> Visualización y Edición de Maquinas y Escalas Tn');
    $("#menu").html("");

    tabla = '<div id="lista_maquina"><table class="table table-hover">';
    thead = '<thead>    <tr>   <th>Maquina</th> <th>Fecha de Calibración</th> <th>Ver/Agregar Escalas</th> <th>Editar</th> <th>Borrar</th> </tr>    </thead>';
    tbody = '<tbody id="body_maquinas"></tbody>';
    tabla += thead + tbody + '</table> </div>';
    agregar = '<div class="control-group"><div class="controls"><div class="span3"></div><br/><button type="button" class="btn btn-danger" onclick="nueva_maquina()">Nueva Maquina</button></div></div>'
    $("#formularios").html(tabla+agregar);

    $.ajax({
        type: 'GET',
        url: 'get_maquinas',
        data: '',
        success: function (data){
            if(data.length == 0)
            {
                UIkit.notify({
                    message : 'No Hay Maquinas Registradas',
                    status  : 'danger',
                    timeout : 3000,
                    pos:'top-center'
                    });
                return;
            }
             for(i=0; i< data.length; i++)
                {
                    nombre = '<th>'+data[i].fields.nombre+'</th>';
                    fecha = '<th>'+data[i].fields.fecha_calibracion+'</th>';
                    lista_escalas = '<th> <button type="button" class="btn btn-danger" onclick="get_escalas('+data[i].pk+')">Ver/Agregar</button></th>';
                    editar = '<th> <button type="button" class="btn btn-danger" onclick="editar_maquina('+data[i].pk+')">Editar</button></th>';
                    borrar = '<th> <button type="button" class="btn btn-danger" onclick="borrar_maquina('+data[i].pk+')">Borrar</button></th>';
                    fila = '<tr>'+nombre+fecha+lista_escalas+editar+borrar+'</tr>';
                    $('#body_maquinas').append(fila);
                }
        },
        error: function(data) {
            alert(data);
        }
    });
}

function nueva_maquina(){
    $("#formularios").load( "../static/html/maquina/registro_maquina.html");
}

function borrar_maquina(id){
    $.ajax({
        type: 'GET',
        url: 'borrar_maquina',
        data: {'id':id},
        success: function (data){
            if(data === 'ok')
            {
                UIkit.notify({
                    message : 'Maquina Borrada Con Exito',
                    status  : 'danger',
                    timeout : 3000,
                    pos:'top-center'
                    });
                get_maquinas();
                return;
            }
        },
        error: function(data) {
            alert(data);
        }
    });
}

function editar_maquina(id){
    orden_editar = id;
    $("#formularios").load( "../static/html/maquina/editar_maquina.html");
}

function get_escalas(id){

    tabla = '<div id="lista_escalas"><table class="table table-hover">';
    thead = '<thead>    <tr>   <th>Codigo</th> <th>Escala</th> <th>Correccion</th> <th>Factor 2</th> <th>Editar</th> <th>Borrar</th> </tr>    </thead>';
    tbody = '<tbody id="body_escalas"></tbody>';
    tabla += thead + tbody + '</table> </div>';
    agregar = '<div class="control-group"><div class="controls"><div class="span3"></div><br/><button type="button" class="btn btn-danger" onclick="nueva_escala('+id+')">Nueva Escala</button></div></div>'
    $("#formularios").html(tabla+agregar);

    $.ajax({
        type: 'GET',
        url: 'get_escalas',
        data: {'id':id},
        success: function (data){
            if(data.length == 0)
            {
                UIkit.notify({
                    message : 'No Hay Escalas Registradas',
                    status  : 'danger',
                    timeout : 3000,
                    pos:'top-center'
                    });
                return;
            }
             for(i=0; i< data.length; i++)
                {
                    codigo = '<th>'+data[i].fields.codigo+'</th>';
                    escala = '<th>'+data[i].fields.escala+'</th>';
                    correccion = '<th>'+data[i].fields.correccion+'</th>';
                    factor = '<th>'+data[i].fields.factor2+'</th>';

                    editar = '<th> <button type="button" class="btn btn-danger" onclick="editar_escala('+data[i].pk+')">Editar</button></th>';
                    borrar = '<th> <button type="button" class="btn btn-danger" onclick="borrar_escala('+data[i].pk+')">Borrar</button></th>';
                    fila = '<tr>'+codigo+escala+correccion+factor+editar+borrar+'</tr>';
                    $('#body_escalas').append(fila);
                }
        },
        error: function(data) {
            alert(data);
        }
    });
}

function nueva_escala(id){
    orden_editar = id;
    $("#formularios").load( "../static/html/maquina/registro_escalatn.html");
}

function borrar_escala(id){
     $.ajax({
            type: 'GET',
            url: 'borrar_escala',
            data: {'id':id},
            success: function (data)
            {
                UIkit.notify({
                    message : 'Escala borrada con exito',
                    status  : 'success',
                    timeout : 5000,
                    pos:'top-center'
                });
                get_maquinas(data);
            },
            error: function(data) {
                alert(error);
            }
        });
}

function editar_escala(id){
    orden_editar = id;
    $("#formularios").load( "../static/html/maquina/editar_escalatn.html");
}