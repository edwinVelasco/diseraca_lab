function pass() {
          //cambia el texto de id = "titulo_vista",  id"etiqueta" id="reorder"
          // el menu va en el div id="menu"
          $("#titulo_vista").html('Cambio de Contraseña');
          $("#etiqueta").html('Contraseña');
          $("#reorder").html('<i class="icon-reorder"></i> edicion de contraseña');
          $( "#menu" ).html('');
          //$("#menu").load( "../static/html/menu_usuario.html");
      }
function cambio_pass()
       {
           pass(); //empresa se encarga de cambiar los titulos.y colocar el menu de los botones registrar, edicion y busqueda
           $("#formularios").load( "../static/html/usuarios/cambiar_pass.html");
       }