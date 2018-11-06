/**
 * Created by diseraca on 4/05/15.
 */

function ordenes_pendientes(){
    $.ajax({
            type: 'GET',
            url: 'ordenes_sin_terminar',
            data: '',
            success: function (data) {
                if (data.length == 0)
                {
                    UIkit.notify({
                        message : 'No se tienen ordenes de servicio asignadas',
                        status  : 'danger',
                        timeout : 3000,
                        pos:'top-center'
                    });
                    return;
                }
                html = '';

                $("#titulo_vista").html('Visualización de Ordenes');
                $("#etiqueta").html('Ordenes');
                $("#reorder").html('<i class="icon-reorder"></i> Visualización Ordenes');
                $("#menu").html("");

                tabla = '<div id="lista_orden"><table class="table table-hover">';
                thead = '<thead>    <tr>   <th>Orden</th> <th>Fecha Orden</th> <th>Empresa</th> <th>Total</th> <th>Ver</th> <th>Terminar</th> </tr> </thead>';
                tbody = '<tbody id="body_orden"> </tbody> </table> </div>';
                tabla += thead + tbody;

                $("#formularios").html(tabla);

                for(var i=0; i<data.length; i++)
                {
                    get_empresa(data[i]);
                }

                $("#body_orden").html(html);

            },
            error: function(data) {
                alert(data);
            }
        });
}

function get_empresa(dd){
    $.ajax({
        type: 'GET',
        url: 'get_empresa',
        data: {'id':dd.fields.empresa},
        success: function (data) {
            if (data != 'error')
            {
                codigo_orden = '<th>'+dd.pk+'</th>';
                fecha_orden = '<th>'+dd.fields.fecha_orden+'</th>';
                empresa = '<th>'+data+'</th>';
                total = '<th>'+dd.fields.total+'</th>';
                ver = '<th><button class="btn btn-danger" onclick="ver_ensayos('+dd.pk+')" type="button">Ver</button></th>';
                terminar = '<th><button class="btn btn-danger" onclick="terminar_orden('+dd.pk+')" type="button">Terminar</button></th>';
                fila = '<tr>'+codigo_orden+fecha_orden+empresa+total+ver+terminar+'</tr>';
                $('#body_orden').append(fila);
            }
        },
        error: function(data) {
            alert(data);
        }
    });
}

function ver_ensayos(orden){
    $.ajax({
            type: 'GET',
            url: 'ordenes_ensayo',
            data: {'id':orden},
            success: function (data) {

                html = '';

                $("#titulo_vista").html('Visualización de Ensayos de la Ordenes '+orden);
                $("#etiqueta").html('Ensayos');
                $("#reorder").html('<i class="icon-reorder"></i> Visualización y Edición de Ensayos');
                $("#menu").html("");

                tabla = '<div id="lista_ensayos"><table class="table table-hover">';
                thead = '<thead>    <tr>   <th>Cod Ensayo</th> <th>Descripción</th> <th>Hechas</th> <th>Totales</th> <th>Nuevo Resultado</th> <th>Ver Resultados</th>  </tr> </thead>';
                tbody = '<tbody id="body_ensayos"> </tbody> </table> </div>';
                tabla += thead + tbody +'</br><div id="resultados"></div>';

                $("#formularios").html(tabla);

                for(var i=0; i<data.length; i++)
                {
                    get_ensayo(data[i]);
                }

            },
            error: function(data) {
                alert(data);
            }
        });
}

function get_ensayo(dd){
    $.ajax({
        type: 'GET',
        url: 'get_ensayo',
        data: {'id':dd.fields.ensayo},
        success: function (data) {
            if (data != 'error')
            {
                ensayo = data.split(',');

                codigo_ensayo = '<th>'+ensayo[2]+'</th>';
                descripcion = '<th>'+ensayo[1]+'</th>';
                hechas = '<th>'+dd.fields.hechas+'</th>';
                totales = '<th>'+dd.fields.cantidad+'</th>';
                agregar = '<th>';
                if (dd.fields.hechas != dd.fields.cantidad && ensayo[2] != '000')
                {
                    agregar += '<button class="btn btn-danger" onclick="nuevo_resultado('+dd.pk+',\''+ensayo[2]+'\')" type="button">Nuevo</button>';
                }
                agregar += '</th>';

                if(ensayo[2] != '000')
                    ver = '<th><button class="btn btn-danger" onclick="ver_resultados('+dd.pk+',\''+ensayo[2]+'\', this)" type="button">Ver</button> </th>';
                else
                    ver = '<th></th>';

                fila = '<tr>'+codigo_ensayo+descripcion+hechas+totales+agregar+ver+'</tr>';
                $("#body_ensayos").append(fila);

            }
        },
        error: function(data) {
            alert(data);
        }
    });
}

function nuevo_resultado(ensayo_orden, ensayo){

    //se debe mirar de que tipo de ensayo es para poder enviarlo al formulario de registro de muestras.
    //aguas

    orden_editar = ensayo_orden;
    console.log(ensayo);
    //235 --> ensayo


    if (ensayo==235)
        $("#formularios").load( "../static/html/ensayos/compresion_concreto.html");
    else
        alert('no hay, formulario para este ensayo');
}

function ver_resultados(ensayo_orden, ensayo, boton){

    tabla = '</br><table class="table table-hover">';
    thead = '<thead><tr> <th>Codigo</th> <th>Obra</th> <th>Elemento</th> <th>N° de Ensayos</th> <th>Codigo de Verificación</th> <th>Imprimir</th> </tr> </thead>';
    tbody = '<tbody id="body_resultados"></tbody></table>';
    tabla += thead + tbody;

    $("#resultados").html(tabla);

    $('btn-success').attr('class', 'btn btn-danger');

    $(boton).removeAttr('class');
    $(boton).attr('class', 'btn btn-success');

    if (ensayo == 235){
        $.ajax({
            type: 'GET',
            url: 'resultados_compresion_concreto',
            data: {'orden':ensayo_orden},
            success: function (data) {
                //console.log(data);
                for(var i=0; i<data.length; i++)
                {
                    codigo = '<th>'+data[i].pk+'</th>';
                    obra = '<th>'+data[i].fields.obra+'</th>';
                    elemento = '<th>'+data[i].fields.elemento+'</th>';
                    n_ensayos = '<th>'+data[i].fields.n_ensayo+'</th>';
                    verificacion = '<th>'+data[i].fields.codigo_verificacion+'</th>';
                    imprimir = '<th><a href="imprimir_resultado_cc?id='+data[i].pk+'" target="_blank" class="btn-danger">imprimir</a></th>';

                    fila = '<tr>'+ codigo+obra+elemento+n_ensayos+verificacion+imprimir+'</tr>';
                    $("#body_resultados").append(fila);
                }
            },
            error: function(data) {
                alert(data);
            }
        });
    }
    else
        alert('no hay mas formatos hechos');
}

