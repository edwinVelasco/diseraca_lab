# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core import serializers
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from laboratorios.models import *
from django.db import IntegrityError
import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import TableStyle, Table, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
import os
from threading import Thread

# esta ruta se utiliza para sacar la img de fondo y el logo de la ufps que va en los pdf's
ruta_view = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def msg_correo(request):
    return render(request, 'laboratorios/orden_terminada_correo.html',
                  {'orden': 4123, 'lab': 'nutricion animal y analisis de alimentos'.encode('utf-8')})


# Create your views here.
def index(request):
    '''para tomas la ip del cliente'''
    # x = request.META['HTTP_X_FORWARDED_FOR'].split(',')
    # #print x[0]
    #print request
    return render(request, 'laboratorios/index.html')


def inicio(request):
    if request.method == 'POST' and 'input-username' in request.POST and 'input-password' in request.POST:
        username = request.POST['input-username']
        password = request.POST['input-password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['usuario'] = username
                return HttpResponse('a')
            else:
                return HttpResponse('des')
        else:
            return HttpResponse('login')


@login_required(login_url='/')
def sesion(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(user__username=request.session['usuario'])
        if persona.tipo == 2:
            if persona.laboratorio_id == 4:
                ordenes = Orden.objects.filter(laboratorio__id=4, aprobacion=True, terminada='0')
                return render(request, 'laboratorios/aguas.html', {'usuario': persona.user.first_name,
                                                                   'pendientes': ordenes})
            elif persona.laboratorio_id == 5:
                ordenes = Orden.objects.filter(laboratorio__id=5, aprobacion=True, terminada='0')
                return render(request, 'laboratorios/nutricion_animal.html', {'usuario': persona.user.first_name,
                                                                              'pendientes': ordenes})
            elif persona.laboratorio_id == 6:
                ordenes = Orden.objects.filter(laboratorio__id=6, aprobacion=True, terminada='0')
                return render(request, 'laboratorios/suelos_agricolas.html', {'usuario': persona.user.first_name,
                                                                              'pendientes': ordenes})
            elif persona.laboratorio_id == 2:
                return HttpResponseRedirect('/resistencia_materiales')

            elif persona.laboratorio_id == 1:
                return HttpResponseRedirect('/suelos_civiles')

        elif persona.tipo == 0:
            return render(request, 'laboratorios/administrador.html', {'usuario': persona.user.first_name})

        elif persona.tipo == 1:
            return render(request, 'laboratorios/jefe.html', {'usuario': persona.user.first_name})

        else:
            return HttpResponseRedirect('logout')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def cerrar(request):
    if request.user.is_authenticated():
        del request.session['usuario']
        logout(request)
    return HttpResponseRedirect('/')


def fecha_hora(request):
    if request.method == 'GET':
        fecha_hora = datetime.datetime.now()
        salida = '%s/%s/%s - %s:%s' % (
        getattr(fecha_hora, 'year'), getattr(fecha_hora, 'month'), getattr(fecha_hora, 'day'),
        getattr(fecha_hora, 'hour'), getattr(fecha_hora, 'minute'))
        return HttpResponse(salida)
    else:
        return Http404

# ---------------------Crud Laboratorios-----------------

def get_laboratorio(request):
    if request.method == 'GET':
        laboratorios = Tipo_Laboratorio.objects.all()
        data = serializers.serialize('json', laboratorios, fields=('nombre'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404  # redirect('/')


def get_nombre_lab(request):
    if request.method == 'GET':
        lab = Tipo_Laboratorio.objects.get(id=request.GET['id'])
        return HttpResponse(lab.nombre.encode('utf-8'))


# ---------------------Fin Crud Laboratorios-----------------

# ---------------------Crud User-----------------
@login_required(login_url='/')
def add_user(request):
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(user__username=request.POST['codigo'])
            return HttpResponse('ya')
        except Persona.DoesNotExist:
            if request.POST['tipo'] == 'n' or request.POST['laboratorio'] == '0':
                return HttpResponse('not')

            user = User()
            user.username = request.POST['codigo']
            user.first_name = request.POST['nombre']
            user.email = request.POST['email']
            user.set_password(request.POST['codigo'])
            user.save()
            persona = Persona()
            persona.user = user
            persona.telefono = request.POST['telefono']
            persona.laboratorio = Tipo_Laboratorio.objects.get(id=request.POST['laboratorio'])
            if int(request.POST['tipo']) == 2:
                persona.encargado = True

            elif int(request.POST['tipo']) == 1:
                otros = Persona.objects.filter(tipo=1)
                for o in otros:
                    o.user.is_active = False
                    o.save()

            persona.tipo = int(request.POST['tipo'])
            persona.save()
            return HttpResponse('ok')

    else:
        return Http404


@login_required(login_url='/')
def editar_user(request):
    if request.method == 'POST':
        try:
            if request.POST['tipo'] == 'n' or request.POST['laboratorio'] == '0':
                return HttpResponse('not')
            persona = Persona.objects.get(id=request.POST['id'])
            persona.user.first_name = request.POST['nombre']
            persona.telefono = request.POST['telefono']
            persona.user.username = request.POST['codigo']
            persona.user.email = request.POST['email']
            persona.laboratorio_id = int(request.POST['laboratorio'])
            persona.tipo = int(request.POST['tipo'])
            if int(request.POST['tipo']) == 2:
                persona.encargado = True
            elif int(request.POST['tipo']) == 1:
                otros = Persona.objects.filter(tipo=1)
                for o in otros:
                    o.user.is_active = False
                    o.save()

            persona.user.save()
            persona.save()

            return HttpResponse('ok')
        except Persona.DoesNotExist:
            return HttpResponse('error')

    else:
        return Http404


@login_required(login_url='/')
def desactivar_user(request):
    if request.method == 'GET':
        try:
            persona = Persona.objects.get(id=request.GET['id'])
            persona.user.is_active = False
            persona.user.save()
            return HttpResponse('ok')  # usuario desactivado
        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


@login_required(login_url='/')
def activar_user(request):
    if request.method == 'GET':
        try:
            persona = Persona.objects.get(id=request.GET['id'])
            persona.user.is_active = True
            persona.user.save()
            return HttpResponse('ok')  # usuario desactivado
        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


@login_required(login_url='/')
def get_user_codigo(request):
    if request.method == 'GET':
        try:
            persona = Persona.objects.get(user__username=request.GET['codigo'])
            salida = '%s,%s,%s,%s,%s' % (
            persona.id, persona.user.first_name, persona.user.username, persona.user.email, persona.user.is_active)
            return HttpResponse(salida)

        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


@login_required(login_url='/')
def get_user(request):
    if request.method == 'GET':
        try:
            if 'id' in request.GET:
                persona = Persona.objects.get(id=request.GET['id'])
                salida = '%s,%s,%s,%s,%s,%s,%s,%s' % (
                persona.id, persona.user.first_name.encode('utf-8'), persona.user.username, persona.telefono, persona.user.email,
                persona.tipo, persona.laboratorio.id, persona.encargado)
                return HttpResponse(salida)
            else:
                return HttpResponse('mal')
        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


@login_required(login_url='/')
def set_pass(request):
    if request.method == 'POST':
        if 'antigua' in request.POST and 'nueva' in request.POST and 'nuevaDos' in request.POST:
            user = authenticate(username=request.session['usuario'], password=request.POST['antigua'])
            if user is not None:
                if request.POST['nueva'] == request.POST['nuevaDos']:
                    user.set_password(request.POST['nueva'])
                    user.save()
                    return HttpResponse('ok')
                else:
                    return HttpResponse('nueva')  # las contrasenas nuevas no concuerdan
            else:
                return HttpResponse('antigua')  # la contrasena a cambiar no es la correcta
        else:
            # no estan los datos en el request
            return HttpResponse('not')
    else:
        return Http404
        # no es un POST


def listado_user(request):
    if request.method == 'GET':
        usuarios = User.objects.order_by('username')
        data = serializers.serialize('json', usuarios, fields=('username', 'first_name', 'email', 'is_active'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


def restaurar_pass(request):
    if request.method == 'GET':
        try:
            persona = Persona.objects.get(id=request.GET['id'])
            persona.user.set_password(persona.user.username)
            persona.user.save()
            return HttpResponse('ok')
        except Persona.DoesNotExist:
            return HttpResponse('not')
    else:
        return Http404


def get_user_firma(request):
    if request.method == 'GET':
        personas = Persona.objects.filter(encargado=True, tipo=1)
        data = serializers.serialize('json', personas, fields=('nombre', 'codigo'))
        return HttpResponse(data, content_type='application/json')


# --------------------- Fin Crud User-----------------

# ---------------------Crud persona-----------------

def add_persona(request):
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(user__username=request.POST['identificacion'])
            return HttpResponse('ya')  # significa que la persona ya fue creada con anterioridad
        except Persona.DoesNotExist:
            user = User()
            user.username = request.POST['identificacion']
            user.first_name = request.POST['nombre']
            user.email = request.POST['email']
            user.set_password(request.POST['identificacion'])
            user.save()

            persona = Persona()
            persona.user = user
            persona.direccion = request.POST['direccion']
            persona.telefono = request.POST['telefono']
            persona.tipo = 4
            persona.laboratorio_id = 9
            persona.save()
            return HttpResponse('ok')
    else:
        return Http404


def get_persona_identificacion(request):
    if request.method == 'GET':
        try:
            if 'codigo' in request.GET:
                persona = Persona.objects.get(user__username=request.GET['codigo'])
                salida = '%s,%s,%s,%s,%s,%s' % (
                persona.id, persona.user.first_name, persona.user.username, persona.telefono, persona.user.email, persona.direccion)
                return HttpResponse(salida.encode('utf-8'))
            else:
                return HttpResponse('mal')
        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


def get_persona_id_nombre(request):
    if request.method == 'GET':
        persona = Persona.objects.get(id=request.GET['id'])
        return HttpResponse(persona.user.first_name.encode('utf-8'))


def get_persona(request):
    if request.method == 'GET':
        try:
            if 'id' in request.GET:
                persona = Persona.objects.get(id=request.GET['id'])
                salida = '%s,%s,%s,%s,%s,%s' % (
                persona.id, persona.user.first_name, persona.user.username, persona.telefono, persona.user.email, persona.tipo)
                return HttpResponse(salida)
            else:
                return HttpResponse('mal')
        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


def get_persona_lab(request):
    if 'id' in request.GET:
        try:
            persona = Persona.objects.get(id=request.GET['id'])
            return HttpResponse(persona.user.first_name)
        except Persona.DoesNotExist:
            return HttpResponse('error')
    else:
        return HttpResponseRedirect('logout')


def listado_personas(request):
    if request.method == 'GET':
        personas = User.objects.all()
        data = serializers.serialize('json', personas, fields=('first_name', 'username'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


def listado_persona_id(request):
    if request.method == 'GET':
        personas = User.objects.all()
        data = serializers.serialize('json', personas, fields=('username'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


# falta el editar persona

# ---------------------Fin Crud persona-----------------


# ---------------------Crud Ensayo-----------------
def add_ensayo(request):
    if request.method == 'POST':
        if 'descripcion' in request.POST and 'valor' in request.POST and 'metodo' in request.POST and 'codigo' in request.POST and 'unidad' in request.POST:  # 'laboratorio' in request.POST:

            # if request.POST['formulario'] == '0':
            #   return HttpResponse('error')# cuando algo en el formulario esta mal
            try:
                ensayo = Ensayo.objects.get(codigo=request.POST['codigo'])
                return HttpResponse('ya')  # significa que el ensayo ya fue creado con anterioridad
            except Ensayo.DoesNotExist:
                ensayo = Ensayo()
                # ensayo.formulario = request.POST['formulario']
                en = request.POST['codigo'][0:2]

                try:
                    ensayo.laboratorio = Tipo_Laboratorio.objects.get(id=int(en))
                    ensayo.descripcion = request.POST['descripcion']
                    ensayo.valor = request.POST['valor']
                    ensayo.codigo = request.POST['codigo']
                    ensayo.metodo = request.POST['metodo']
                    ensayo.unidad = request.POST['unidad']

                    if 'acreditado' in request.POST:
                        ensayo.acreditado = True

                    ensayo.save()
                    return HttpResponse('ok')  # significa que el ensayo fue creado con exito
                except Tipo_Laboratorio.DoesNotExist:
                    return HttpResponse('lab')  # significa que el codigo del laboratorio no existe

    else:
        return Http404


def get_ensayo(request):

    if request.method == 'GET':
        try:
            if 'codigo' in request.GET:
                ensayo = Ensayo.objects.get(codigo=request.GET['codigo'])
                salida = '%s,%s,%s,%s,%s,%s,%s' % (
                ensayo.id, ensayo.codigo, ensayo.descripcion, ensayo.valor, ensayo.unidad, ensayo.metodo,
                ensayo.acreditado)
                return HttpResponse(salida)
            else:
                return HttpResponse('mal')

        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


def get_ensayo_lab(request):
    if 'id' in request.GET:
        try:
            ensayo = Ensayo.objects.get(id=request.GET['id'])
            salida = '%s,%s,%s,%s,%s' % (ensayo.id, ensayo.descripcion, ensayo.codigo, ensayo.metodo, ensayo.unidad)
            return HttpResponse(salida)
        except Ensayo.DoesNotExist:
            return HttpResponse('error')  # no existe el ensayo
    else:
        return HttpResponseRedirect('logout')


def listado_ensayos(request):
    if request.method == 'GET':
        ensayo = Ensayo.objects.all()
        data = serializers.serialize('json', ensayo, fields=('descripcion', 'codigo', ''))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


# retorna los ensayos del laboratorio enviado a la views
def lista_ensayo_laboratorio(request):
    if request.method == 'GET':
        #print request.GET['laboratorio']
        if request.GET['laboratorio'] == 'a':
            return HttpResponse('mal')  # se debe informar en el navegador que se seleccione un tipo de laboratorio.

        laboratorio = Tipo_Laboratorio.objects.get(id=request.GET['laboratorio'])
        ensayo = Ensayo.objects.filter(laboratorio=laboratorio)

        data = serializers.serialize('json', ensayo, fields=('descripcion', 'valor', 'codigo'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


def editar_ensayo(request):
    if request.method == 'POST':
        if 'id' in request.POST and 'descripcion' in request.POST and 'valor' in request.POST and 'metodo' in request.POST and 'codigo' in request.POST and 'unidad' in request.POST:  # 'laboratorio' in request.POST:
            try:

                # if request.POST['laboratorio'] == '0' or request.POST['formulario'] == '0':
                #   return HttpResponse('not')

                ensayo = Ensayo.objects.get(id=request.POST['id'])

                en = request.POST['codigo'][0:2]

                ensayo.laboratorio = Tipo_Laboratorio.objects.get(id=int(en))
                ensayo.descripcion = request.POST['descripcion']
                ensayo.valor = request.POST['valor']
                ensayo.codigo = request.POST['codigo']
                ensayo.metodo = request.POST['metodo']
                ensayo.unidad = request.POST['unidad']
                if 'acreditado' in request.POST:
                    ensayo.acreditado = True

                ensayo.save()
                return HttpResponse('ok')

            except Ensayo.DoesNotExist:
                return HttpResponse('error')
        else:
            return HttpResponse('not')
    else:
        return Http404

    # retorna los ensayos de un 'laboratorio' y que no tengan formulario
    # def get_ensayo_orden(request):
    # if request.method == 'GET':


def get_ensayo_id(request):  # retorna el ensayo que no tiene formulario deacuerdo al laboratorio
    if request.method == 'GET':
        try:
            if 'id' in request.GET:
                ensayo = Ensayo.objects.get(id=request.GET['id'])
                salida = '%s,%s' % (ensayo.codigo, ensayo.descripcion)
                return HttpResponse(salida)
            else:
                return HttpResponse('mal')

        except Persona.DoesNotExist:
            return HttpResponse('not')  # usuario no encontrado
    else:
        return Http404


def get_ensayos_orden(request):  # retorna los ensayos agregados en una orden
    if request.method == 'GET':
        orden = Orden.objects.get(id=request.GET['id'])
        orden_ensayos = Orden_Ensayo.objects.filter(orden=orden)

        data = serializers.serialize('json', orden_ensayos, fields=('subtotal', 'valor_uni', 'cantidad', 'ensayo'))
        return HttpResponse(data, content_type='application/json')

    else:
        return Http404


# ---------------------Fin Crud Ensayo-----------------


# ---------------------Crud Adelantos-----------------

def add_adelanto(request):
    if request.method == 'POST':
        adelanto = Adelanto()
        adelanto.persona = Persona.objects.get(user__username=request.POST['persona'])
        adelanto.consignacion = request.POST['consignacion']
        adelanto.total_consignado = request.POST['consignado']
        adelanto.saldo = request.POST['consignado']
        adelanto.hechas = 0
        adelanto.save()
        return HttpResponse("ok")


def get_adelantos_orden(request):
    if request.method == 'GET':
        persona = Persona.objects.get(user__username=request.GET['empresa'])
        adelantos = Adelanto.objects.filter(persona=persona).exclude(saldo=0)
        data = serializers.serialize('json', adelantos, fields=('consignacion', 'saldo', 'hechas'))
        return HttpResponse(data, content_type='application/json')


# ---------------------fin Crud Adelantos-------------


# ---------------------Crud convenio-----------------
def add_convenio(request):
    if request.method == 'POST':
        convenio = Convenio()
        convenio.persona = Persona.objects.get(user__username=request.POST['persona'])
        convenio.autorizo = request.POST['autorizo']
        convenio.fecha_aprovacion = request.POST['fecha_autorizacion']
        convenio.monto = request.POST['monto']
        convenio.save()
        return HttpResponse("ok")


# ---------------------fin Crud convenio-----------------


# ---------------------Crud Orden-----------------
def add_orden(request):
    if request.method == 'POST':
        if 'laboratorio' in request.POST and 'empresa' in request.POST and 'total' in request.POST and 'descuento' in request.POST:
            try:
                orden = Orden()
                lab = Tipo_Laboratorio.objects.get(id=request.POST['laboratorio'])
                orden.laboratorio = lab
                orden.persona = Persona.objects.get(user__username=request.POST['empresa'])
                orden.total = request.POST['total']
                orden.descuento = request.POST['descuento']
                orden.fecha_orden = datetime.date.today()

                jefes = Persona.objects.filter(tipo=1, user__is_active=True)
                orden.jefe = jefes[0].user.username

                if 'beneficiario' in request.POST:
                    orden.beneficiario = '1'

                if 'pendiente' in request.POST or request.POST['consignacion'] == '':
                    orden.pendiente = True

                orden.consignacion = request.POST['consignacion']

                consecutivo = Consecutivo_lab.objects.get(laboratorio=lab)
                if lab.id < 10:
                    if consecutivo.consecutivo < 10:
                        consecutivo_lab = '0' + str(lab.id) +'00000'+str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 100:
                        consecutivo_lab = '0' + str(lab.id) + '0000' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 1000:
                        consecutivo_lab = '0' + str(lab.id) + '000' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 10000:
                        consecutivo_lab = '0' + str(lab.id) + '00' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 100000:
                        consecutivo_lab = '0' + str(lab.id) + '0' + str(consecutivo.consecutivo)
                    else:
                        consecutivo_lab = '0' + str(lab.id) + str(consecutivo.consecutivo)
                else:
                    if consecutivo.consecutivo < 10:
                        consecutivo_lab = str(lab.id) + '00000' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 100:
                        consecutivo_lab = str(lab.id) + '0000' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 1000:
                        consecutivo_lab = str(lab.id) + '000' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 10000:
                        consecutivo_lab = str(lab.id) + '00' + str(consecutivo.consecutivo)
                    elif consecutivo.consecutivo < 100000:
                        consecutivo_lab = str(lab.id) + '0' + str(consecutivo.consecutivo)
                    else:
                        consecutivo_lab = str(lab.id) + str(consecutivo.consecutivo)

                orden.consecutivo_lab = consecutivo_lab
                consecutivo.consecutivo += 1
                consecutivo.save()
                orden.save()

                if request.POST['adelanto'] != "0":
                    adelanto = Adelanto.objects.get(id=request.POST['adelanto'])
                    adelanto.hechas += 1
                    adelanto.saldo -= int(orden.total)
                    adelanto.save()

                #orden = Orden.objects.latest('id')
                ensayos = int(request.POST['ensayos'])

                #se recoren los ensayos que se agregaron en el formulario i en el numero que completa el name que

                for i in range(ensayos):
                    if 'codigo_tb%d'%(i) in request.POST:
                        try:
                            orden_ensayo = Orden_Ensayo()
                            cantidad = 'cantidad_tb%d'%(i)
                            orden_ensayo.cantidad = request.POST[cantidad]
                            codigo = request.POST['codigo_tb%d'%(i)]
                            ensayo = Ensayo.objects.get(codigo=codigo)
                            orden_ensayo.ensayo = ensayo
                            orden_ensayo.acreditado = ensayo.acreditado
                            orden_ensayo.orden = orden
                            valor = 'valor_tb%d'%(i)
                            orden_ensayo.valor_uni = request.POST[valor]
                            subtotal = 'sub_tb%d'%(i)
                            orden_ensayo.subtotal = request.POST[subtotal]
                            orden_ensayo.save()
                        except Ensayo.DoesNotExist:
                            pass

                salida=orden.id

                if 'pendiente' in request.POST or request.POST['consignacion'] == '':
                    salida = str(salida)+',1'

                return HttpResponse(str(salida))

            except Persona.DoesNotExist:
                return HttpResponse('not persona')
            except Tipo_Laboratorio.DoesNotExist:
                return HttpResponse('not laboratorio')
        else:
            return HttpResponse('error form')


    else:
        return Http404


def anular_orden(request):
    if 'id' in request.POST:
        orden = Orden.objects.get(id=request.POST['id'])
        orden.terminada = '2'
        orden.save()
        try:
            anulacion = Anulacion_Orden()
            anulacion.orden = orden
            anulacion.motivo = request.POST['motivo']
            anulacion.usuario = request.POST['quien']
            anulacion.fecha = datetime.datetime.now()
            anulacion.save()

            enviar_correo_anulacion(orden, anulacion)
            return HttpResponse('ok')
        except IntegrityError:
            return HttpResponse('ya')


def editar_orden(request):
    if request.method == 'POST':
        if 'consignacion' in request.POST and 'num_factura' in request.POST and 'fecha_factura' in request.POST and 'observacion' in request.POST and 'id' in request.POST:
            orden = Orden.objects.get(id=request.POST['id'])
            orden.consignacion = request.POST['consignacion']
            if request.POST['fecha_factura'] != '':
                orden.fecha_factura = request.POST['fecha_factura']
            else:
                orden.fecha_factura = None

            orden.num_factura = request.POST['num_factura']
            orden.observacion = request.POST['observacion']
            orden.total = request.POST['total']
            orden.descuento = request.POST['descuento']
            if 'beneficiario' in request.POST:
                orden.beneficiario = '1'
            else:
                orden.beneficiario = '0'

            if 'factura' in request.POST:
                orden.requiere_factura = '1'
            else:
                orden.requiere_factura = '0'

            if 'pendiente' in request.POST:
                orden.pendiente = True
            else:
                orden.pendiente = False

            orden.save()
            orden_ensayos = Orden_Ensayo.objects.filter(orden=orden)

            for ensayo in orden_ensayos:
                cantida = 'cantidad_tb%s' % (ensayo.id)
                subtotal = 'sub_tb%s' % (ensayo.id)
                ensayo.cantidad = request.POST[cantida]
                ensayo.subtotal = request.POST[subtotal]
                ensayo.save()

            if 'cantidad_tb0' in request.POST:
                orden_ensayo = Orden_Ensayo()
                orden_ensayo.cantidad = request.POST['cantidad_tb0']
                orden_ensayo.ensayo = Ensayo.objects.get(codigo='0000')
                orden_ensayo.orden = orden
                orden_ensayo.valor_uni = request.POST['valor_tb0']
                orden_ensayo.subtotal = request.POST['sub_tb0']
                orden_ensayo.hechas = request.POST['cantidad_tb0']
                orden_ensayo.save()

            return HttpResponse(orden.id)
    else:
        return Http404


def orden_para_editar(request):
    if request.method == 'GET':
        try:
            orden = Orden.objects.get(id=request.GET['id'])
            salida = '%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
            orden.total, orden.beneficiario, orden.descuento, orden.consignacion, orden.num_factura, orden.observacion,
            orden.laboratorio, orden.fecha_factura, orden.pendiente)
            return HttpResponse(salida)
        except Orden.DoesNotExist:
            return HttpResponse('not')  # la orden no encontrada
        except Orden.MultipleObjectsReturned:
            return HttpResponse('m')
    else:
        return Http404


def orden_persona(request):
    """consulta las ordenes que haya tenido una persona"""
    if request.method == 'GET':
        if 'empresa' in request.GET:
            try:
                persona = Persona.objects.get(user__username=request.GET['empresa'])
                ordenes = Orden.objects.filter(persona=persona).order_by('id')
                salida = ''

                for orden in ordenes:
                    salida += '<tr><th>%s</th>' %orden.id
                    salida += '<th>%s</th>' %orden.fecha_orden
                    salida += '<th>%s</th>' %orden.persona.user.first_name

                    if orden.consignacion == '':
                        salida += '<th>Sin consignacion</th>'
                    else:
                        salida += '<th>%s</th>' % orden.consignacion

                    if orden.num_factura == '':
                        salida += '<th>Sin Factura</th>'
                    else:
                        salida += '<th>%s</th>' % orden.num_factura
                    salida += '<th>%s</th>' % orden.laboratorio.nombre
                    salida += '<th>%s</th>' % orden.total



                    if orden.terminada == '0':
                        salida += '<th><button class="btn btn-danger" onclick="editar_orden(%s)" type="button">Editar</button></th>' %orden.id
                        salida += '<th>En Proceso</th>'
                        salida += '<th><button class="btn btn-danger" onclick="anular_orden(%s)" type="button">Anular</button></th>' % orden.id
                    elif orden.terminada == '1':
                        salida += '<th>Sin opcion</th>'
                        salida += '<th>Terminada</th>'
                        salida += '<th><button class="btn btn-danger" onclick="anular_orden(%s)" type="button">Anular</button></th>' % orden.id
                    else:
                        salida += '<th>Sin opcion</th>'
                        salida += '<th>Sin opcion</th>'
                        salida += '<th>Anulada</th>'

                    if not orden.aprobacion:
                        salida += '<th>Sin aprobar</th></tr>'
                    else:
                        salida += '<th><button class="btn btn-danger" onclick="imprimir_orden(%s)" type="button">' \
                                      'Imprimir</button></th></tr>' % orden.id

                return HttpResponse(salida)
            except Persona.DoesNotExist:
                return HttpResponse('no persona')
        else:
            return HttpResponse('error get')  # no se envia un dato con la descripcion persona
    else:
        return Http404


def orden_con_num(request):
    """consulta la orden por consignacion-->consignacion o numero de orden-->numero"""
    if request.method == 'GET':
        try:
            if 'consignacion' in request.GET:
                orden = Orden.objects.get(consignacion=request.GET['consignacion'])
            elif 'numero' in request.GET:
                orden = Orden.objects.get(id=request.GET['numero'])
            else:
                return HttpResponse('error')  # error del envio al server del la variable consignacion.

            salida = '<tr><th>%s</th>' % str(orden.id)
            salida += '<th>%s</th>' % str(orden.fecha_orden)
            salida += '<th>%s</th>' % orden.persona.user.first_name.encode('utf-8')

            if orden.consignacion == '':
                salida += '<th>Sin consignacion</th>'
            else:
                salida += '<th>%s</th>' % orden.consignacion.encode('utf-8')

            if orden.num_factura == '':
                salida += '<th>Sin Factura</th>'
            else:
                salida += '<th>%s</th>' % str(orden.num_factura)
            salida += '<th>%s</th>' % orden.laboratorio.nombre.encode('utf-8')
            salida += '<th>%s</th>' % str(orden.total)

            if orden.terminada == '0':
                salida += '<th><button class="btn btn-danger" onclick="editar_orden(%s)" type="button">Editar</button></th>' % str(orden.id)
                salida += '<th>En Proceso</th>'
                salida += '<th><button class="btn btn-danger" onclick="anular_orden(%s)" type="button">Anular</button></th>' % str(orden.id)
            elif orden.terminada == '1':
                salida += '<th>Sin opcion</th>'
                salida += '<th>Terminada</th>'
                salida += '<th><button class="btn btn-danger" onclick="anular_orden(%s)" type="button">Anular</button></th>' % str(orden.id)
            else:
                salida += '<th>Sin opcion</th>'
                salida += '<th>Sin opcion</th>'
                salida += '<th>Anulada</th>'

            if not orden.aprobacion:
                salida += '<th>Sin aprobar</th></tr>'
            else:
                salida += '<th><button class="btn btn-danger" onclick="imprimir_orden(%s)" type="button">' \
                          'Imprimir</button></th></tr>' % str(orden.id)

            return HttpResponse(salida)
        except Orden.DoesNotExist:
            return HttpResponse('not')  # no se encontro la orden con el numero dado
    else:
        return Http404


def ordenes_sin_aprobacion(request):
    if request.method == 'GET':
        ordenes = Orden.objects.filter(aprobacion=False).exclude(consignacion='')

        if len(ordenes) > 0:
            salida = '''
                    <div id="lista_orden"><table class="table table-hover">
                        <thead><tr>
                            <th>N° Orden</th>
                            <th>Empresa</th>
                            <th>Consignación</th>
                            <th>Laboratorio</th>
                            <th>Precio</th>
                            <th>Descuento</th>
                            <th>Accion</th></tr>
                        </thead>
                        <tbody>

                    '''
            for orden in ordenes:
                salida += '<tr><th>%s</th>' % orden.id
                salida += '<th>%s</th>' % orden.persona.user.first_name.encode('utf-8')
                salida += '<th>%s</th>' % orden.consignacion.encode('utf-8')
                salida += '<th>%s</th>' % orden.laboratorio.nombre.encode('utf-8')
                salida += '<th>%s</th>' % str(orden.total)
                salida += '<th>%s</th>' % str(orden.descuento)
                salida += '<th><button class="btn btn-danger" onclick="aprobar_orden(%s)" type="button">' \
                          'Aprobar</button></tr>' % str(orden.id)

            salida += '</tbody></div></table>'
            return HttpResponse(salida)

        else:
            return HttpResponse('not')


def ordenes_aprobadas_no_impresas(request):
    ordenes = Orden.objects.filter(aprobacion=True).filter(contador_impresiones=0)
    if len(ordenes) > 0:
        salida = '''
                <div id="lista_orden"><table class="table table-hover">
                    <thead><tr>
                        <th>N° Orden</th>
                        <th>Empresa</th>
                        <th>Consignación</th>
                        <th>Laboratorio</th>
                        <th>imprimir</th></tr>
                    </thead>
                    <tbody>

                '''
        for orden in ordenes:
            salida += '<tr><th>%s</th>' % str(orden.id)
            salida += '<th>%s</th>' % orden.persona.user.first_name.encode('utf-8')
            salida += '<th>%s</th>' % orden.consignacion.encode('utf-8')
            salida += '<th>%s</th>' % orden.laboratorio.nombre.encode('utf-8')
            salida += '<th><a href="imprimir_orden?id=%s" target="_blank" class="btn-danger">imprimir</a></th></tr>' % str(orden.id)

        salida += '</tbody></div></table>'
        return HttpResponse(salida)
    else:
        return HttpResponse('not')


def aprobar_orden(request):
    if request.method == 'GET':  # se recibe el id de la orden a editar
        try:
            orden = Orden.objects.get(id=request.GET['id'])
            orden.aprobacion = True
            orden.save()
            th_press = Thread(target=enviar_correo_add_orden, args=(orden, datetime.datetime.now(), request.session['usuario'],))
            th_press.start()
            return HttpResponse('ok')
        except Orden.DoesNotExist:
            return HttpResponse('error')


@login_required(login_url='/')
def imprimir_orden(request):
    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate PDF headers.
        orden = Orden.objects.get(id=request.GET['id'])
        orden_ensayos = Orden_Ensayo.objects.filter(orden=orden)

        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.setFont("Times-Roman", 12)
        if orden.terminada == '2':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo2.jpg', 180, 200, width=420, height=420)
        else:
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 180, 200, width=420, height=420)

        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)

        estilo = getSampleStyleSheet()
        # P0 = Paragraph('<b>GESTION DE SERVICIOS ACADEMICOS</b>', estilo["BodyText"])
        # P1 = Paragraph('<b>SOLICITUD DE SERVICIOS DE LABORATORIOS</b>', estilo["BodyText"])

        p.drawString(140, 760, 'GESTION DE SERVICIOS ACADEMICOS')
        p.drawString(125, 730, 'SOLICITUD DE SERVICIOS DE LABORATORIOS')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GS-01 /v 1</b>', estilo["BodyText"])

        data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]
        table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (3, 1), 'CENTER'),
            # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 50, 722)
        vacio = [['']]

        marco1 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                       ], colWidths=510, rowHeights=90
                       )
        marco1.wrapOn(p, 100, 400)
        marco1.drawOn(p, 50, 620)

        # encabezado

        p.setFont("Times-Roman", 10)

        p.drawString(55, 690, 'FECHA:')
        dic_mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                   9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        fecha = '%s DE %s DEL %s' % (orden.fecha_orden.day, dic_mes[orden.fecha_orden.month], orden.fecha_orden.year)

        p.drawString(95, 690, fecha.upper())
        p.line(95, 687, 285, 687)

        p.drawString(310, 690, 'LABORATORIO:')
        p.drawString(390, 690, orden.laboratorio.nombre.upper()[:33])
        p.line(390, 687, 550, 687)

        p.drawString(55, 670, 'INTERESADO:')
        if len(orden.persona.user.first_name) > 26:
            p.drawString(130, 670, orden.persona.user.first_name.upper()[:24]+' ...')
        else:
            p.drawString(130, 670, orden.persona.user.first_name.upper())
        p.line(130, 667, 285, 667)

        p.drawString(310, 670, 'CÉDULA / NIT:')
        p.drawString(390, 670, orden.persona.user.username)
        p.line(390, 667, 550, 667)

        p.drawString(55, 650, 'DIRECCIÓN:')
        if len(orden.persona.direccion) > 29:
            p.drawString(120, 650, orden.persona.direccion.upper()[:27]+' ...')
        else:
            p.drawString(120, 650, orden.persona.direccion.upper())
        p.line(120, 647, 285, 647)

        p.drawString(310, 650, 'EMAIL:')
        if len(orden.persona.user.email) > 30:
            p.drawString(350, 650, orden.persona.user.email.upper()[:38]+' ...')
        else:
            p.drawString(350, 650, orden.persona.user.email.upper())
        p.line(350, 647, 550, 647)

        p.drawString(55, 630, 'TELEFONOS:')
        p.drawString(125, 630, orden.persona.telefono[:23])
        p.line(125, 627, 285, 627)

        p.drawString(310, 630, 'N° CONSIGNACIÓN:')
        p.drawString(415, 630, orden.consignacion)
        p.line(415, 627, 550, 627)

        # p.setFont("Helvetica", 5)

        ensayo = Paragraph('<b>N° ENSAYO</b>', estilo["BodyText"])
        des_ensayo = Paragraph('<b>DESCRIPCIÓN DEL ENSAYO</b>', estilo["BodyText"])
        cantidad = Paragraph('<b>CANTIDAD</b>', estilo["BodyText"])
        data = [[ensayo, des_ensayo, cantidad, Paragraph('<b>VALOR UNI.</b>', estilo["BodyText"]),
                 Paragraph('<b>SUBTOTAL</b>', estilo["BodyText"])], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', '']]

        x = 1
        for ensayo in orden_ensayos:
            data[x][0] = ensayo.ensayo.codigo
            if len(ensayo.ensayo.descripcion) > 35:
                data[x][1] = ensayo.ensayo.descripcion[:30] + '...'
            else:
                data[x][1] = ensayo.ensayo.descripcion[:30]

            data[x][2] = ensayo.cantidad
            data[x][3] = ensayo.valor_uni
            data[x][4] = ensayo.subtotal
            x = x + 1

        table = Table(data=data,
                      style=[
                          # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                          ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                          ('ALIGN', (2, 1), (4, 16), 'CENTER'),
                          ('FONT', (0, 0), (4, 16), 'Times-Roman'),
                          ('SIZE', (0, 0), (4, 16), 12),
                      ], colWidths=(70, 235, 65, 70, 70), rowHeights=20
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 270)

        p.setFont("Times-Roman", 12)

        if orden.beneficiario == '1':
            p.drawString(300, 250, 'SUBTOTAL:  $')
            sub = int(orden.total) * 2
            p.drawString(430, 250, str(sub))

            p.drawString(300, 235, 'DESCUENTO 50%:  $')
            p.drawString(430, 235, orden.descuento)

            p.drawString(300, 220, 'TOTAL:  $')
            p.drawString(430, 220, orden.total)

            p.setFillColorRGB(1, 0, 0)
            p.drawString(55, 235, 'BENEFICIARIO ACUERDO')
            p.setFillColorRGB(0, 0, 0)
        else:
            p.drawString(300, 235, 'VALOR TOTAL: $')
            p.drawString(430, 235, orden.total)

        if orden.fecha_factura != None:
            fecha_fac = '%s-%s-%s' % (orden.fecha_factura.day, orden.fecha_factura.month, orden.fecha_factura.year)
        else:
            fecha_fac = ''

        vacio = [['', str(orden.id), str(orden.num_factura), fecha_fac], ['', '', '', ''], ['', '', '', '']]

        vacio[1][0] = 'OBSERVACION: \n' + orden.observacion.encode('utf-8')
        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('FONT', (0, 1), (0, 1), 'Times-Roman'),
                           ('FONT', (0, 0), (3, 0), 'Times-Roman'),
                           ('SIZE', (0, 1), (0, 1), 12),
                           ('VALIGN', (0, 1), (0, 1), 'TOP'),
                           ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                           ('SPAN', (0, 1), (3, 1)),  # combina celdas
                           ('SPAN', (0, 2), (3, 2)),  # combina celdas
                       ], colWidths=127.5, rowHeights=(20, 40, 60)
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 88)

        if orden.requiere_factura == '1':
            p.setFillColorRGB(1, 0, 0)
            p.drawString(55, 193, 'REQUIERE FACTURA')
            p.setFillColorRGB(0, 0, 0)

        p.setFont("Times-Roman", 8)
        p.drawString(225, 202, 'N° Orden')
        p.drawString(350, 202, 'N° Factura')
        p.drawString(490, 202, 'Fecha')

        p.setFont("Times-Roman", 12)
        p.drawString(80, 103, 'Vo. Bo. Jefe División de Servicios Académicos.')


        user = User.objects.get(username=orden.jefe)
        # el cuadro de la firma debe ser de 7.5 cm X 1.5 cm y de 700 X 110 px en la imagen jpg
        p.drawImage(ruta_view + '/firmas/firmas/'+str(orden.jefe)+'.jpg', 340, 100, width=200, height=40)
        p.line(340, 100, 540, 100)
        p.setFont("Times-Roman", 7)
        p.drawString(410, 90, str(user.first_name).upper())
        p.drawString(340, 90, 'NOMBRE DEL JEFE:')

        # Close the PDF object cleanly, and we're done.

        data_pie = [['Elaboró:', 'Revisó:', 'Aprobó:'], ['Fecha:', 'Fecha:', 'Fecha:']]
        data_pie = Table(data_pie, colWidths=170, rowHeights=18)
        data_pie.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('FONT', (0, 0), (2, 1), 'Times-Roman'),
            ('SIZE', (0, 0), (2, 1), 12),
        ]))
        data_pie.wrapOn(p, 100, 400)
        data_pie.drawOn(p, 50, 42)

        orden.contador_impresiones = orden.contador_impresiones + 1
        orden.save()

        p.showPage()
        p.save()
        return response

    else:
        return Http404


@login_required(login_url='/')
def imprimir_pendiente(request):
    if request.method == 'GET':

        # Create the HttpResponse object with the appropriate PDF headers.
        orden = Orden.objects.get(id=request.GET['id'])
        orden_ensayos = Orden_Ensayo.objects.filter(orden=orden)

        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.setFont("Times-Roman", 12)

        p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 90, 550, width=220, height=188)
        p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 360, 550, width=220, height=188)

        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 66.5, 724, width=38, height=38)
        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 336.5, 724, width=38, height=38)

        data_encabezado = [['', 'División de Servicios Acádemicos'], ['', 'Recepción de Consignación']]

        table_encabezado = Table(data_encabezado, colWidths=(41, 224), rowHeights=21)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (1, 1), 'CENTER'),
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 65, 722)

        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 335, 722)

        data = [['N° Orden', '', 'Consignación', ''], ['persona', '', '', ''], ['Valor', '', '', '']]
        data[0][1] = str(orden.id)
        data[0][3] = orden.consignacion
        data[1][1] = orden.persona.user.first_name
        data[2][1] = orden.total

        table = Table(data=data,
                      style=[
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('ALIGN', (0, 1), (0, 2), 'CENTER'),
                          ('ALIGN', (2, 1), (3, 2), 'CENTER'),
                          ('FONT', (0, 0), (3, 2), 'Times-Roman'),
                          ('SPAN', (1, 1), (3, 1)),
                          ('SPAN', (1, 2), (3, 2)),
                          ('SIZE', (0, 0), (3, 2), 12),
                      ], colWidths=(56.3, 66.3, 76.3, 66.3), rowHeights=20
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 65, 640)

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 335, 640)

        p.line(65, 589, 180, 589)
        p.drawString(65, 580, 'Recibe')

        p.line(335, 589, 450, 589)
        p.drawString(335, 580, 'Recibe')

        p.line(200, 589, 315, 589)
        p.drawString(200, 580, 'Entrega')

        p.line(470, 589, 585, 589)
        p.drawString(470, 580, 'Entrega')

        p.line(65, 549, 595, 549)

        p.line(332.5, 549, 332.5, 775)

        p.showPage()
        p.save()
        return response

    else:
        return Http404


