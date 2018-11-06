/**
 * Created by wolf on 25/08/16.
 */


function cotizacion() {
    $("#titulo_vista").html('Registro de cotización');
    $("#etiqueta").html('Registro de cotización');
    $("#reorder").html('<i class="icon-reorder"></i> Registro de cotización');
    $("#formularios").load( "../static/html/cotizacion/cotizacion_admin.html");
}
