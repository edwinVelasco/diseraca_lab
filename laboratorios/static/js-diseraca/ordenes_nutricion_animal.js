/**
 * Created by edwin on 9/11/15.
 */

function nuevo_resultado_nutricion(ensayo_orden){
    orden_editar = ensayo_orden;
    $("#formularios").load( "../static/html/nutricion_animal/lab_nutricion.html");
}


function terminar_orden(orden){
    var r = confirm("Desea Terminar la Orden, recuerde que no se puede retroceder a esta accción?");
    if (r == true) {
        $.ajax({
            type: 'GET',
            url: 'terminar_orden',
            data: {'id':orden},// tipo = a--> aguas,  m--> resistencia de materiales
            success: function (data) {
                if (data === 'ok'){
                    UIkit.notify({
                        message : 'Orden: '+orden_editar+' Terminada con exito',
                        status  : 'success',
                        timeout : 3000,
                        pos:'top-center'
                    });
                    window.location='sesion';
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
                    window.location='sesion';
                }
            },
            error: function(data) {
                alert(data);
            }
        });
    }
}


function ver_resultado_nutricion(orden){
    $.ajax({
        type: 'GET',
        url: 'get_resultados_orden_nutricion',
        data: {'orden':orden},
        success: function (data) {
            //'codigo', 'fecha', 'tipo'

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

            tabla = '<br/><div id="lista_resultados_nutricion"><h2>Reporte de Analisis de la Orden: '+orden+'</h2><br/><br/><table class="table table-hover">';
            thead = '<thead>    <tr>  <th>Fecha</th> <th>Codigo de muestra</th> <th>Tipo muestra</th> <th>Imprimir</th> <th>Editar</th> </tr> </thead>';
            tbody = '<tbody id="body_lista_resultados_nutricion"> </tbody> </table> </div>';

            tabla = tabla+thead+tbody;

            $("#lista_reportes").html(tabla);

            for (i=0;i< data.length; i++)
            {
                fecha = '<th>'+data[i].fields.fecha+'</th>';
                codigo = '<th>'+data[i].fields.codigo+'</th>';
                tipo = '<th>'+data[i].fields.tipo+'</th>';
                imprimir = '<th><a href="imprimir_resultado_nutricion?id='+data[i].pk+'" target="_blank" class="btn btn-danger">Imprimir</a></th>';
                editar = '<th><button class="btn btn-danger" onclick="editar_resultado_nutricion('+data[i].pk+')" type="button">Editar</button></th>';
                fila = '<tr>'+fecha+codigo+tipo+imprimir+editar+'</tr>';
                $('#body_lista_resultados_nutricion').append(fila);
            }
        },
        error: function(data) {
            alert(data);
        }
    });
}


function editar_resultado_nutricion(resultado){
    orden_editar = resultado;
    $("#formularios").load( "../static/html/nutricion_animal/editar_lab_nutricion.html");
}


function cotizacion() {
    $("#formularios").load( "../static/html/cotizacion/cotizacion.html");
}