# ---------------------Fin Crud Orden-----------------

# -----------------Metodos para la orden de lab --------------------------
@login_required(login_url='/')
def ordenes_sin_terminar(request):  # retorna las ordenes si terminar y que ya han sido aprobadas por el jefe...
    if 'tipo' in request.session and 'usuario' in request.session:
        usuario = User.objects.get(user__username=request.session['usuario'])
        ordenes = Orden.objects.filter(laboratorio=usuario.laboratorio, terminada='0', aprobacion=True).\
            order_by('fecha_orden')

        data = serializers.serialize('json', ordenes, fields=('fecha_orden', 'persona', 'total', 'terminada'))
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('logout')


@login_required(login_url='/')
def ordenes_terminadas(request):
    if 'usuario' in request.session:
        usuario = Persona.objects.get(user__username=request.session['usuario'])
        hoy = datetime.datetime.now()
        #hasta_fecha = hoy - datetime.timedelta(days=15)
        ordenes = Orden.objects.filter(laboratorio=usuario.laboratorio, terminada='1') # .filter(fecha_terminada__range=[hasta_fecha, hoy])
        '''
        salida = []
        for orden in ordenes:
            if orden.terminada == '1':
                vencimiento = orden.fecha_terminada + datetime.timedelta(days=15)
                if vencimiento > fecha:
                    salida.append(orden)
        '''
        data = serializers.serialize('json', ordenes, fields=('fecha_orden', 'persona', 'total', 'fecha_terminada'))
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def ordenes_ensayo(request):
    if 'id' in request.GET:
        orden = Orden.objects.get(id=request.GET['id'])
        ensayos = Orden_Ensayo.objects.filter(orden=orden)

        data = serializers.serialize('json', ensayos, fields=('ensayo', 'hechas', 'cantidad'))
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def terminar_orden(request):
    if 'id' in request.GET:
        orden = Orden.objects.get(id=request.GET['id'])
        ensayos_ordenes = Orden_Ensayo.objects.filter(orden=orden)

        for en in ensayos_ordenes:
            if en.hechas < en.cantidad:
                return HttpResponse('not')

        orden.terminada = '1'
        orden.fecha_terminada = datetime.datetime.now()
        orden.save()
        r = enviar_correo_ordenT(orden)
        return HttpResponse(r)


