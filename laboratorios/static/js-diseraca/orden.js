function registro_orden(){
    $("#formularios").load( "../static/html/orden/registro_orden.html");
}


function registro_adelanto(){
    $("#formularios").load( "../static/html/adelanto/registro_adelanto.html");
}


function registro_convenio(){
    $("#formularios").load( "../static/html/convenio/registro_convenio.html");
}


function buscar_orden(){

    busqueda = '<div class="row-fluid" id="busqueda_orden"></div>';
    tabla = '<div id="lista_orden"><table class="table table-hover">';
    thead = '<thead>    <tr>   <th>Orden</th> <th>Fecha</th> <th>Empresa</th> <th>Consignación</th> <th>Factura</th><th>Laboratorio</th> <th>Valor</th>  <th>Editar</th><th>Estado</th> <th>Anular</th> <th>Ver/Imprimir</th></tr></thead>';
    tbody = '<tbody id="body_orden"></tbody></div>';
    tabla += thead + tbody + '</table>';
    $("#formularios").html(busqueda+tabla);
    $("#busqueda_orden").load( "../static/html/orden/buscar_orden.html");
}


function anular_orden(numero){
    orden_editar = numero;
    $("#formularios").load( "../static/html/orden/anular_orden.html");
}


function editar_orden(numero){
    orden_editar = numero;
    $("#formularios").load( "../static/html/orden/editar_orden.html");
}


function ordenes_sin_aprobar(){
    $.ajax({
        type: 'GET',
        url: 'ordenes_sin_aprobacion',
        success: function (data) {

            if (data == 'not') {
                $("#formularios").html('Sin Ordenes para Aprobar');
                UIkit.notify({
                    message : 'No hay Ordenes Sin Aprobar',
                    status  : 'success',
                    timeout : 3000,
                    pos:'top-center'
                });
            }
            else
            {
                $("#formularios").html(data);
            }

        },
        error: function(data) {
            alert(data);
        }
    });
}


function ordenes_sin_imprimir(){
    $.ajax({
            type: 'GET',
            url: 'ordenes_aprobadas_no_impresas',
            success: function (data) {

                if (data === 'not') {
                    $("#formularios").html('Sin Ordenes para imprimir');
                    UIkit.notify({
                        message : 'No hay Ordenes Aprobadas Sin Imprimir',
                        status  : 'success',
                        timeout : 3000,
                        pos:'top-center'
                    });
                }
                else
                {
                    $("#formularios").html(data);
                }

            },
            error: function(data) {
                alert(data);
            }
        });
}


function aprobar_orden(id){
    $.ajax({
        type: 'GET',
        url: 'aprobar_orden',
        data: {'id':id},
        success: function (data) {
            if (data === 'ok'){
                UIkit.notify({
                    message : 'Orden Aprobada y se envio el correo al laboratorio',
                    status  : 'success',
                    timeout : 5000,
                    pos:'top-center'
                });
            }
            else{
                UIkit.notify({
                    message : 'Orden Aprobada, no se pudo enviar correo',
                    status  : 'success',
                    timeout : 5000,
                    pos:'top-center'
                });
            }
            ordenes_sin_aprobar();

        },
        error: function(data) {
            alert(data);
        }
    });
}
