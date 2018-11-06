/**
 * Created by wolf on 28/10/16.
 */
function buscar_resultado() {
    $("#titulo_vista").html('Resultados');
    $("#etiqueta").html('Busqueda de resultados');
    $("#reorder").html('<i class="icon-reorder"></i> Busqueda de Resultados');
    $("#formularios").load( "../static/html/buscar_resultados/buscar.html");
}

function anular_resultado(busqueda){
    $.ajax({
        type: 'GET',
        url: 'anular_resultado',
        data: {'busqueda':busqueda},
        success: function (data) {
            UIkit.notify({
                message : data,
                status  : 'success',
                timeout : 3000,
                pos:'top-center'
            });
            buscar_resultado();
        },
        error: function(data) {
            alert(data);
        }
    });
    return false;
}