# -----------------Fin Metodos para la orden de lab --------------------------

# --------------enviar correo -------------

def enviar_correo_ordenT(orden):
    """envia correo cuando el laboratorista termina la orden"""
    try:
        subject = 'Div. Servicios Academicos-UFPS'
        contenido = Context({'orden': orden.id, 'lab': orden.laboratorio.nombre})
        to = [orden.persona.user.email]
        message = get_template('laboratorios/orden_terminada_correo.html').render(contenido)
        msg = EmailMessage(subject, message, 'diseraca@ufps.edu.co', to=to)
        msg.content_subtype = 'html'
        msg.send()
        return 'ok'
    except Exception as e:
        return 'error'


def enviar_correo_anulacion(orden, anulacion):
    """envia correo cuando el laboratorista termina la orden"""
    subject = 'Anulacion de Orden'
    fecha = '%s/%s/%s a las %s:%s' % (getattr(anulacion.fecha, 'year'), getattr(anulacion.fecha, 'month'),
                                      getattr(anulacion.fecha, 'day'), getattr(anulacion.fecha, 'hour'),
                                      getattr(anulacion.fecha, 'minute'))

    contenido = Context({'orden': orden.id, 'lab': orden.laboratorio.nombre.encode('utf-8'),
                         'quien': anulacion.usuario.encode('utf-8'), 'motivo': anulacion.motivo.encode('utf-8'),
                         'fecha': fecha})
    to = [orden.persona.user.email]
    message = get_template('laboratorios/orden_anulada_correo.html').render(contenido)
    msg = EmailMessage(subject, message, 'diseraca@ufps.edu.co', to=to)
    msg.content_subtype = 'html'

    try:
        msg.send()
        return 'ok'
    except Exception:
        return 'error'


def enviar_correo_add_orden(orden, fecha, usuario):
    """envia correo cuando el jefe aprueba la orden"""
    try:
        subject = 'Nueva Orden Aprobada'
        fecha = '%s/%s/%s a las %s:%s' % (getattr(fecha, 'year'), getattr(fecha, 'month'),
                                          getattr(fecha, 'day'), getattr(fecha, 'hour'),
                                          getattr(fecha, 'minute'))
        usuario = User.objects.get(username=usuario)
        contenido = Context({'orden': orden.id, 'fecha': fecha, 'usuario': usuario})
        to = orden.laboratorio.email
        message = get_template('laboratorios/add_orden_correo.html').render(contenido)
        msg = EmailMessage(subject, message, 'diseraca@ufps.edu.co', [to])
        msg.content_subtype = 'html'
        msg.send()
    except Exception as e:
        print('error', e)


# --------------fin enviar correo por termiancion orden-------------

# --------------- Crud de Ensayos de Aguas------------------
def get_ensayos_agua(request):
    if request.method == 'GET':
        if 'orden' in request.GET:
            try:
                ensayos_ordenes = Orden_Ensayo.objects.filter(orden=Orden.objects.get(id=request.GET['orden']))

                data = serializers.serialize('json', ensayos_ordenes, fields=('ensayo', 'cantidad', 'hechas'))
                return HttpResponse(data, content_type='application/json')
            except Orden.DoesNotExist:
                return HttpResponse('error')


@login_required(login_url='/')
def add_resultado_aguas(request):
    if request.method == 'POST':
        resultado = Resultado_Aguas()  # el nuevo reporte de resultados
        orden = Orden.objects.get(id=request.POST['id'])

        resultado.orden = orden
        resultado.codigo = request.POST['codigo_muestra']
        resultado.municipio = request.POST['municipio']
        resultado.lugar = request.POST['lugar']
        resultado.tomado_por = request.POST['tomada']
        resultado.tipo_muestra = request.POST['tipo_muestra']
        resultado.fecha_muestreo = request.POST['fecha_muestreo']
        resultado.hora_muestra = request.POST['hora']
        resultado.nombre = request.POST['nombre_m']
        resultado.observacion = request.POST['observacion']

        if orden.beneficiario == '1':
            resultado.estado = '2'
        else:
            resultado.estado = '1'

        jefes = Persona.objects.filter(tipo=1, user__is_active=True)
        resultado.jefe = jefes[0].user.username
        resultado.encargado = request.session['usuario']

        resultado.save()
        if orden.laboratorio.id < 10:
            resultado.verificacion = '0' + str(orden.laboratorio.id)
        else:
            resultado.verificacion = str(orden.laboratorio.id)

        if orden.id < 10:
            resultado.verificacion += '00000' + str(orden.id)
        elif orden.id < 100:
            resultado.verificacion += '0000' + str(orden.id)
        elif orden.id < 1000:
            resultado.verificacion += '000' + str(orden.id)
        elif orden.id < 10000:
            resultado.verificacion += '00' + str(orden.id)
        elif orden.id < 100000:
            resultado.verificacion += '0' + str(orden.id)
        else:
            resultado.verificacion += str(orden.id)

        resultado.verificacion += str(resultado.id)
        resultado.save()

        ensayos_ordenes = Orden_Ensayo.objects.filter(orden=orden)

        if 'codigo_0439-a' in request.POST:
            for en in ensayos_ordenes:
                if en.ensayo.codigo == '0439':
                    en.hechas = en.hechas + 1
                    en.save()
                    r = Resultado_agua_ensayo()  # nuevo resultado de ensayo aguas
                    r.reporte = resultado
                    r.ensayo = en.ensayo
                    r.codigo = '0439-a'
                    r.descripcion = 'Coliformes totales'
                    r.unidad = request.POST['unidad_0439-a']
                    r.metodo = request.POST['metodo_0439-a']
                    r.resultado = request.POST['resultado_0439-a']
                    r.limite = request.POST['limite_0439-a']
                    r.acreditado = en.ensayo.acreditado
                    r.save()
                    r = Resultado_agua_ensayo()  # nuevo resultado de ensayo aguas
                    r.reporte = resultado
                    r.ensayo = en.ensayo
                    r.codigo = '0439-b'
                    r.descripcion = 'coliformes fecales'
                    r.unidad = request.POST['unidad_0439-b']
                    r.metodo = request.POST['metodo_0439-b']
                    r.resultado = request.POST['resultado_0439-b']
                    r.limite = request.POST['limite_0439-b']
                    r.acreditado = en.ensayo.acreditado
                    r.save()
                    break

        for i in range(len(ensayos_ordenes)):  # itero los ensayo que llegan de formulario
            if 'codigo_' + str(i) in request.POST:
                ensayo = Ensayo.objects.get(codigo=request.POST['codigo_' + str(i)])
                for en in ensayos_ordenes:  # se itera las ordenes ensayos para mirar cuales vienen del formulario...
                    if en.ensayo.codigo == ensayo.codigo:  # si llega uno del form se modifica las hechas en 1
                        en.hechas = en.hechas + 1
                        en.save()

                r = Resultado_agua_ensayo()  # nuevo resultado de ensayo aguas
                r.reporte = resultado
                r.ensayo = ensayo
                r.codigo = request.POST['codigo_' + str(i)]
                r.descripcion = request.POST['descripcion_' + str(i)]
                r.unidad = request.POST['unidad_' + str(i)]
                r.metodo = request.POST['metodo_' + str(i)]
                r.resultado = request.POST['resultado_' + str(i)]
                r.limite = request.POST['limite_' + str(i)]
                r.acreditado = ensayo.ensayo.acreditado
                r.save()
        return HttpResponse('ok')


