# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [ url(r'^$', views.index),
                url(r'^login$', views.inicio),
                url(r'^sesion$', views.sesion),
                url(r'^logout$', views.cerrar),
                url(r'^fecha_hora$', views.fecha_hora),

                # laboratorios
                url(r'^get_laboratorio$', views.get_laboratorio),
                url(r'^get_nombre_lab', views.get_nombre_lab),

                # usuario
                url(r'^add_user$', views.add_user),
                url(r'^set_pass$', views.set_pass),
                url(r'^listado_user$', views.listado_user),
                url(r'^restaurar_pass$', views.restaurar_pass),
                url(r'^desactivar_user$', views.desactivar_user),
                url(r'^activar_user$', views.activar_user),
                url(r'^get_user_codigo$', views.get_user_codigo),
                url(r'^get_user$', views.get_user),
                url(r'^editar_user$', views.editar_user),

                # imagenes y firmas
                #url(r'^add_foto$', views.add_foto),
                #url(r'^add_firma$', views.add_firma),
                #url(r'^get_user_firma$', views.get_user_firma),

                #convenios  add_convenio
                url(r'^add_convenio$', views.add_convenio),

                #cotizacion
                url(r'^lista_ensayo_cotizacion$', views.lista_ensayo_cotizacion),
                url(r'^cotizacion_pdf_lab$', views.cotizacion_pdf_lab),
                url(r'^cotizacion_pdf_admin$', views.cotizacion_pdf_admin),


                #adelantos
                url(r'^add_adelanto$', views.add_adelanto),
                url(r'^get_adelantos_orden$', views.get_adelantos_orden),

                # Empresas
                url(r'^add_empresa$', views.add_persona),
                url(r'^listado_empresas$', views.listado_personas),
                url(r'^get_empresa_identificacion$', views.get_persona_identificacion),
                url(r'^listado_empresa_id$', views.listado_persona_id),
                url(r'^get_empresa_id_nombre$', views.get_persona_id_nombre),

                # ensayos
                url(r'^add_ensayo$', views.add_ensayo),
                url(r'^listado_ensayos$', views.listado_ensayos),
                url(r'^get_ensayo$', views.get_ensayo),
                url(r'^editar_ensayo$', views.editar_ensayo),
                url(r'^lista_ensayo_laboratorio$', views.lista_ensayo_laboratorio),
                url(r'^get_ensayo_id$', views.get_ensayo_id),
                url(r'^get_ensayos_orden$', views.get_ensayos_orden),

                # orden
                url(r'^add_orden$', views.add_orden),
                url(r'^orden_empresa$', views.orden_persona),
                url(r'^orden_con_num$', views.orden_con_num),
                url(r'^orden_para_editar$', views.orden_para_editar),
                url(r'^editar_orden$', views.editar_orden),
                url(r'^imprimir_orden$', views.imprimir_orden),
                url(r'^aprobar_orden$', views.aprobar_orden),
                url(r'^ordenes_sin_aprobacion$', views.ordenes_sin_aprobacion),
                url(r'^ordenes_aprobadas_no_impresas$', views.ordenes_aprobadas_no_impresas),
                url(r'^imprimir_pendiente$', views.imprimir_pendiente),
                url(r'^anular_orden$', views.anular_orden),

                # ordenes, laboratorios
                url(r'^ordenes_sin_terminar$', views.ordenes_sin_terminar),
                url(r'^ordenes_ensayo$', views.ordenes_ensayo),
                url(r'^get_ensayo_lab$', views.get_ensayo_lab),
                url(r'^get_empresa_lab$', views.get_persona_lab),
                url(r'^terminar_orden$', views.terminar_orden),
                url(r'^ordenes_terminadas$', views.ordenes_terminadas),

                # ensayos de agua
                url(r'^get_ensayos_agua$', views.get_ensayos_agua),
                url(r'^add_resultado_aguas$', views.add_resultado_aguas),
                url(r'^get_resultados_orden_aguas$', views.get_resultados_orden_aguas),
                url(r'^imprimir_resultado_aguas$', views.imprimir_resultado_aguas),
                url(r'^get_resultado_editar_aguas$', views.get_resultado_editar_aguas),
                url(r'^get_ensayos_resultado_editar_aguas$', views.get_ensayos_resultado_editar_aguas),
                url(r'^editar_resultado_aguas$', views.editar_resultado_aguas),

                # ensayos de nutricion animal
                url(r'^add_resultado_nutricion$', views.add_resultado_nutricion),
                url(r'^get_resultados_orden_nutricion$', views.get_resultados_orden_nutricion),
                url(r'^imprimir_resultado_nutricion$', views.imprimir_resultado_nutricion),
                url(r'^get_ensayos_resultado_editar_nutricion$', views.get_ensayos_resultado_editar_nutricion),
                url(r'^get_resultado_editar_nutricion$', views.get_resultado_editar_nutricion),
                url(r'^get_metodos_ensayo$', views.get_metodos_ensayo),
                url(r'^editar_resultado_nutricion$', views.editar_resultado_nutricion),

                # ensayos de suelos agricolas
                url(r'^add_resultado_suelos_agricolas$', views.add_resultado_suelos_agricolas),
                url(r'^get_resultados_orden_suelos_agricolas$', views.get_resultados_orden_suelos_agricolas),
                url(r'^imprimir_resultado_agricolas$', views.imprimir_resultado_agricolas),
                url(r'^get_resultado_editar_sa$', views.get_resultado_editar_sa),
                url(r'^editar_resultado_sa$', views.editar_resultado_sa),


                url(r'^msg_correo$', views.msg_correo),

                # anulación de resultado
                url(r'^buscar_resultado$', views.buscar_resultado),
                url(r'^anular_resultado$', views.anular_resultado),


                # resistencia de materiales.
                url(r'^resistencia_materiales$', views.resistencia_materiales),
                url(r'^add_traccion_acero$', views.add_traccion_acero),


                #suelos civiles
                url(r'^suelos_civiles$', views.suelos_civiles),



                ]
