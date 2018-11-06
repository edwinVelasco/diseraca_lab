function nuevo_resultado_suelos(ensayo_orden){
    orden_editar = ensayo_orden;
    $("#formularios").load( "../static/html/suelos_agricolas/lab_suelos_agricolas.html");
}


function ver_ensayos_suelos(orden){
    $.ajax({
        type: 'GET',
        url: 'get_resultados_orden_suelos_agricolas',
        data: {'orden':orden},
        success: function (data) {
            //'codigo', 'municipio', 'identificacion', 'fecha', 'tipo_muestra'

            if (data.length == 0)
            {
                UIkit.notify({
                    message : 'No hay muestras de resultados para esta Orden: '+orden,
                    status  : 'danger',
                    timeout : 4000,
                    pos:'top-center'
                });
                return;
            }

            tabla = '<br/><div id="lista_resultados_agricolas"><h2>Reporte de Analisis de la Orden: '+orden+'</h2><br/><br/><table class="table table-hover">';
            thead = '<thead>    <tr>  <th>Propietario</th> <th>Vereda</th> <th>Finca</th> <th>Lote</th> <th>Cultivo</th> <th>Imprimir</th> <th>Editar</th> </tr> </thead>';
            tbody = '<tbody id="body_lista_resultados_agricolas"> </tbody> </table> </div>';

            tabla = tabla+thead+tbody;

            $("#lista_reportes").html(tabla);

            for (i=0;i< data.length; i++)
            {
                propietario = '<th>'+data[i].fields.propietario+'</th>';
                vereda = '<th>'+data[i].fields.vereda+'</th>';
                finca = '<th>'+data[i].fields.finca+'</th>';
                lote = '<th>'+data[i].fields.lote+'</th>';
                cultivo = '<th>'+data[i].fields.cultivo+'</th>';
                imprimir = '<th><a href="imprimir_resultado_agricolas?id='+data[i].pk+'" target="_blank" class="btn-danger">imprimir</a></th>';
                editar = '<th><button class="btn btn-danger" onclick="editar_resultado_suelos('+data[i].pk+')" type="button">Editar</button></th>';
                fila = '<tr>'+propietario+vereda+finca+lote+cultivo+imprimir+editar+'</tr>';
                $('#body_lista_resultados_agricolas').append(fila);
            }
        },
        error: function(data) {
            alert(data);
        }
    });

}


function terminar_orden(orden){
    var r = confirm("Desea Terminar la Orden, recuerde que no se puede retroceder a esta accción?");
    if (r == true) {
        $.ajax({
            type: 'GET',
            url: 'terminar_orden',
            data: {'id':orden},
            success: function (data) {
                if (data === 'ok'){
                    UIkit.notify({
                        message : 'Orden: '+orden_editar+' Terminada con exito',
                        status  : 'success',
                        timeout : 3000,
                        pos:'top-center'
                    });
                    window.location ='sesion'

                }
                else if (data === 'not'){
                    UIkit.notify({
                        message : 'No se puede terminar la orden: '+orden+', Aún tiene ensayos por hacer',
                        status  : 'danger',
                        timeout : 4000,
                        pos:'top-center'
                    });
                }
                else{
                    UIkit.notify({
                        message : 'Orden: '+orden+' terminada con exito, pero no se pudo enviar el correo',
                        status  : 'warning',
                        timeout : 4000,
                        pos:'top-center'
                    });
                    window.location ='sesion'
                }
            },
            error: function(data) {
                alert(data);
            }
        });
    }
}


function editar_resultado_suelos(resultado){
    orden_editar = resultado;
    $("#formularios").load( "../static/html/suelos_agricolas/editar_resultado.html");
}


function ordenes_terminadas_suelos(){
    $.ajax({
            type: 'GET',
            url: 'ordenes_terminadas',
            data: '',
            success: function (data) {
                if (data.length == 0)
                {
                    UIkit.notify({
                        message : 'No se tienen ordenes terminadas en el lapso de 15 dias',
                        status  : 'danger',
                        timeout : 3000,
                        pos:'top-center'
                    });
                    $("#formularios").html('');
                    return;
                }
                html = '';

                $("#titulo_vista").html('Visualización de Ordenes de Servicio Terminadas en el Lapso de 15 Dias');
                $("#etiqueta").html('Ordenes');
                $("#reorder").html('<i class="icon-reorder"></i> Visualización Ordenes');
                $("#menu").html("");

                tabla = '<div id="lista_orden"><table class="table table-hover">';
                thead = '<thead>    <tr>   <th>Orden</th> <th>Fecha Orden</th> <th>Empresa</th> <th>Total</th> <th>Ver Resultado</th></tr> </thead>';
                tbody = '<tbody id="body_orden"> </tbody> </table> </div>';
                tabla += thead + tbody;

                $("#formularios").html(tabla);

                for(var i=0; i<data.length; i++)
                {
                    //get_empresa_agua(data[i]);
                }

            },
            error: function(data) {
                alert(data);
            }
        });
}


function cotizacion() {
    $("#formularios").load( "../static/html/cotizacion/cotizacion.html");
}