@login_required(login_url='/')
def get_resultados_orden_aguas(request):
    if request.method == 'GET':
        resultados = Resultado_Aguas.objects.filter(orden=Orden.objects.get(id=request.GET['orden'])).order_by('fecha')

        data = serializers.serialize('json', resultados,
                                     fields=('codigo', 'municipio', 'fecha', 'tipo_muestra', 'fecha_muestreo'))
        return HttpResponse(data, content_type='application/json')


# retorna los datos del resultado que se toman de la vista
@login_required(login_url='/')
def get_resultado_editar_aguas(request):
    if request.method == 'GET' and 'id' in request.GET:
        resultado = Resultado_Aguas.objects.get(id=request.GET['id'])
        salida = '%s/%s/%s/%s/%s/%s/%s/%s/%s' % (resultado.codigo, resultado.municipio, resultado.lugar,
                                                 resultado.tomado_por, resultado.tipo_muestra, resultado.fecha_muestreo,
                                                 resultado.hora_muestra, resultado.nombre, resultado.observacion)
        return HttpResponse(salida)


# retorna los datos de cada uno de los ensayos agregados en la vista
@login_required(login_url='/')
def get_ensayos_resultado_editar_aguas(request):
    if request.method == 'GET' and 'id' in request.GET:
        reporte = Resultado_Aguas.objects.get(id=request.GET['id'])
        resultados_ensayo = Resultado_agua_ensayo.objects.filter(reporte=reporte)

        data = serializers.serialize('json', resultados_ensayo, fields=('codigo', 'descripcion', 'unidad', 'metodo',
                                                                        'resultado', 'limite'))
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def editar_resultado_aguas(request):
    if request.method == 'POST':
        resultado = Resultado_Aguas.objects.get(id=request.POST['id'])

        resultado.codigo = request.POST['codigo_muestra']
        resultado.municipio = request.POST['municipio']
        resultado.lugar = request.POST['lugar']
        resultado.tomado_por = request.POST['tomada']
        resultado.tipo_muestra = request.POST['tipo_muestra']
        resultado.fecha_muestreo = request.POST['fecha_muestreo']
        resultado.hora_muestra = request.POST['hora']
        resultado.nombre = request.POST['nombre_m']
        resultado.observacion = request.POST['observacion']
        resultado.save()

        resultados_ensayo = Resultado_agua_ensayo.objects.filter(reporte=resultado)

        for r in resultados_ensayo:
            r.metodo = request.POST['metodo_' + str(r.id)]
            r.resultado = request.POST['resultado_' + str(r.id)]
            r.limite = request.POST['limite_' + str(r.id)]
            r.unidad = request.POST['unidad_' + str(r.id)]
            r.save()
        return HttpResponse('ok')


@login_required(login_url='/')
def imprimir_resultado_aguas(request):
    if request.method == 'GET':
        resultado = Resultado_Aguas.objects.get(id=request.GET['id'])

        response = HttpResponse(content_type='application/pdf')

        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list  of functionality.
        p.setFont("Times-Roman", 12)

        if resultado.estado == '1':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 190, 180, width=420, height=388)
        elif resultado.estado == '2':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo2.jpg', 120, 180, width=420, height=388)
        elif resultado.estado == '3':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo3.jpg', 100, 180, width=420, height=388)
        else:
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo4.jpg', 100, 180, width=420, height=388)

        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)
        estilo = getSampleStyleSheet()

        p.line(125, 697, 340, 697)
        p.line(425, 697, 540, 697)

        p.line(125, 677, 340, 677)
        p.line(425, 677, 540, 677)

        p.line(125, 657, 340, 657)
        p.line(425, 657, 540, 657)

        # p.line(185, 615, 340, 615)

        if len(resultado.orden.persona.direccion) > 20:
            direccion = resultado.orden.persona.direccion[:27] + '...'
        else:
            direccion = resultado.orden.persona.direccion

        if len(resultado.orden.persona.user.email) > 45:
            email = resultado.orden.persona.user.email[:43] + '...'
        else:
            email = resultado.orden.persona.user.email.encode('utf-8')

        if len(resultado.orden.persona.user.first_name) > 43:
            n_persona = resultado.orden.persona.user.first_name.encode('utf-8')[:40] + '...'
        else:
            n_persona = resultado.orden.persona.user.first_name.encode('utf-8')

        enca_uno = [['Interesado:', n_persona, 'Cedula/Nit:', resultado.orden.persona.user.username],
                    ['Dirección:', direccion, 'Telefono:', resultado.orden.persona.telefono],
                    ['Email:', email, 'Fecha:', resultado.fecha]]

        marco_enca_uno = Table(data=enca_uno,
                               style=[
                                   # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (3, 2), 'Times-Roman'),
                                   ('SIZE', (0, 0), (3, 2), 12),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ], colWidths=(70, 230, 70, 140), rowHeights=20
                               )
        marco_enca_uno.wrapOn(p, 100, 400)
        marco_enca_uno.drawOn(p, 50, 655)

        p.line(165, 607, 340, 607)
        p.line(455, 607, 540, 607)

        p.line(165, 587, 340, 587)
        p.line(455, 587, 540, 587)

        p.line(165, 567, 340, 567)
        p.line(455, 567, 540, 567)

        p.line(165, 547, 340, 547)
        p.line(455, 547, 540, 547)

        enca_dos = [['Codigo de muestra:', resultado.codigo, 'Tipo de muestra:', resultado.tipo_muestra],
                    ['Lugar del muestreo:', resultado.lugar[:28], 'Municipio:', resultado.municipio],
                    ['Tomada por:', resultado.tomado_por.encode('utf-8')[:28], 'Fecha de muestreo:', resultado.fecha_muestreo],
                    ['Hora de muestreo:', resultado.hora_muestra, 'N° de Orden:', resultado.orden.id]]

        marco_enca_dos = Table(data=enca_dos,
                               style=[
                                   # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (3, 3), 'Times-Roman'),
                                   ('SIZE', (0, 0), (3, 3), 12),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ], colWidths=(110, 190, 100, 110), rowHeights=20
                               )
        marco_enca_dos.wrapOn(p, 100, 400)
        marco_enca_dos.drawOn(p, 50, 545)

        p.drawString(240, 530, 'LABORATORIO DE AGUAS')


        p.drawString(220, 635, 'IDENTIFICACION DE LA MUESTRA')

        data = [
            [Paragraph('<b>N°</b>', estilo["BodyText"]), Paragraph('<b>DESCRIPCIÓN DEL ENSAYO</b>', estilo["BodyText"])
                , Paragraph('<b>UNIDAD</b>', estilo["BodyText"]), Paragraph('<b>METODO</b>', estilo["BodyText"]),
             Paragraph('<b>RESULTADO</b>', estilo["BodyText"]), Paragraph('<b>LIMITE P.</b>', estilo["BodyText"])],
            ['', '', '', '', '', ''],
            ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''],
            ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''],
            ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''],
            ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''],
            ['', '', '', '', '', '']]

        res_ensayo_orden = Resultado_agua_ensayo.objects.filter(reporte=resultado).order_by('codigo')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GS-03 /v 1</b>', estilo["BodyText"])

        if res_ensayo_orden[0].acreditado:
            p.drawImage(ruta_view + '/laboratorios/static/img/ideam.jpg', 503, 723.5, width=53, height=53)
            p.setFont("Times-Roman", 9)
            p.drawString(50, 510, '\"Laboratorio Acreditado por el IDEAM para los parametros, según Resolución No. 1065 de 16 de mayo de 2017\"')
            p.setFont("Times-Roman", 12)
            p.drawString(120, 760, 'GESTION DE SERVICIOS ACADEMICOS')
            p.drawString(150, 730, 'RESULTADO DE ANALISIS')

            data_encabezado = [['', '', P2, P3, ''], ['', '', 'PAGINAS', '1/1', '']]
            table_encabezado = Table(data_encabezado, colWidths=(62, 238, 66, 82, 62), rowHeights=28)
            table_encabezado.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (4, 0), (4, 1)),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                # ('SPAN', (1, 0), (1, 1)),
                # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                ('FONT', (0, 1), (0, 1), 'Times-Roman'),
                ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
                ('ALIGN', (0, 0), (3, 1), 'CENTER'),
                # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
            ]))
            table_encabezado.wrapOn(p, 100, 400)
            table_encabezado.drawOn(p, 50, 722)
        else:
            p.drawString(150, 760, 'GESTION DE SERVICIOS ACADEMICOS')
            p.drawString(180, 730, 'RESULTADO DE ANALISIS')
            data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]
            table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
            table_encabezado.setStyle(TableStyle([
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('SPAN', (0, 0), (0, 1)),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                # ('SPAN', (1, 0), (1, 1)),
                # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                ('FONT', (0, 1), (0, 1), 'Times-Roman'),
                ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
                ('ALIGN', (0, 0), (3, 1), 'CENTER'),
                # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
            ]))
            table_encabezado.wrapOn(p, 100, 400)
            table_encabezado.drawOn(p, 50, 722)

        fila = 1
        for r in res_ensayo_orden:
            data[fila][0] = r.codigo

            if len(r.descripcion) > 27:
                data[fila][1] = r.descripcion[:25].encode('utf-8') + '...'

            else:
                data[fila][1] = r.descripcion.encode('utf-8')

            data[fila][2] = r.unidad.encode('utf-8')

            data[fila][3] = r.metodo.encode('utf-8')

            data[fila][4] = r.resultado

            if len(r.limite) > 18:
                data[fila][5] = r.limite[:16] + '...'
            else:
                data[fila][5] = r.limite

            fila = fila + 1

        table = Table(data=data,
                      style=[
                          # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                          ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                          ('ALIGN', (2, 1), (5, 16), 'CENTER'),
                          ('FONT', (0, 0), (5, 16), 'Times-Roman'),
                          ('SIZE', (0, 0), (5, 0), 10),
                          ('SIZE', (0, 1), (5, 16), 12),
                      ], colWidths=(40, 150, 70, 100, 80, 70), rowHeights=17
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 230)

        vacio = [[''], ['']]
        # p.drawString(55, 205, 'OBSERVACION:')

        vacio[0][0] = 'OBSERVACION: Los resultados de los ensayos reportados, solo pertenecen a ' \
                      'las muestras analizadas en este \nreporte. el contenido de esta ' \
                      'información no se puede copiar y/o reproducir sin la áutorización del laboratorio de\n' \
                      'aguas-ufps - '
        if resultado.observacion.encode('utf-8') != '':
            vacio[0][0] += '\n'+resultado.observacion.encode('utf-8')


        encargado = User.objects.get(username=resultado.encargado)
        # p.drawImage(ruta_view + '/firmas/firmas/'+str(encargado.codigo)+'.jpg', 60, 120, width=200, height=40)
        p.drawString(60, 112, str(encargado.first_name).upper())
        p.drawString(60, 102, 'Analista: Laboratorio de AGUA-UFPS')
        # p.drawString(60, 102, 'Analista: Asistente de laboratorio-UFPS')
        p.line(60, 122, 250, 122)

        jefe = User.objects.get(username=resultado.jefe)
        p.drawImage(ruta_view + '/firmas/firmas/' + str(jefe.username.encode('utf-8')) + '.jpg', 310, 120, width=200, height=40)
        p.drawString(310, 112, str(jefe.first_name.encode('utf-8')).upper())

        p.drawString(400, 162, 'N° Verificación: ' + str(resultado.verificacion))
        p.drawString(310, 102, 'Vo. Bo. Jefe Division de Servicios Académicos.')
        p.line(310, 122, 540, 122)

        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('FONT', (0, 1), (0, 1), 'Times-Roman'),
                           ('SIZE', (0, 1), (0, 1), 12),
                           # ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
                           # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                       ], colWidths=510, rowHeights=60
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 100)

        p.setFont("Times-Roman", 10)
        p.drawString(90, 80, 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER - DIVISION DE SERVICIOS ACADEMICOS')

        p.setFont("Times-Roman", 8)
        p.setFillColorRGB(1, 0, 0)  # cambia el color de la letra a rojo
        p.drawString(130, 70, 'Avenda Gran Colombia N° E - 96 B. Colsag. Telefax. 5753256 e-mail diseraca@ufps.edu.co')
        p.drawString(280, 60, 'CUCUTA - COLOMBIA')

        p.showPage()
        p.save()
        return response


# --------------- Crud de Ensayos de Aguas------------------


# --------------- Crud de Ensayos de Nutricion Animal-----------
@login_required(login_url='/')
def add_resultado_nutricion(request):
    if request.method == 'POST':
        resultado = Resultado_Nutricion_Animal()  # el nuevo reporte de resultados
        orden = Orden.objects.get(id=request.POST['id'])
        resultado.orden = orden
        resultado.codigo = request.POST['codigo_muestra']
        resultado.tipo = request.POST['tipo_muestra']
        resultado.descripcion = request.POST['descripcion']

        if orden.beneficiario == '1':
            resultado.estado = '2'
        else:
            resultado.estado = '1'

        jefes = Persona.objects.filter(tipo=1, user__is_active=True)
        resultado.jefe = jefes[0].user.username

        resultado.encargado = request.session['usuario']

        resultado.save()

        if orden.laboratorio.id < 10:
            resultado.verificacion = '0' + str(orden.laboratorio.id)
        else:
            resultado.verificacion = str(orden.laboratorio.id)

        if orden.id < 10:
            resultado.verificacion += '00000' + str(orden.id)
        elif orden.id < 100:
            resultado.verificacion += '0000' + str(orden.id)
        elif orden.id < 1000:
            resultado.verificacion += '000' + str(orden.id)
        elif orden.id < 10000:
            resultado.verificacion += '00' + str(orden.id)
        elif orden.id < 100000:
            resultado.verificacion += '0' + str(orden.id)
        else:
            resultado.verificacion += str(orden.id)

        resultado.verificacion += str(resultado.id)
        resultado.save()

        ensayos_ordenes = Orden_Ensayo.objects.filter(orden=orden)

        for i in range(len(ensayos_ordenes)):  # itero los ensayo que llegan de formulario
            if 'codigo_' + str(i) in request.POST:
                ensayo = Ensayo.objects.get(codigo=request.POST['codigo_' + str(i)])
                for en in ensayos_ordenes:  # se itera las ordenes ensayos para mirar cuales vienen del formulario...
                    if en.ensayo.codigo == ensayo.codigo:  # si llega uno del form se modifica las hechas en 1
                        en.hechas = en.hechas + 1
                        en.save()

                r = Resultado_Nutricion_Animal_Ensayo()  # nuevo resultado de ensayo aguas
                r.reporte = resultado
                r.ensayo = ensayo
                r.codigo = request.POST['codigo_' + str(i)]
                r.descripcion = request.POST['descripcion_' + str(i)]
                r.metodo = request.POST['metodo_' + str(i)]
                r.resultado = request.POST['resultado_' + str(i)]
                r.save()
        return HttpResponse('ok')


@login_required(login_url='/')
def get_metodos_ensayo(request):
    if request.method == 'GET' and 'codigo' in request.GET:
        try:
            ensayo = Ensayo.objects.get(codigo=request.GET['codigo'])
            return HttpResponse(ensayo.metodo.encode('utf-8'))
        except Ensayo.DoesNotExist:
            return HttpResponse('not')


@login_required(login_url='/')
def get_resultados_orden_nutricion(request):
    if request.method == 'GET':
        resultados = Resultado_Nutricion_Animal.objects.filter(
            orden=Orden.objects.get(id=request.GET['orden'])).order_by('fecha')
        data = serializers.serialize('json', resultados, fields=('codigo', 'fecha', 'tipo'))
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def get_resultado_editar_nutricion(request):
    if request.method == 'GET' and 'id' in request.GET:
        resultado = Resultado_Nutricion_Animal.objects.get(id=request.GET['id'])
        salida = '%s/%s/%s' % (resultado.codigo, resultado.tipo, resultado.descripcion)
        return HttpResponse(salida)


@login_required(login_url='/')
def get_ensayos_resultado_editar_nutricion(request):
    if request.method == 'GET' and 'id' in request.GET:
        reporte = Resultado_Nutricion_Animal.objects.get(id=request.GET['id'])
        resultados_ensayo = Resultado_Nutricion_Animal_Ensayo.objects.filter(reporte=reporte)

        data = serializers.serialize('json', resultados_ensayo, fields=('codigo', 'descripcion', 'metodo', 'resultado'))
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def editar_resultado_nutricion(request):
    if request.method == 'POST':

        reporte = Resultado_Nutricion_Animal.objects.get(id=request.POST['id'])
        reporte.codigo = request.POST['codigo_muestra']
        reporte.tipo = request.POST['tipo_muestra']
        reporte.descripcion = request.POST['descripcion']
        reporte.save()
        ensayos_reporte = Resultado_Nutricion_Animal_Ensayo.objects.filter(reporte=reporte)

        for ensayo in ensayos_reporte:
            ensayo.metodo = request.POST['metodo_' + str(ensayo.id)]
            ensayo.resultado = request.POST['resultado_' + str(ensayo.id)]
            ensayo.save()

        return HttpResponse('ok')


@login_required(login_url='/')
def imprimir_resultado_nutricion(request):
    if request.method == 'GET':
        resultado = Resultado_Nutricion_Animal.objects.get(id=request.GET['id'])

        response = HttpResponse(content_type='application/pdf')

        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list  of functionality.
        p.setFont("Times-Roman", 12)

        if resultado.estado == '1':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 190, 180, width=420, height=388)
        elif resultado.estado == '2':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo2.jpg', 120, 180, width=420, height=388)
        elif resultado.estado == '3':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo3.jpg', 100, 180, width=420, height=388)
        else:
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo4.jpg', 100, 180, width=420, height=388)

        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)
        estilo = getSampleStyleSheet()
        p.drawString(150, 760, 'GESTION DE SERVICIOS ACADEMICOS')
        p.drawString(180, 730, 'RESULTADO DE ANALISIS')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GS-03 /v 1</b>', estilo["BodyText"])

        data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]

        table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('FONT', (0, 1), (0, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (3, 1), 'CENTER'),
            # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 50, 722)

        if len(resultado.orden.persona.user.first_name) > 30:
            n_persona = resultado.orden.persona.user.first_name.encode('utf-8')[:30] + '...'
        else:
            n_persona = resultado.orden.persona.user.first_name.encode('utf-8')

        p.line(125, 697, 340, 697)
        p.line(425, 697, 540, 697)

        p.line(125, 677, 340, 677)
        p.line(425, 677, 540, 677)

        p.line(125, 657, 340, 657)
        p.line(425, 657, 540, 657)

        # p.line(185, 615, 340, 615)
        enca_uno = [['Interesado:', n_persona, 'Cedula/Nit:', resultado.orden.persona.user.username].encode('utf-8'),
                    ['Telefono:', resultado.orden.persona.telefono, 'Dirección:', resultado.orden.persona.direccion.encode('utf-8')],
                    ['Email:', resultado.orden.persona.user.email.encode('utf-8'), 'Fecha:', resultado.fecha]]

        marco_enca_uno = Table(data=enca_uno,
                               style=[
                                   # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (3, 2), 'Times-Roman'),
                                   ('SIZE', (0, 0), (3, 2), 12),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ], colWidths=(70, 230, 70, 140), rowHeights=20
                               )
        marco_enca_uno.wrapOn(p, 100, 400)
        marco_enca_uno.drawOn(p, 50, 655)

        if len(resultado.descripcion) > 76:
            descripcion = resultado.descripcion.encode('utf-8')[:75] + '...'
        else:
            descripcion = resultado.descripcion.encode('utf-8')

        if len(resultado.tipo) > 40:
            tipo = resultado.tipo[:38] + '...'
        else:
            tipo = resultado.tipo

        enca_dos = [['Codigo de la muestra:', resultado.codigo, 'Tipo de muestra:', tipo],
                    ['Descripción:', descripcion, '', '']]

        marco_enca_dos = Table(data=enca_dos,
                               style=[
                                   # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (1, 1), 'Times-Roman'),
                                   ('SIZE', (0, 0), (1, 1), 12),
                                   ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ], colWidths=(110, 100, 80, 220), rowHeights=20
                               )
        marco_enca_dos.wrapOn(p, 100, 400)
        marco_enca_dos.drawOn(p, 50, 585)

        p.drawString(100, 560, 'LABORATORIO DE NUTRICIÓN ANIMAL Y ANÁLISIS DE ALIMENTOS')
        p.drawString(220, 635, 'IDENTIFICACIÓN DE LA MUESTRA')

        data = [
            [Paragraph('<b>N°</b>', estilo["BodyText"]), Paragraph('<b>DESCRIPCIÓN DEL ENSAYO</b>', estilo["BodyText"]),
             Paragraph('<b>RESULTADO</b>', estilo["BodyText"]), Paragraph('<b>METODO</b>', estilo["BodyText"])],
            ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
            ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
            ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
            ['', '', '', '']]

        res_ensayo_orden = Resultado_Nutricion_Animal_Ensayo.objects.filter(reporte=resultado).order_by('codigo')

        fila = 1
        for r in res_ensayo_orden:
            data[fila][0] = r.codigo

            if len(r.descripcion) > 30:
                data[fila][1] = r.descripcion[:28] + '...'
            else:
                data[fila][1] = r.descripcion

            data[fila][2] = r.resultado
            data[fila][3] = r.metodo
            fila = fila + 1

        table = Table(data=data,
                      style=[
                          # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                          ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                          ('ALIGN', (2, 1), (3, 16), 'CENTER'),
                          ('FONT', (0, 0), (3, 16), 'Times-Roman'),
                          ('SIZE', (0, 0), (3, 16), 12),
                      ], colWidths=(30, 320, 80, 80), rowHeights=17
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 250)
        p.drawString(60, 230, 'Codigo de verificación: ' + str(resultado.verificacion))
        vacio = [[''], ['']]

        vacio[0][0] = 'OBSERVACION: Los resultados de los ensayos reportados, solo pertenecen a ' \
                      'las muestras analizadas en este\nreporte. el contenido de esta ' \
                      'información no se puede copiar y/o reproducir sin la áutorización del laboratorio de\n' \
                      'nutrición animal y análisis de alimentos-ufps\n'

        encargado = User.objects.get(username=resultado.encargado)
        #p.drawImage(ruta_view + '/firmas/firmas/'+str(encargado.codigo)+'.jpg', 60, 120, width=200, height=40)
        p.drawString(60, 112, str(encargado.first_name).upper())
        p.drawString(60, 102, 'Analista: Lab Nutrición Animal...-UFPS')
        p.line(60, 122, 250, 122)

        jefe = User.objects.get(username=resultado.jefe)
        p.drawImage(ruta_view + '/firmas/firmas/'+str(resultado.jefe) + '.jpg', 310, 120, width=200, height=40)
        p.drawString(310, 112, str(jefe.first_name).upper())
        p.drawString(400, 162, 'N° Orden: ' + str(resultado.orden.id))
        p.drawString(310, 102, 'Vo. Bo. Jefe Division de Servicios Académicos.')
        p.line(310, 122, 540, 122)

        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('FONT', (0, 1), (0, 1), 'Times-Roman'),
                           ('SIZE', (0, 1), (0, 1), 12),
                           # ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
                           # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                       ], colWidths=510, rowHeights=60
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 100)

        p.setFont("Times-Roman", 10)
        p.drawString(90, 80, 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER - DIVISION DE SERVICIOS ACADEMICOS')

        p.setFont("Times-Roman", 8)
        p.setFillColorRGB(1, 0, 0)  # cambia el color de la letra a rojo
        p.drawString(130, 70, 'Avenda Gran Colombia N° E - 96 B. Colsag. Telefax. 5753256 e-mail diseraca@ufps.edu.co')
        p.drawString(280, 60, 'CUCUTA - COLOMBIA')

        p.showPage()
        p.save()
        return response


# --------------- Fin Crud de Ensayos de Nutricion -------------

# --------------- crud de Ensayos de suelos agricolas------------
@login_required(login_url='/')
def add_resultado_suelos_agricolas(request):
    if request.method == 'POST':

        if request.POST['lista_ensayos_orden'] == '0':
            return HttpResponse('lista_ensayos')

        orden = Orden.objects.get(id=request.POST['id'])
        resultado = Resultado_suelos_agricolas()
        resultado.orden = orden
        resultado.propietario = request.POST['propietario']
        resultado.fecha_recepcion = request.POST['fecha_recepcion']
        resultado.departamento = request.POST['departamento']
        resultado.municipio = request.POST['municipio']
        resultado.vereda = request.POST['vereda']
        resultado.finca = request.POST['finca']
        resultado.lote = request.POST['lote']
        resultado.cultivo = request.POST['cultivo']

        if orden.beneficiario == '1':
            resultado.estado = '2'
        else:
            resultado.estado = '1'

        # resultados de los analisis quimico
        # cada resultado se divide en 3 partes separados por comas, (resultados, unidad, metodo)
        if 'resultado_ph' in request.POST:
            resultado.ph = request.POST['resultado_ph']+'#' + request.POST['unidad_ph'] + '#' + request.POST['metodo_ph']
        if 'resultado_ce' in request.POST:
            resultado.ce = request.POST['resultado_ce']+'#' + request.POST['unidad_ce'] + '#' + request.POST['metodo_ce']
        if 'resultado_co' in request.POST:
            resultado.co = request.POST['resultado_co']+'#'+request.POST['unidad_co']+'#'+request.POST['metodo_co']
        if 'resultado_mo' in request.POST:
            resultado.mo = request.POST['resultado_mo'] + '#' + request.POST['unidad_mo'] + '#' + request.POST['metodo_mo']
        if 'resultado_n' in request.POST:
            resultado.n = request.POST['resultado_n'] + '#' + request.POST['unidad_n'] + '#' + request.POST['metodo_n']
        if 'resultado_p' in request.POST:
            resultado.p = request.POST['resultado_p'] + '#' + request.POST['unidad_p'] + '#' + request.POST['metodo_p']
        if 'resultado_k' in request.POST:
            resultado.k = request.POST['resultado_k'] + '#' + request.POST['unidad_k'] + '#' + request.POST['metodo_k']
        if 'resultado_ca' in request.POST:
            resultado.ca = request.POST['resultado_ca'] + '#' + request.POST['unidad_ca'] + '#' + request.POST['metodo_ca']
        if 'resultado_mg' in request.POST:
            resultado.mg = request.POST['resultado_mg'] + '#' + request.POST['unidad_mg'] + '#' + request.POST['metodo_mg']
        if 'resultado_al' in request.POST:
            resultado.al = request.POST['resultado_al'] + '#' + request.POST['unidad_al'] + '#' + request.POST['metodo_al']
        if 'resultado_na' in request.POST:
            resultado.na = request.POST['resultado_na'] + '#' + request.POST['unidad_na'] + '#' + request.POST['metodo_na']
        if 'resultado_cic' in request.POST:
            resultado.cic = request.POST['resultado_cic'] + '#' + request.POST['unidad_cic']+'#'+request.POST['metodo_cic']
        if 'resultado_cice' in request.POST:
            resultado.cice = request.POST['resultado_cice']+'#'+request.POST['unidad_cice']+'#'+request.POST['metodo_cice']  # mirar formula
        if 'resultado_ai' in request.POST:
            resultado.acidez = request.POST['resultado_ai']+'#'+request.POST['unidad_ai']+'#'+request.POST['metodo_ai']
        if 'resultado_s' in request.POST:
            resultado.s = request.POST['resultado_s'] + '#' + request.POST['unidad_s'] + '#' + request.POST['metodo_s']
        if 'resultado_fe' in request.POST:
            resultado.fe = request.POST['resultado_fe'] + '#' + request.POST['unidad_fe'] + '#' + request.POST['metodo_fe']
        if 'resultado_mn' in request.POST:
            resultado.mn = request.POST['resultado_mn'] + '#' + request.POST['unidad_mn'] + '#' + request.POST['metodo_mn']
        if 'resultado_cu' in request.POST:
            resultado.cu = request.POST['resultado_cu'] + '#' + request.POST['unidad_cu'] + '#' + request.POST['metodo_cu']
        if 'resultado_zn' in request.POST:
            resultado.zn = request.POST['resultado_zn'] + '#' + request.POST['unidad_zn'] + '#' + request.POST['metodo_zn']
        if 'resultado_b' in request.POST:
            resultado.b = request.POST['resultado_b'] + '#' + request.POST['unidad_b'] + '#' + request.POST['metodo_b']

        # relaciones cationicas
        if 'resultado_ca_mg' in request.POST:
            resultado.ca_mg = request.POST['resultado_ca_mg'] + '#' + request.POST['unidad_ca_mg'] + '#' + request.POST[
            'metodo_ca_mg']
        if 'resultado_ca_k' in request.POST:
            resultado.ca_k = request.POST['resultado_ca_k'] + '#' + request.POST['unidad_ca_k'] + '#' + request.POST[
            'metodo_ca_k']
        if 'resultado_mg_k' in request.POST:
            resultado.mg_k = request.POST['resultado_mg_k'] + '#' + request.POST['unidad_mg_k'] + '#' + request.POST[
            'metodo_mg_k']
        if 'resultado_ca_mg_k' in request.POST:
            resultado.ca_mg_k = request.POST['resultado_ca_mg_k'] + '#' + request.POST['unidad_ca_mg_k'] + '#' + \
                            request.POST['metodo_ca_mg_k']

        if 'resultado_sat_na' in request.POST:
            resultado.sat_na = request.POST['resultado_sat_na'] + '#' + request.POST['unidad_sat_na'] + '#' + \
                            request.POST['metodo_sat_na']
        if 'resultado_sat_k' in request.POST:
            resultado.sat_k = request.POST['resultado_sat_k'] + '#' + request.POST['unidad_sat_k'] + '#' + \
                            request.POST['metodo_sat_k']
        if 'resultado_sat_ca' in request.POST:
            resultado.sat_ca = request.POST['resultado_sat_ca'] + '#' + request.POST['unidad_sat_ca'] + '#' + \
                            request.POST['metodo_sat_ca']
        if 'resultado_sat_mg' in request.POST:
            resultado.sat_mg = request.POST['resultado_sat_mg'] + '#' + request.POST['unidad_sat_mg'] + '#' + \
                            request.POST['metodo_sat_mg']
        if 'resultado_sat_al' in request.POST:
            resultado.sat_al = request.POST['resultado_sat_al'] + '#' + request.POST['unidad_sat_al'] + '#' + \
                            request.POST['metodo_sat_al']

        # analisis fisico
        if 'resultado_t1' in request.POST:
            resultado.textura_1 = request.POST['resultado_t1'] + '#' + request.POST['unidad_t1'] + '#' + request.POST[
            'metodo_t1']

        if 'metodo_t2_arena' in request.POST:
            resultado.t2_arena = request.POST['resultado_t2_arena'] + '#' + request.POST['unidad_t2_arena'] + '#' + \
                             request.POST['metodo_t2_arena']
        if 'metodo_t2_arcilla' in request.POST:
            resultado.t2_arcilla = request.POST['resultado_t2_arcilla'] + '#' + request.POST['unidad_t2_arcilla'] + '#' + \
                               request.POST['metodo_t2_arcilla']
        if 'metodo_t2_limo' in request.POST:
            resultado.t2_limo = request.POST['resultado_t2_limo'] + '#' + request.POST['unidad_t2_limo'] + '#' + \
                            request.POST['metodo_t2_limo']
        if 'clase_t2' in request.POST:
            resultado.t2_clase = request.POST['clase_t2']

        #resultado.observacion = request.POST['observacion']

        jefes = Persona.objects.filter(tipo=1, user__is_active=True)
        resultado.jefe = jefes[0].user.username

        resultado.encargado = request.session['usuario']

        lis_ensayo= request.POST['lista_ensayos_orden'].split(',')
        en = Orden_Ensayo.objects.get(id=lis_ensayo[0])
        en.hechas += 1
        en.save()
        resultado.ensayo = en.ensayo

        if orden.laboratorio.id < 10:
            resultado.verificacion = '0' + str(orden.laboratorio.id)
        else:
            resultado.verificacion = str(orden.laboratorio.id)

        if orden.id < 10:
            resultado.verificacion += '00000' + str(orden.id)
        elif orden.id < 100:
            resultado.verificacion += '0000' + str(orden.id)
        elif orden.id < 1000:
            resultado.verificacion += '000' + str(orden.id)
        elif orden.id < 10000:
            resultado.verificacion += '00' + str(orden.id)
        elif orden.id < 100000:
            resultado.verificacion += '0' + str(orden.id)
        else:
            resultado.verificacion += str(orden.id)

        resultado.verificacion += str(resultado.id)

        resultado.orden = Orden.objects.get(id=request.POST['id'])
        resultado.save()

        if orden.laboratorio.id < 10:
            resultado.verificacion = '0' + str(orden.laboratorio.id)
        else:
            resultado.verificacion = str(orden.laboratorio.id)

        if orden.id < 10:
            resultado.verificacion += '00000' + str(orden.id)
        elif orden.id < 100:
            resultado.verificacion += '0000' + str(orden.id)
        elif orden.id < 1000:
            resultado.verificacion += '000' + str(orden.id)
        elif orden.id < 10000:
            resultado.verificacion += '00' + str(orden.id)
        elif orden.id < 100000:
            resultado.verificacion += '0' + str(orden.id)
        else:
            resultado.verificacion += str(orden.id)

        resultado.verificacion += str(resultado.id)
        resultado.save()

        return HttpResponse('ok')
    return HttpResponse('not')


@login_required(login_url='/')
def get_resultados_orden_suelos_agricolas(request):
    if request.method == 'GET':
        resultados = Resultado_suelos_agricolas.objects.filter(orden=Orden.objects.get(id=request.GET['orden'])).order_by('fecha')
        data = serializers.serialize('json', resultados, fields=('propietario', 'vereda', 'finca', 'lote', 'cultivo'))
        #print data
        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
def imprimir_resultado_agricolas(request):
    if request.method == 'GET':
        resultado = Resultado_suelos_agricolas.objects.get(id=request.GET['id'])

        response = HttpResponse(content_type='application/pdf')

        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=A4)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list  of functionality.
        p.setFont("Times-Roman", 12)

        if resultado.estado == '1':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 190, 180, width=420, height=388)
        elif resultado.estado == '2':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo2.jpg', 120, 180, width=420, height=388)
        elif resultado.estado == '3':
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo3.jpg', 100, 180, width=420, height=388)
        else:
            p.drawImage(ruta_view + '/laboratorios/static/img/fondo4.jpg', 100, 180, width=420, height=388)

        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)
        estilo = getSampleStyleSheet()
        p.drawString(150, 800, 'GESTION DE SERVICIOS ACADEMICOS')
        p.drawString(180, 770, 'RESULTADO DE ANALISIS')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GS-03 /v 1</b>', estilo["BodyText"])

        data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]

        table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('FONT', (0, 1), (0, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (3, 1), 'CENTER'),
            # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 50, 762)

        if len(resultado.orden.persona.user.first_name) > 30:
            n_persona = resultado.orden.persona.user.first_name[:30] + '...'
        else:
            n_persona = resultado.orden.persona.user.first_name

        #p.line(125, 697, 340, 697)
        #p.line(425, 697, 540, 697)

        #p.line(125, 677, 340, 677)
        #p.line(425, 677, 540, 677)

        #p.line(125, 657, 340, 657)
        #p.line(425, 657, 540, 657)

        # p.line(185, 615, 340, 615)
        enca_uno = [['Interesado:', n_persona, 'Cedula/Nit:', resultado.orden.persona.user.username],
                    ['Telefono:', resultado.orden.persona.telefono, 'Dirección:', resultado.orden.persona.direccion],
                    ['Email:', resultado.orden.persona.user.email, 'Fecha:', resultado.fecha]]

        marco_enca_uno = Table(data=enca_uno,
                               style=[
                                   #('GRID', (0, 0),(-1, -1), 0.5, colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (3, 2), 'Times-Roman'),
                                   ('SIZE', (0, 0), (3, 2), 12),
                                   #('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                   ('VALIGN', (0, 0), (3, 2), 'MIDDLE'),
                                   ('LINEABOVE', (1, 1), (1, 1), 1, colors.grey),
                                   ('LINEABOVE', (3, 1), (3, 1), 1, colors.grey),
                                   ('LINEABOVE', (1, 2), (1, 2), 1, colors.grey),
                                   ('LINEABOVE', (3, 2), (3, 2), 1, colors.grey),
                                   ('LINEABOVE', (1, 3), (1, 3), 1, colors.grey),
                                   ('LINEABOVE', (3, 3), (3, 3), 1, colors.grey),
                               ], colWidths=(70, 230, 70, 140), rowHeights=20
                               )
        marco_enca_uno.wrapOn(p, 100, 400)
        marco_enca_uno.drawOn(p, 50, 700)

        enca_dos = [['Propietario:', resultado.propietario, 'Fecha recepción:', resultado.fecha_recepcion,'Vereda:', resultado.vereda],
                    ['Municipio:', resultado.municipio, 'Departamento:', resultado.departamento, 'Finca:', resultado.finca],
                    ['Cultivo:', resultado.cultivo, 'Lote:', resultado.lote,  '', '']]

        marco_enca_dos = Table(data=enca_dos,
                               style=[
                                   #('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                   # ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   # ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
                                   ('FONT', (0, 0), (5, 2), 'Times-Roman'),
                                   ('SIZE', (0, 0), (5, 2), 12),
                                   #('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                   #('VALIGN', (0, 0), (5, 2), 'MIDDLE'),
                                   ('LINEABOVE', (1, 1), (1, 1), 1, colors.grey),
                                   ('LINEABOVE', (3, 1), (3, 1), 1, colors.grey),
                                   ('LINEABOVE', (5, 1), (5, 1), 1, colors.grey),

                                   ('LINEABOVE', (1, 2), (1, 2), 1, colors.grey),
                                   ('LINEABOVE', (3, 2), (3, 2), 1, colors.grey),
                                   ('LINEABOVE', (5, 2), (5, 2), 1, colors.grey),

                                   ('LINEABOVE', (1, 3), (1, 3), 1, colors.grey),
                                   ('LINEABOVE', (3, 3), (3, 3), 1, colors.grey),
                               ], colWidths=(63, 107, 90, 100, 50, 100), rowHeights=20
                               )
        marco_enca_dos.wrapOn(p, 100, 400)
        marco_enca_dos.drawOn(p, 50, 618)

        p.drawString(220, 683, 'Identificción de la muestra')
        p.drawString(50, 600, 'Laboratorio de suelos agricolas: Ensayo ('+str(resultado.ensayo.codigo)+') '+
                     str(resultado.ensayo.descripcion[:1].upper())+str(resultado.ensayo.descripcion[1:].lower()))

        data = [
            [Paragraph('<b>Descripción del resultado</b>', estilo["BodyText"]), Paragraph('<b>Resultado</b>', estilo["BodyText"]),
             Paragraph('<b>Unidad</b>', estilo["BodyText"]), Paragraph('<b>Método</b>', estilo["BodyText"]),
             Paragraph('<b>Nivel</b>', estilo["BodyText"])],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
            ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']]

        fila = 1

        if resultado.ph != None:
            text = resultado.ph.split('#')
            data[fila][0] = 'pH'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 5.5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 6.5:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.ce != None:
            text = resultado.ce.split('#')
            data[fila][0] = 'Conductividad Electrica C.E'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) > 0 and float(text[0]) < 2:
                data[fila][4] = 'Medio'
            elif float(text[0]) > 4:
                data[fila][4] = 'Alto'
            fila += 1

        if resultado.co != None:
            text = resultado.co.split('#')
            data[fila][0] = 'Carbono Orgánico Oxidable (CO)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'XXXX'
            fila += 1

        if resultado.mo != None:
            text = resultado.mo.split('#')
            data[fila][0] = 'Materia Orgnica (M.O)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'XXXX'
            fila += 1

        if resultado.n != None:
            text = resultado.n.split('#')
            data[fila][0] = 'Nitrogeno Total (N)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'XXXX'
            fila += 1

        if resultado.p != None:
            text = resultado.p.split('#')
            data[fila][0] = 'Fósforo (P)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 15:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 40:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.k != None:
            text = resultado.k.split('#')
            data[fila][0] = 'Potasio (K)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 0.2:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 0.4:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.ca != None:
            text = resultado.ca.split('#')
            data[fila][0] = 'Calcio (Ca)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 3:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 6:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.mg != None:
            text = resultado.mg.split('#')
            data[fila][0] = 'Magnesio (Mg)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 1.5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 2.5:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.al != None:
            text = resultado.al.split('#')
            data[fila][0] = 'Aluminio (Al)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 1:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 1:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.na!= None:
            text = resultado.na.split('#')
            data[fila][0] = 'Sodio (Na)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 0.1:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 0.5:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.cic != None:
            text = resultado.cic.split('#')
            data[fila][0] = 'Intercambio Cationico (CIC)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 10:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 20:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.cice != None:
            text = resultado.cice.split('#')
            data[fila][0] = 'Intercambio Cationico E (CICE)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 0.2:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 0.4:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.s != None:
            text = resultado.s.split('#')
            data[fila][0] = 'Azufre (S)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 10:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.fe != None:
            text = resultado.fe.split('#')
            data[fila][0] = 'Hierro (Fe)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 25:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 50:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.mn != None:
            text = resultado.mn.split('#')
            data[fila][0] = 'Manganeso (Mn)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 10:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.cu != None:
            text = resultado.cu.split('#')
            data[fila][0] = 'Cobre (Cu)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 1:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 3:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.zn != None:
            text = resultado.zn.split('#')
            data[fila][0] = 'Zinc (Zn)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 1.5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 3:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.b != None:
            text = resultado.b.split('#')
            data[fila][0] = 'Boro (B)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 0.2:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 0.4:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        #relaciones cationicas

        if resultado.ca_mg != None:
            text = resultado.ca_mg.split('#')
            data[fila][0] = 'Ca/Mg'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 3:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 5:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.ca_k != None:
            text = resultado.ca_k.split('#')
            data[fila][0] = 'Ca/K'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 15:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 30:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.mg_k != None:
            text = resultado.mg_k.split('#')
            data[fila][0] = 'Mg/K'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 10:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 15:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.ca_mg_k != None:
            text = resultado.ca_mg_k.split('#')
            data[fila][0] = '(Ca+Mg)/K'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 20:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 40:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.sat_na != None:
            text = resultado.sat_na.split('#')
            data[fila][0] = '% Sat de Sodio (Na)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 5:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 15:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.sat_k != None:
            text = resultado.sat_k.split('#')
            data[fila][0] = '% Sat de Potasio (K)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 2:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 3:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.sat_ca != None:
            text = resultado.sat_ca.split('#')
            data[fila][0] = '% Sat de Calcio (Ca)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 50:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 70:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.sat_mg != None:
            text = resultado.sat_mg.split('#')
            data[fila][0] = '% Sat de Magnesio (Mg)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 10:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 20:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        if resultado.sat_al != None:
            text = resultado.sat_al.split('#')
            data[fila][0] = '% Sat de Aluminio (Al)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            if float(text[0]) < 20:
                data[fila][4] = 'Bajo'
            elif float(text[0]) > 50:
                data[fila][4] = 'Alto'
            else:
                data[fila][4] = 'Medio'
            fila += 1

        #texturas

        if resultado.textura_1 != None:
            text = resultado.textura_1.split('#')
            data[fila][0] = 'Textura (1)'
            data[fila][1] = text[0]+' -- ' + text[2]

        if resultado.t2_arena != None:
            text = resultado.t2_arena.split('#')
            data[fila][0] = 'Textura  Arena (2)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'NA'
            fila += 1

        if resultado.t2_arcilla != None:
            text = resultado.t2_arcilla.split('#')
            data[fila][0] = 'Textura  Arcilla (2)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'NA'
            fila += 1

        if resultado.t2_limo != None:
            text = resultado.t2_limo.split('#')
            data[fila][0] = 'Textura  Limo (2)'
            data[fila][1] = text[0]
            data[fila][2] = text[1]
            data[fila][3] = text[2]
            data[fila][4] = 'NA'
            fila += 1

        if resultado.t2_clase != None:
            data[fila][0] = 'Clase de Textura (2)'
            data[fila][1] = resultado.t2_clase

        if resultado.ensayo.codigo == '0602' or resultado.ensayo.codigo == '0626':
            table = Table(data=data,
                          style=[
                              # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                              ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                              ('ALIGN', (1, 1), (2, 29), 'CENTER'),
                              ('ALIGN', (4, 1), (4, 29), 'CENTER'),
                              # ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                              ('FONT', (0, 0), (4, 29), 'Times-Roman'),
                              ('SIZE', (0, 0), (4, 29), 10),
                              ('VALIGN', (0, 1), (4, 29), 'MIDDLE'),
                              ('SPAN', (1, fila), (4, fila)),
                          ], colWidths=(150, 62, 50, 211, 36), rowHeights=14
                          )
        elif resultado.ensayo.codigo == '0601':
            table = Table(data=data,
                          style=[
                              # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                              ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                              ('ALIGN', (1, 1), (2, 29), 'CENTER'),
                              ('ALIGN', (4, 1), (4, 29), 'CENTER'),
                              # ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                              ('FONT', (0, 0), (4, 29), 'Times-Roman'),
                              ('SIZE', (0, 0), (4, 29), 10),
                              ('VALIGN', (0, 1), (4, 29), 'MIDDLE'),
                              ('SPAN', (1, fila), (4, fila)),
                          ], colWidths=(150, 62, 50, 211, 36), rowHeights=14
                          )
        else:
            table = Table(data=data,
                          style=[
                              # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                              ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                              ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                              ('ALIGN', (1, 1), (2, 29), 'CENTER'),
                              ('ALIGN', (4, 1), (4, 29), 'CENTER'),
                              # ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                              ('FONT', (0, 0), (4, 29), 'Times-Roman'),
                              ('SIZE', (0, 0), (4, 29), 10),
                              ('VALIGN', (0, 1), (4, 29), 'MIDDLE'),
                          ], colWidths=(150, 62, 50, 211, 36), rowHeights=14
                          )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 175)
        p.drawString(60, 162, 'Codigo de verificación: '+str(resultado.verificacion))
        vacio = [['']]

        encargado = User.objects.get(username=resultado.encargado)
        # p.drawImage(ruta_view+'/firmas/firmas/'+str(encargado.codigo)+'.jpg', 60, 120, width=200, height=40)
        p.drawString(60, 112, str(encargado.first_name).upper())
        p.drawString(60, 102, 'Analista: Lab Suelos Agricolas-UFPS')
        p.line(60, 122, 250, 122)

        jefe = User.objects.get(username=resultado.jefe)
        p.drawImage(ruta_view+'/firmas/firmas/'+str(resultado.jefe)+'.jpg', 310, 120, width=200, height=40)
        p.drawString(310, 112, str(jefe.first_name).upper())
        p.drawString(400, 162, 'N° Orden: ' + str(resultado.orden.id))
        p.drawString(310, 102, 'Vo. Bo. Jefe Division de Servicios Académicos.')
        p.line(310, 122, 540, 122)

        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           #('FONT', (0, 1), (0, 1), 'Times-Roman'),
                           #('SIZE', (0, 1), (0, 1), 12),
                           # ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
                           # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                       ], colWidths=510, rowHeights=60
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 100)

        p.setFont("Times-Roman", 10)
        p.drawString(90, 80, 'UNIVERSIDAD FRANCISCO DE PAULA SANTANDER - DIVISION DE SERVICIOS ACADEMICOS')

        p.setFont("Times-Roman", 8)
        p.setFillColorRGB(1, 0, 0)  # cambia el color de la letra a rojo
        p.drawString(130, 70, 'Avenda Gran Colombia N° E - 96 B. Colsag. Telefax. 5753256 e-mail diseraca@ufps.edu.co')
        p.drawString(280, 60, 'CUCUTA - COLOMBIA')

        p.showPage()
        p.save()
        return response


@login_required(login_url='/')
def get_resultado_editar_sa(request):
    resultado = Resultado_suelos_agricolas.objects.get(id=request.GET['resultado'])
    salida = '%s\%s\%s\%s\%s\%s\%s\%s\%s\%s' % (resultado.id, resultado.ensayo.codigo, resultado.propietario,
                                                resultado.fecha_recepcion, resultado.departamento, resultado.municipio,
                                                resultado.vereda, resultado.finca, resultado.lote, resultado.cultivo)

    salida += '\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s\%s' \
              % (resultado.ph, resultado.ce, resultado.mo, resultado.co, resultado.n, resultado.p, resultado.k,
                 resultado.ca, resultado.mg, resultado.al, resultado.na, resultado.cic, resultado.cice, resultado.s,
                 resultado.fe, resultado.mn, resultado.cu, resultado.zn, resultado.b)

    salida += '\%s\%s\%s\%s\%s\%s\%s\%s\%s' % (resultado.ca_mg, resultado.ca_k, resultado.mg_k, resultado.ca_mg_k,
                                                 resultado.sat_na, resultado.sat_k, resultado.sat_ca, resultado.sat_mg,
                                                resultado.sat_al)

    salida += '\%s\%s\%s\%s\%s' % (resultado.textura_1, resultado.t2_arena, resultado.t2_arcilla, resultado.t2_limo,
                                  resultado.t2_clase)
    return HttpResponse(salida.encode('UTF-8'))


@login_required(login_url='/')
def editar_resultado_sa(request):
    if request.method == 'POST':
        resultado = Resultado_suelos_agricolas.objects.get(id=request.POST['id'])
        resultado.propietario = request.POST['propietario']
        resultado.fecha_recepcion = request.POST['fecha_recepcion']
        resultado.departamento = request.POST['departamento']
        resultado.municipio = request.POST['municipio']
        resultado.vereda = request.POST['vereda']
        resultado.finca = request.POST['finca']
        resultado.lote = request.POST['lote']
        resultado.cultivo = request.POST['cultivo']

        # resultados de los analisis quimico
        # cada resultado se divide en 3 partes separados por comas, (resultados, unidad, metodo)
        if 'resultado_ph' in request.POST:
            resultado.ph = request.POST['resultado_ph']+'#' + request.POST['unidad_ph'] + '#' + request.POST['metodo_ph']
        if 'resultado_ce' in request.POST:
            resultado.ce = request.POST['resultado_ce']+'#' + request.POST['unidad_ce'] + '#' + request.POST['metodo_ce']
        if 'resultado_co' in request.POST:
            resultado.co = request.POST['resultado_co']+'#'+request.POST['unidad_co']+'#'+request.POST['metodo_co']
        if 'resultado_mo' in request.POST:
            resultado.mo = request.POST['resultado_mo'] + '#' + request.POST['unidad_mo'] + '#' + request.POST['metodo_mo']
        if 'resultado_n' in request.POST:
            resultado.n = request.POST['resultado_n'] + '#' + request.POST['unidad_n'] + '#' + request.POST['metodo_n']
        if 'resultado_p' in request.POST:
            resultado.p = request.POST['resultado_p'] + '#' + request.POST['unidad_p'] + '#' + request.POST['metodo_p']
        if 'resultado_k' in request.POST:
            resultado.k = request.POST['resultado_k'] + '#' + request.POST['unidad_k'] + '#' + request.POST['metodo_k']
        if 'resultado_ca' in request.POST:
            resultado.ca = request.POST['resultado_ca'] + '#' + request.POST['unidad_ca'] + '#' + request.POST['metodo_ca']
        if 'resultado_mg' in request.POST:
            resultado.mg = request.POST['resultado_mg'] + '#' + request.POST['unidad_mg'] + '#' + request.POST['metodo_mg']
        if 'resultado_al' in request.POST:
            resultado.al = request.POST['resultado_al'] + '#' + request.POST['unidad_al'] + '#' + request.POST['metodo_al']
        if 'resultado_na' in request.POST:
            resultado.na = request.POST['resultado_na'] + '#' + request.POST['unidad_na'] + '#' + request.POST['metodo_na']
        if 'resultado_cic' in request.POST:
            resultado.cic = request.POST['resultado_cic'] + '#' + request.POST['unidad_cic']+'#'+request.POST['metodo_cic']
        if 'resultado_cice' in request.POST:
            resultado.cice = request.POST['resultado_cice']+'#'+request.POST['unidad_cice']+'#'+request.POST['metodo_cice']  # mirar formula
        if 'resultado_ai' in request.POST:
            resultado.acidez = request.POST['resultado_ai']+'#'+request.POST['unidad_ai']+'#'+request.POST['metodo_ai']
        if 'resultado_s' in request.POST:
            resultado.s = request.POST['resultado_s'] + '#' + request.POST['unidad_s'] + '#' + request.POST['metodo_s']
        if 'resultado_fe' in request.POST:
            resultado.fe = request.POST['resultado_fe'] + '#' + request.POST['unidad_fe'] + '#' + request.POST['metodo_fe']
        if 'resultado_mn' in request.POST:
            resultado.mn = request.POST['resultado_mn'] + '#' + request.POST['unidad_mn'] + '#' + request.POST['metodo_mn']
        if 'resultado_cu' in request.POST:
            resultado.cu = request.POST['resultado_cu'] + '#' + request.POST['unidad_cu'] + '#' + request.POST['metodo_cu']
        if 'resultado_zn' in request.POST:
            resultado.zn = request.POST['resultado_zn'] + '#' + request.POST['unidad_zn'] + '#' + request.POST['metodo_zn']
        if 'resultado_b' in request.POST:
            resultado.b = request.POST['resultado_b'] + '#' + request.POST['unidad_b'] + '#' + request.POST['metodo_b']

        # relaciones cationicas
        if 'resultado_ca_mg' in request.POST:
            resultado.ca_mg = request.POST['resultado_ca_mg'] + '#' + request.POST['unidad_ca_mg'] + '#' + request.POST[
            'metodo_ca_mg']
        if 'resultado_ca_k' in request.POST:
            resultado.ca_k = request.POST['resultado_ca_k'] + '#' + request.POST['unidad_ca_k'] + '#' + request.POST[
            'metodo_ca_k']
        if 'resultado_mg_k' in request.POST:
            resultado.mg_k = request.POST['resultado_mg_k'] + '#' + request.POST['unidad_mg_k'] + '#' + request.POST[
            'metodo_mg_k']
        if 'resultado_ca_mg_k' in request.POST:
            resultado.ca_mg_k = request.POST['resultado_ca_mg_k'] + '#' + request.POST['unidad_ca_mg_k'] + '#' + \
                            request.POST['metodo_ca_mg_k']

        if 'resultado_sat_na' in request.POST:
            resultado.sat_na = request.POST['resultado_sat_na'] + '#' + request.POST['unidad_sat_na'] + '#' + \
                            request.POST['metodo_sat_na']
        if 'resultado_sat_k' in request.POST:
            resultado.sat_k = request.POST['resultado_sat_k'] + '#' + request.POST['unidad_sat_k'] + '#' + \
                            request.POST['metodo_sat_k']
        if 'resultado_sat_ca' in request.POST:
            resultado.sat_ca = request.POST['resultado_sat_ca'] + '#' + request.POST['unidad_sat_ca'] + '#' + \
                            request.POST['metodo_sat_ca']
        if 'resultado_sat_mg' in request.POST:
            resultado.sat_mg = request.POST['resultado_sat_mg'] + '#' + request.POST['unidad_sat_mg'] + '#' + \
                            request.POST['metodo_sat_mg']
        if 'resultado_sat_al' in request.POST:
            resultado.sat_al = request.POST['resultado_sat_al'] + '#' + request.POST['unidad_sat_al'] + '#' + \
                            request.POST['metodo_sat_al']

        # analisis fisico
        if 'resultado_t1' in request.POST:
            resultado.textura_1 = request.POST['resultado_t1'] + '#' + request.POST['unidad_t1'] + '#' + request.POST[
            'metodo_t1']

        if 'metodo_t2_arena' in request.POST:
            resultado.t2_arena = request.POST['resultado_t2_arena'] + '#' + request.POST['unidad_t2_arena'] + '#' + \
                             request.POST['metodo_t2_arena']
        if 'metodo_t2_arcilla' in request.POST:
            resultado.t2_arcilla = request.POST['resultado_t2_arcilla'] + '#' + request.POST['unidad_t2_arcilla'] + '#' + \
                               request.POST['metodo_t2_arcilla']
        if 'metodo_t2_limo' in request.POST:
            resultado.t2_limo = request.POST['resultado_t2_limo'] + '#' + request.POST['unidad_t2_limo'] + '#' + \
                            request.POST['metodo_t2_limo']
        if 'clase_t2' in request.POST:
            resultado.t2_clase = request.POST['clase_t2']

        #resultado.observacion = request.POST['observacion']


        resultado.save()

        return HttpResponse('ok')
    return HttpResponse('not')

# --------------- fin crud de Ensayos de suelos agricolas------------


# ---------------views de las cotizaciones ------------------------
@login_required(login_url='/')
def lista_ensayo_cotizacion(request):
    if request.method == 'GET':
        usuario = Persona.objects.get(user__username=request.session['usuario'])
        ensayo = Ensayo.objects.filter(laboratorio=usuario.laboratorio)

        data = serializers.serialize('json', ensayo, fields=('descripcion', 'valor', 'codigo'))
        return HttpResponse(data, content_type='application/json')
    else:
        return Http404


@login_required(login_url='/')
def cotizacion_pdf_lab(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.setFont("Times-Roman", 12)
        p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 180, 200, width=420, height=420)
        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)

        estilo = getSampleStyleSheet()

        p.drawString(140, 760, 'GESTION DE SERVICIOS ACADEMICOS')
        p.drawString(125, 730, 'COTIZACIÓN DE SERVICIOS DE LABORATORIOS')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GA-01 /v 0</b>', estilo["BodyText"])

        data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]
        table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (3, 1), 'CENTER'),
            # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 50, 722)
        vacio = [['']]

        marco1 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                       ], colWidths=510, rowHeights=90
                       )
        marco1.wrapOn(p, 100, 400)
        marco1.drawOn(p, 50, 620)

        # encabezado
        p.setFont("Times-Roman", 10)

        p.drawString(55, 690, 'FECHA:')
        dic_mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                   9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

        fecha = '%s DE %s DEL %s' % (datetime.date.today().day, dic_mes[datetime.date.today().month], str(datetime.date.today().year))

        p.drawString(95, 690, fecha.upper())
        p.line(95, 687, 285, 687)

        p.drawString(290, 690, 'LABORATORIO:')
        usuario = Persona.objects.get(user__username=request.session['usuario'])
        p.drawString(370, 690, usuario.laboratorio.nombre.upper()[:33])
        p.line(370, 687, 550, 687)

        p.drawString(55, 670, 'INTERESADO:')
        p.drawString(130, 670, request.POST['nombre'].upper()[:24])
        p.line(130, 667, 285, 667)

        p.drawString(290, 670, 'CÉDULA / NIT:')
        p.drawString(370, 670, request.POST['empresa'].upper())
        p.line(370, 667, 550, 667)

        p.drawString(55, 650, 'DIRECCIÓN:')
        p.drawString(120, 650, request.POST['direccion'].upper()[:33])
        p.line(120, 647, 285, 647)

        p.drawString(290, 650, 'EMAIL:')
        p.drawString(330, 650, request.POST['email'].upper()[:31])
        p.line(330, 647, 550, 647)

        p.drawString(55, 630, 'TELEFONOS:')
        p.drawString(125, 630, request.POST['tel'][:23])
        p.line(125, 627, 285, 627)
        # p.setFont("Helvetica", 5)

        ensayo = Paragraph('<b>N° ENSAYO</b>', estilo["BodyText"])
        des_ensayo = Paragraph('<b>DESCRIPCIÓN DEL ENSAYO</b>', estilo["BodyText"])
        cantidad = Paragraph('<b>CANTIDAD</b>', estilo["BodyText"])
        data = [[ensayo, des_ensayo, cantidad, Paragraph('<b>VALOR UNI.</b>', estilo["BodyText"]),
                 Paragraph('<b>SUBTOTAL</b>', estilo["BodyText"])], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', '']]
        ensayos = int(request.POST['ensayos'])
        if ensayos > 16:
            return HttpResponse('Solo ingrese un maximo de 16 ensayos en cada Cotizacion')
        x = 1
        for i in range(ensayos):
            ww = 'codigo_tb%s' % (str(i))

            if ww in request.POST:
                data[x][0] = request.POST[('codigo_tb%s' % (str(i)))]
                desc = request.POST[('descripcion_tb%s' % (str(i)))]

                if len(desc) > 35:
                    data[x][1] = desc[:30] + '...'
                else:
                    data[x][1] = desc

                data[x][2] = request.POST[('cantidad_tb%s' % (str(i)))]
                data[x][3] = request.POST[('valor_tb%s' % (str(i)))]
                data[x][4] = request.POST[('sub_tb%s' % (str(i)))]
                x += 1

        table = Table(data=data,
                      style=[
                          # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                          ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                          ('ALIGN', (2, 1), (4, 16), 'CENTER'),
                          ('FONT', (0, 0), (4, 16), 'Times-Roman'),
                          ('SIZE', (0, 0), (4, 16), 12),
                      ], colWidths=(70, 235, 65, 70, 70), rowHeights=20
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 270)

        p.setFont("Times-Roman", 12)

        total = request.POST['total']
        descuento = request.POST['descuento']

        if 'beneficiario' in request.POST:
            beneficiario = '1'
            p.drawString(300, 250, 'SUBTOTAL:  $')
            sub = int(total) * 2
            p.drawString(430, 250, str(sub))

            p.drawString(300, 235, 'DESCUENTO 50%:  $')
            p.drawString(430, 235, descuento)

            p.drawString(300, 220, 'TOTAL:  $')
            p.drawString(430, 220, total)

            p.setFillColorRGB(1, 0, 0)
            p.drawString(55, 235, 'BENEFICIARIO ACUERDO')
            p.setFillColorRGB(0, 0, 0)

        else:
            p.drawString(300, 235, 'VALOR TOTAL: $')
            p.drawString(430, 235, total)

        vacio = [[''], ['']]

        vacio[0][0] = 'OBSERVACION: \nSi esta de acuerdo con la propuesta favor consignar en la cuenta de ahorros ' \
                      'N° 83248722510 de BANCOLOMBIA código\nCONVENIO 29573 formato de RECAUDOS a nombre de ' \
                      'UFPS-FRIE SERVICIOS ACADÉMICOS\n'

        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('FONT', (0, 0), (0, 0), 'Times-Roman'),
                           ('SIZE', (0, 0), (0, 0), 10),
                           # ('VALIGN', (0, 1), (0, 1), 'TOP'),
                           # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                       ], colWidths=510, rowHeights=60
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 88)
        p.drawString(80, 103, 'Vo. Bo. Jefe División de Servicios Académicos.')

        jefes = Persona.objects.filter(tipo=1, user__is_active=True)


        # el cuadro de la firma debe ser de 7.5 cm X 1.5 cm y de 700 X 110 px en la imagen jpg
        p.drawImage(ruta_view+'/firmas/firmas/'+str(jefes[0].user.username)+'.jpg', 340, 100, width=200, height=40)
        p.line(340, 100, 540, 100)
        p.setFont("Times-Roman", 7)
        p.drawString(340, 90, str(jefes[0].user.first_name).upper())
        # p.drawString(340, 90, 'NOMBRE DEL JEFE: '+str(j.nombre).upper())

        # Close the PDF object cleanly, and we're done.

        data_pie = [['Elaboró:', 'Revisó:', 'Aprobó:'], ['Fecha:', 'Fecha:', 'Fecha:']]
        data_pie = Table(data_pie, colWidths=170, rowHeights=18)
        data_pie.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('FONT', (0, 0), (2, 1), 'Times-Roman'),
            ('SIZE', (0, 0), (2, 1), 12),
        ]))
        data_pie.wrapOn(p, 100, 400)
        data_pie.drawOn(p, 50, 42)
        p.showPage()
        p.save()
        return response
        # se recoren los ensayos que se agregaron en el formulario i en el numero que completa el name que

    else:
        return Http404


@login_required(login_url='/')
def cotizacion_pdf_admin(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="orden.pdf"'

        # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.setFont("Times-Roman", 12)
        p.drawImage(ruta_view + '/laboratorios/static/img/fondo.jpg', 180, 200, width=420, height=420)
        p.drawImage(ruta_view + '/laboratorios/static/img/ufps.png', 33, 707.5, width=93, height=83)

        estilo = getSampleStyleSheet()

        p.drawString(140, 760, 'GESTION DE SERVICIOS ACADEMICOS')
        p.drawString(125, 730, 'COTIZACIÓN DE SERVICIOS DE LABORATORIOS')

        P2 = Paragraph('<b>CÓDIGO</b>', estilo["BodyText"])
        P3 = Paragraph(' <b>FO-GA-01 /v 0</b>', estilo["BodyText"])

        data_encabezado = [['', '', P2, P3], ['', '', 'PAGINAS', '1/1']]
        table_encabezado = Table(data_encabezado, colWidths=(62, 300, 66, 82), rowHeights=28)
        table_encabezado.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('TEXTFONT', (0, 1), (-1, 1), 'Times-Roman'),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('ALIGN', (0, 0), (3, 1), 'CENTER'),
            # ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        table_encabezado.wrapOn(p, 100, 400)
        table_encabezado.drawOn(p, 50, 722)
        vacio = [['']]

        marco1 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                       ], colWidths=510, rowHeights=90
                       )
        marco1.wrapOn(p, 100, 400)
        marco1.drawOn(p, 50, 620)

        # encabezado
        p.setFont("Times-Roman", 10)

        p.drawString(55, 690, 'FECHA:')
        dic_mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                   9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        fecha_orden = datetime.date.today()
        fecha = '%s DE %s DEL %s' % (fecha_orden.day, dic_mes[fecha_orden.month], fecha_orden.year)

        p.drawString(95, 690, fecha.upper())
        p.line(95, 687, 285, 687)
        laboratorio = Tipo_Laboratorio.objects.get(id=request.POST['laboratorio'])
        p.drawString(310, 690, 'LABORATORIO:')

        p.drawString(390, 690, laboratorio.nombre.upper()[:33])
        p.line(390, 687, 550, 687)

        p.drawString(55, 670, 'INTERESADO:')
        p.drawString(130, 670, request.POST['nombre'].upper()[:24])
        p.line(130, 667, 285, 667)

        p.drawString(310, 670, 'CÉDULA / NIT:')
        p.drawString(390, 670, request.POST['empresa'].upper())
        p.line(390, 667, 550, 667)

        p.drawString(55, 650, 'DIRECCIÓN:')
        p.drawString(120, 650, request.POST['direccion'].upper()[:33])
        p.line(120, 647, 285, 647)

        p.drawString(310, 650, 'EMAIL:')
        p.drawString(350, 650, request.POST['email'].upper()[:31])
        p.line(350, 647, 550, 647)

        p.drawString(55, 630, 'TELEFONOS:')
        p.drawString(125, 630, request.POST['tel'][:23])
        p.line(125, 627, 285, 627)
        # p.setFont("Helvetica", 5)

        ensayo = Paragraph('<b>N° ENSAYO</b>', estilo["BodyText"])
        des_ensayo = Paragraph('<b>DESCRIPCIÓN DEL ENSAYO</b>', estilo["BodyText"])
        cantidad = Paragraph('<b>CANTIDAD</b>', estilo["BodyText"])
        data = [[ensayo, des_ensayo, cantidad, Paragraph('<b>VALOR UNI.</b>', estilo["BodyText"]),
                 Paragraph('<b>SUBTOTAL</b>', estilo["BodyText"])], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                ['', '', '', '', '']]
        ensayos = int(request.POST['ensayos'])
        x = 1
        for i in range(ensayos):
            if 'codigo_tb%d' % (i) in request.POST:
                data[x][0] = request.POST[('codigo_tb%s' % (i))]
                desc = request.POST[('descripcion_tb%s' % (i))]

                if len(desc) > 35:
                    data[x][1] = desc[:30] + '...'
                else:
                    data[x][1] = desc

                data[x][2] = request.POST[('cantidad_tb%s' % (i))]
                data[x][3] = request.POST[('valor_tb%s' % (i))]
                data[x][4] = request.POST[('sub_tb%s' % (i))]
                x += 1

        table = Table(data=data,
                      style=[
                          # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                          ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                          ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                          ('ALIGN', (0, 1), (0, 16), 'CENTER'),
                          ('ALIGN', (2, 1), (4, 16), 'CENTER'),
                          ('FONT', (0, 0), (4, 16), 'Times-Roman'),
                          ('SIZE', (0, 0), (4, 16), 12),
                      ], colWidths=(70, 235, 65, 70, 70), rowHeights=20
                      )

        table.wrapOn(p, 100, 400)
        table.drawOn(p, 50, 270)

        p.setFont("Times-Roman", 12)

        total = request.POST['total']
        descuento = request.POST['descuento']

        if 'beneficiario' in request.POST:
            beneficiario = '1'
            p.drawString(300, 250, 'SUBTOTAL:  $')
            sub = int(total) * 2
            p.drawString(430, 250, str(sub))

            p.drawString(300, 235, 'DESCUENTO 50%:  $')
            p.drawString(430, 235, descuento)

            p.drawString(300, 220, 'TOTAL:  $')
            p.drawString(430, 220, total)

            p.setFillColorRGB(1, 0, 0)
            p.drawString(55, 235, 'BENEFICIARIO ACUERDO')
            p.setFillColorRGB(0, 0, 0)

        else:
            p.drawString(300, 235, 'VALOR TOTAL: $')
            p.drawString(430, 235, total)

        vacio = [[''], ['']]

        vacio[0][0] = 'OBSERVACION: \nSi esta de acuerdo con la propuesta favor consignar en la cuenta de ahorros ' \
                      'N° 83248722510 de BANCOLOMBIA código\nCONVENIO 29573 formato de RECAUDOS a nombre de ' \
                      'UFPS-FRIE SERVICIOS ACADÉMICOS\n'

        marco2 = Table(data=vacio,
                       style=[
                           # ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                           # ALIGN: LEFT (default) | CENTER | RIGHT | DECIMAL
                           # VALIGN: BOTTOM (default) | MIDDLE | TOP
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('FONT', (0, 0), (0, 0), 'Times-Roman'),
                           ('SIZE', (0, 0), (0, 0), 10),
                           # ('VALIGN', (0, 1), (0, 1), 'TOP'),
                           # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                       ], colWidths=510, rowHeights=60
                       )

        marco2.wrapOn(p, 100, 100)
        marco2.drawOn(p, 50, 88)
        p.drawString(80, 103, 'Vo. Bo. Jefe División de Servicios Académicos.')

        jefes = Persona.objects.filter(tipo=1, user__is_active=True)

        # el cuadro de la firma debe ser de 7.5 cm X 1.5 cm y de 700 X 110 px en la imagen jpg
        p.drawImage(ruta_view+'/firmas/firmas/'+str(jefes[0].user.username)+'.jpg', 340, 100, width=200, height=40)
        p.line(340, 100, 540, 100)
        p.setFont("Times-Roman", 7)
        p.drawString(340, 90, str(jefes[0].user.first_name).upper())
        # p.drawString(340, 90, 'NOMBRE DEL JEFE: '+str(j.nombre).upper())

        # Close the PDF object cleanly, and we're done.

        data_pie = [['Elaboró:', 'Revisó:', 'Aprobó:'], ['Fecha:', 'Fecha:', 'Fecha:']]
        data_pie = Table(data_pie, colWidths=170, rowHeights=18)
        data_pie.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (0, 0), (0, 1)),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            # ('SPAN', (1, 0), (1, 1)),
            ('VALIGN', (1, 0), (1, 1), 'MIDDLE'),
            ('FONT', (0, 0), (2, 1), 'Times-Roman'),
            ('SIZE', (0, 0), (2, 1), 12),
        ]))
        data_pie.wrapOn(p, 100, 400)
        data_pie.drawOn(p, 50, 42)
        p.showPage()
        p.save()
        return response


#---------------- fin views de las cotizaciones -------------------


#---------------- inicio busqueda de resultados y anulacion----------
@login_required(login_url='/')
def buscar_resultado(request):
    if 'busqueda' in request.GET:
        if request.GET['busqueda'][:2] == '04':#lab de aguas
            try:
                res = Resultado_Aguas.objects.get(verificacion=request.GET['busqueda'])
                if res.estado == '1' or res.estado == '2':
                    out = '<th>%s</th><th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_aguas?id=%s" target="_blank" class="btn-danger">Imprimir</a></th>' \
                          '<th><button class="btn btn-danger" onclick="anular_resultado(\'%s\')" type="button">Anular</button>' \
                          '</th>' % (
                              res.fecha, res.codigo, res.municipio, res.tipo_muestra, res.id, request.GET['busqueda'])
                else:
                    out = '<th>%s</th><th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_aguas?id=%s" target="_blank" class="btn-danger">Imprimir</a></th>' \
                          '<th>Anulado</th>' % (res.fecha, res.codigo, res.municipio, res.tipo_muestra, res.id)

                tabla = '<br/>Reporte de Analisis de Aguas:<br/><br/><table class="table table-hover">' \
                        '<thead>    <tr>  <th>Fecha</th>  <th>Codigo de muestra</th> <th>Municipio</th> <th>Tipo muestra' \
                        '</th> <th>Imprimir</th> <th>Anular</th> </tr> </thead><tbody>%s</tbody> </table>' %(out)

                return HttpResponse(tabla)
            except Resultado_Aguas.DoesNotExist:
                return HttpResponse('not')
        elif request.GET['busqueda'][:2] == '05': #lab analisis de alimentos
            try:
                res = Resultado_Nutricion_Animal.objects.get(verificacion=request.GET['busqueda'])
                if res.estado == '1' or res.estado == '2':
                    out = '<th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_nutricion?id=%s" target="_blank" class="btn-danger">Imprimir</a></th>' \
                          '<th><button class="btn btn-danger" onclick="anular_resultado(\'%s\')" type="button">Anular</button>' \
                          '</th>' % (res.fecha, res.codigo, res.tipo, res.id, request.GET['busqueda'])
                else:
                    out = '<th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_nutricion?id=%s" target="_blank" class="btn-danger">Imprimir</a></th>' \
                          '<th>Anulado</th>' % (res.fecha, res.codigo, res.tipo, res.id)

                tabla = '<br/>Reporte de Analisis de alimentos y nutricion animal:<br/><br/><table class="table table' \
                        '-hover"><thead>    <tr>  <th>Fecha</th>  <th>Codigo de muestra</th> <th>Tipo muestra' \
                        '</th> <th>Imprimir</th> <th>Anular</th> </tr> </thead><tbody>%s</tbody> </table>' %(out)

                return HttpResponse(tabla)
            except Resultado_Nutricion_Animal.DoesNotExist:
                return HttpResponse('not')
        elif request.GET['busqueda'][:2] == '06': #lab suelos agricolas
            try:
                res = Resultado_suelos_agricolas.objects.get(verificacion=request.GET['busqueda'])
                if res.estado == '1' or res.estado == '2':
                    out = '<th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_agricolas?id=%s" target="_blank" class="btn-danger">' \
                          'Imprimir</a></th><th><button class="btn btn-danger" onclick="anular_resultado(\'%s\')" ' \
                          'type="button">Anular</button></th>' % (res.propietario, res.vereda, res.finca, res.lote,
                                                                  res.cultivo, res.id, request.GET['busqueda'])
                else:
                    out = '<th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>' \
                          '<th><a href="imprimir_resultado_agricolas?id=%s" target="_blank" class="btn-danger">Imprimir</a></th>' \
                          '<th>Anulado</th>' % (res.propietario, res.vereda, res.finca, res.lote, res.cultivo, res.id)

                tabla = '<br/>Reporte de Analisis de Suelos agricolas:<br/><br/><table class="table table' \
                        '-hover"><thead>    <tr>  <th>Propietario</th>  <th>Vereda</th> <th>Finca' \
                        '</th> <th>Lote</th> <th>Cultivo</th><th>Imprimir</th> <th>Anular</th> </tr> </thead>' \
                        '<tbody>%s</tbody> </table>' %(out)

                return HttpResponse(tabla)
            except Resultado_suelos_agricolas.DoesNotExist:
                return HttpResponse('not')
        else:
            return HttpResponse('aun no se tiene desarrolladopara otros lab')
    else:
        return HttpResponse('error')


@login_required(login_url='/')
def anular_resultado(request):
    if 'busqueda' in request.GET:
        if request.GET['busqueda'][:2] == '04':#lab de aguas
            try:
                res = Resultado_Aguas.objects.get(verificacion=request.GET['busqueda'])
                res_ensayos = Resultado_agua_ensayo.objects.filter(reporte=res)
                res.orden.terminada='0' #se coloca la orden en 0 para que les salga al laboratorio y
                # pueda agregar el resultado con los datos nuevos
                res.orden.save()

                if res.estado == '1':
                    res.estado = '3'
                    res.save()
                elif res.estado == '2':
                    res.estado = '4'
                    res.save()
                else:
                    return HttpResponse('Resultado de aguas ya anulado anteriormente')

                for i in res_ensayos:
                    x = Orden_Ensayo.objects.filter(orden=res.orden).filter(ensayo=i.ensayo)
                    w = Orden_Ensayo.objects.get(id=x[0].id)
                    w.cantidad += 1
                    w.save()

                return HttpResponse('Resultado anulado satisfactoriamente')
            except Resultado_Aguas.DoesNotExist:
                return HttpResponse('no existe el codigo')
        elif request.GET['busqueda'][:2] == '05':#lab analisis de alimentos
            try:
                res = Resultado_Nutricion_Animal.objects.get(verificacion=request.GET['busqueda'])
                res_ensayos = Resultado_Nutricion_Animal_Ensayo.objects.filter(reporte=res)
                res.orden.terminada='0' #se coloca la orden en 0 para que les salga al laboratorio y
                # pueda agregar el resultado con los datos nuevos
                res.orden.save()
                if res.estado == '1':
                    res.estado = '3'
                    res.save()
                elif res.estado == '2':
                    res.estado = '4'
                    res.save()
                else:
                    return HttpResponse('Resultado de nutricion animal ya anulado anteriormente')

                for i in res_ensayos:
                    x = Orden_Ensayo.objects.filter(orden=res.orden).filter(ensayo=i.ensayo)
                    w = Orden_Ensayo.objects.get(id=x[0].id)
                    w.cantidad += 1
                    w.save()

                return HttpResponse('Resultado de nutricion animal anulado satisfactoriamente')
            except Resultado_Aguas.DoesNotExist:
                return HttpResponse('no existe el codigo')
        elif request.GET['busqueda'][:2] == '06':#suelos agricolas
            try:
                res = Resultado_suelos_agricolas.objects.get(verificacion=request.GET['busqueda'])
                res.orden.terminada='0' #se coloca la orden en 0 para que les salga al laboratorio y
                # pueda agregar el resultado con los datos nuevos
                res.orden.save()

                if res.estado == '1':
                    res.estado = '3'
                    res.save()
                elif res.estado == '2':
                    res.estado = '4'
                    res.save()
                else:
                    return HttpResponse('Resultado de Suelos agricolas ya anulado anteriormente')

                x = Orden_Ensayo.objects.filter(orden=res.orden).filter(ensayo=res.ensayo)
                x[0].cantidad += 1
                x[0].save()
                return HttpResponse('Resultado de Suelos agricolas anulado satisfactoriamente')
            except Resultado_Aguas.DoesNotExist:
                return HttpResponse('no existe el codigo')
        else:
            return HttpResponse('jum ni idea XD')
    else:
        return HttpResponse('error')


#---------------- fin busca de resultados y anulacion----------


#----------------inicio resistencia de materiales-----------------
@login_required(login_url='/')
def resistencia_materiales(request):
    ordenes = Orden.objects.filter(laboratorio__id=2, terminada=0, aprobacion=True)
    usuario = User.objects.get(username=request.session['usuario'])
    return render(request, 'laboratorios/resistencia/index.html', {'usuario': usuario, 'pendientes': ordenes})


#----------------fin resistencia de materiales-----------------




#----------------inicio suelos civiles-----------------
@login_required(login_url='/')
def suelos_civiles(request):
    ordenes = Orden.objects.filter(laboratorio__id=1, terminada=0, aprobacion=True)
    usuario = User.objects.get(username=request.session['usuario'])
    print(ordenes)
    return render(request, 'laboratorios/suelos_civiles/index.html', {'usuario': usuario, 'pendientes': ordenes})


def add_traccion_acero(request):
    if request.method == 'POST':
        print(request.POST)
        return HttpResponse('ok')



#----------------fin suelos civiles-----------------