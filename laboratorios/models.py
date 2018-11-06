from django.db import models
from django.contrib.auth.models import User


class Tipo_Laboratorio(models.Model):
    nombre = models.CharField(max_length=45)
    email = models.EmailField(max_length=70)

    def __unicode__(self):
        return('%s' %(self.id))


class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    laboratorio = models.ForeignKey('Tipo_Laboratorio', null=True)
    encargado = models.BooleanField(default=False)
    direccion = models.CharField(max_length=50, null=True)
    '''
    0 --> admin
    1 --> jefe
    2 --> laboratorista
    3 --> secretaria
    4 --> cliente
    '''
    tipo = models.IntegerField()

    def __unicode__(self):
        return '%s' % self.user.username


class Ensayo(models.Model):
    codigo = models.CharField(max_length=4, unique=True)
    descripcion = models.CharField(max_length=200)
    valor = models.IntegerField()
    #formulario = models.IntegerField()
    laboratorio = models.ForeignKey('Tipo_Laboratorio')
    unidad = models.CharField(max_length=25)
    metodo = models.CharField(max_length=70)
    acreditado = models.BooleanField(default=False)

    def __unicode__(self):
        return ('%s+%s+%s+%s' % (self.id, self.descripcion,self.unidad,self.metodo))


class Orden(models.Model):
    fecha_orden = models.DateField()
    laboratorio = models.ForeignKey('Tipo_Laboratorio')
    persona = models.ForeignKey('Persona')
    beneficiario = models.CharField(max_length=1, default='0')
    #1 si esta con descuento y 0 sin descuento
    total = models.CharField(max_length=10)
    descuento = models.CharField(max_length=10)
    observacion = models.TextField()
    num_factura = models.CharField(max_length=10)
    fecha_factura = models.DateField(null=True)
    consignacion = models.CharField(max_length=30)
    editado = models.CharField(max_length=1, default='0')
    #1 si esta editado  y 0 si no, este funciona para el saber si requiere o no factura.
    requiere_factura = models.CharField(max_length=1, default='1')
    #1 --> si requiere  0 --> no requiere factura

    terminada = models.CharField(max_length=1, default='0')
    #1 --> terminada  0 --> no terminada, 2 --> anulada
    fecha_terminada = models.DateField(null=True)
    jefe = models.CharField(max_length=10)
    pendiente = models.BooleanField(default=False)

    contador_impresiones = models.IntegerField(default=0)
    aprobacion = models.BooleanField(default=False)
    consecutivo_lab = models.CharField(max_length=24, unique=True)

    def __unicode__(self):
        return ('%s, %s, %s, %s, %s, %s' % (self.fecha_factura, self.total, self.descuento, self.observacion, self.num_factura, self.fecha_orden))


class Orden_Ensayo(models.Model):
    orden = models.ForeignKey('Orden')
    ensayo = models.ForeignKey('Ensayo')
    cantidad = models.IntegerField()
    valor_uni = models.CharField(max_length=10)
    subtotal = models.CharField(max_length=10)
    acreditado = models.BooleanField(default=False)

    estado = models.CharField(max_length=1, default='0')
    #1 --> en proceso  0 --> sin iniciar  2 --> terminados
    hechas = models.IntegerField(default=0)

    def __unicode__(self):
        return ('%s, %s, %s, %s, %s' % (self.orden, self.ensayo, self.cantidad, self.valor_uni, self.subtotal))


class Consecutivo_lab(models.Model):
    laboratorio = models.OneToOneField('Tipo_Laboratorio', primary_key=True)
    consecutivo = models.IntegerField(default=1)


class Anulacion_Orden(models.Model):
    orden = models.OneToOneField('Orden')
    motivo = models.TextField()
    usuario = models.CharField(max_length=50)
    fecha = models.DateTimeField()


class Adelanto(models.Model):
    persona = models.ForeignKey('Persona')
    consignacion = models.CharField(max_length=50)
    total_consignado = models.IntegerField()
    saldo = models.IntegerField()
    hechas = models.IntegerField()


class Convenio(models.Model):
    persona = models.ForeignKey('Persona')
    fecha_aprovacion = models.DateField()
    monto = models.IntegerField()
    autorizo = models.CharField(max_length=100)


class Resultado_Compresion_Concreto(models.Model):
    orden_ensayo = models.ForeignKey('Orden_Ensayo')
    obra = models.TextField()
    elemento = models.CharField(max_length=30)
    observacion = models.TextField()
    n_ensayo = models.CharField(max_length=15)
    codigo_verificacion = models.CharField(max_length=120)# orden_id**2 * id * 0,5
    escala = models.CharField(max_length=15)
    correccion = models.CharField(max_length=10)
    factor2 = models.CharField(max_length=20)
    maquina = models.CharField(max_length=20)
    fecha_calibracion = models.CharField(max_length=10)
    jefe = models.CharField(max_length=10)
    encargado = models.CharField(max_length=10)
    verificacion = models.CharField(max_length=20, null=True)  # codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado


class Muestra_Compresion_Concreto(models.Model):
    resultado = models.ForeignKey('Resultado_Compresion_Concreto')
    diametro = models.CharField(max_length=10)
    altura = models.CharField(max_length=10)
    area = models.CharField(max_length=10)# diametro * diametro*3.14156/4*6.4516
    volumen = models.CharField(max_length=10)# area * altura * 2.54
    fecha_recepcion = models.DateField()
    asentamiento = models.CharField(max_length=10)
    tipo_concreto = models.CharField(max_length=10)
    proyeccion = models.CharField(max_length=10)
    num_muestra = models.CharField(max_length=10)
    fecha_elaboracion = models.DateField()
    fecha_ensayo = models.DateField()
    peso_muestra = models.CharField(max_length=10)
    carga_maxima = models.CharField(max_length=10)
    edad = models.CharField(max_length=5)# fecha_ensayo - fecha_elaboracion
    peso_unitario = models.CharField(max_length=10)# peso_muestra / volumen / 1000000

    carga_max_corregida = models.CharField(max_length=10)# factor2 + (correccion * carga_maxima)

    resistencia_kgf = models.CharField(max_length=10)# carga_max_corregida / area
    resistencia_mpa = models.CharField(max_length=10)# resistencia_kgf * 0.101972
    resistencia_psi = models.CharField(max_length=10)# resistencia_kgf * 14.22
    porcentaje_resistencia = models.CharField(max_length=10)# resistencia_psi / proyeccion * 100


class Resultado_Aguas(models.Model):
    orden = models.ForeignKey('Orden')
    nombre = models.TextField(null=True) #
    fecha = models.DateField(auto_now=True)#fecha de la creacion de la orden
    codigo = models.CharField(max_length=20) # codigo de la muestra
    municipio = models.CharField(max_length=20) # municipio
    lugar = models.CharField(max_length=50) # lugar del muestre
    tomado_por = models.CharField(max_length=30) # tomado por
    tipo_muestra = models.CharField(max_length=50)# tipo de muestra
    fecha_muestreo = models.DateField()#feha del muestreo
    hora_muestra = models.CharField(max_length=10) #hora del muestreo
    jefe = models.CharField(max_length=10)
    observacion = models.TextField(null=True)
    encargado = models.CharField(max_length=10)
    verificacion = models.CharField(max_length=20, unique=True)# codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado
    estado = models.CharField(max_length=1)
    # 1-> normal, 2-> resultado de estudiante, 3-> normal anulado, 4-> estudiante anulado


class Resultado_agua_ensayo(models.Model):
    reporte = models.ForeignKey('Resultado_Aguas')
    ensayo = models.ForeignKey('Ensayo')
    codigo = models.CharField(max_length=6)
    descripcion = models.CharField(max_length=125)
    unidad = models.CharField(max_length=25)
    metodo = models.CharField(max_length=50)
    resultado = models.CharField(max_length=10)
    limite = models.CharField(max_length=100)#limite permisible
    acreditado = models.BooleanField()


class Resultado_Nutricion_Animal(models.Model):
    orden = models.ForeignKey('Orden')
    fecha = models.DateField(auto_now=True) #fecha de la creacion del resultado
    codigo = models.CharField(max_length=50) # codigo de la muestra
    tipo = models.CharField(max_length=125) #tipo de la muestra
    descripcion = models.TextField()
    jefe = models.CharField(max_length=10)
    encargado = models.CharField(max_length=10)
    verificacion = models.CharField(max_length=20,  unique=True)
    # codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado
    estado = models.CharField(max_length=1)
    # 1-> normal, 2-> resultado de estudiante, 3-> normal anulado, 4-> estudiante anulado


class Resultado_Nutricion_Animal_Ensayo(models.Model):
    reporte = models.ForeignKey('Resultado_Nutricion_Animal')
    ensayo = models.ForeignKey('Ensayo')
    codigo = models.CharField(max_length=4)
    descripcion = models.CharField(max_length=125)
    metodo = models.CharField(max_length=50)
    resultado = models.CharField(max_length=10)


class Resultado_suelos_agricolas(models.Model):
    orden = models.ForeignKey('Orden')
    ensayo = models.ForeignKey('Ensayo')
    verificacion = models.CharField(max_length=20, unique=True)
    # codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado
    fecha = models.DateField(auto_now=True)  # fecha de la creacion del resultado

    propietario = models.CharField(max_length=70)
    fecha_recepcion = models.DateField(auto_now=True)  # fecha recibido de la muestra
    departamento = models.CharField(max_length=50)
    municipio = models.CharField(max_length=50)
    vereda = models.CharField(max_length=50)
    finca = models.CharField(max_length=50)
    lote = models.CharField(max_length=50)
    cultivo = models.CharField(max_length=50)
    estado = models.CharField(max_length=1)
    # 1-> normal, 2-> resultado de estudiante, 3-> normal anulado, 4-> estudiante anulado

    #resultados de los analisis quimico
    #cada resultado se divide en 3 partes separados por comas, (resultados, unidad, metodo)
    ph = models.CharField(max_length=120, null=True)
    ce = models.CharField(max_length=120, null=True)
    co = models.CharField(max_length=120, null=True) #mo/1.724
    mo = models.CharField(max_length=120, null=True)
    n = models.CharField(max_length=120, null=True)
    p = models.CharField(max_length=120, null=True)
    k = models.CharField(max_length=120, null=True)
    ca = models.CharField(max_length=120, null=True)
    mg = models.CharField(max_length=120, null=True)
    al = models.CharField(max_length=120, null=True)
    na = models.CharField(max_length=120, null=True)
    cic = models.CharField(max_length=120, null=True)
    cice = models.CharField(max_length=120, null=True)# mirar formula
    #acidez = models.CharField(max_length=120, null=True)
    s = models.CharField(max_length=120, null=True)
    fe = models.CharField(max_length=120, null=True)
    mn = models.CharField(max_length=120, null=True)
    cu = models.CharField(max_length=120, null=True)
    zn = models.CharField(max_length=120, null=True)
    b = models.CharField(max_length=120, null=True)
    #20 con el que esta comentado

    #relaciones cationicas

    ca_mg = models.CharField(max_length=120, null=True)
    ca_k = models.CharField(max_length=120, null=True)
    mg_k = models.CharField(max_length=120, null=True)
    #ca_b = models.CharField(max_length=120, null=True)#no
    #fe_mn = models.CharField(max_length=120, null=True)#no
    #p_zn = models.CharField(max_length=120, null=True)#no
    ca_mg_k = models.CharField(max_length=120, null=True)

    #4
    sat_na = models.CharField(max_length=120, null=True)
    sat_k = models.CharField(max_length=120, null=True)
    sat_ca = models.CharField(max_length=120, null=True)
    sat_mg = models.CharField(max_length=120, null=True)
    sat_al = models.CharField(max_length=120, null=True)
    #5

    #analisis fisico

    textura_1 = models.CharField(max_length=120, null=True)
    t2_arena = models.CharField(max_length=120, null=True)
    t2_arcilla = models.CharField(max_length=120, null=True)
    t2_limo = models.CharField(max_length=120, null=True)
    t2_clase = models.CharField(max_length=120, null=True)#nuevo
    #5

    jefe = models.CharField(max_length=10)
    observacion = models.TextField(null=True)
    encargado = models.CharField(max_length=10)


class Resultado_Traccion_Acero(models.Model):
    orden = models.ForeignKey('Orden_Ensayo')
    ensayo = models.ForeignKey('Ensayo')
    verificacion = models.CharField(max_length=20, unique=True)
    # codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado
    fecha = models.DateField(auto_now=True)  # fecha de la creacion del resultado

    jefe = models.CharField(max_length=10)
    encargado = models.CharField(max_length=10)
    estado = models.IntegerField()
    # 1-> normal, 2-> resultado de estudiante, 3-> normal anulado, 4-> estudiante anulado
    descripcion = models.TextField()

    #datos del ensayo
    norma_icontec = models.CharField(max_length=20)
    title = models.CharField(max_length=40)
    n_muestra = models.IntegerField()

    a1 = models.CharField(max_length=40)
    a2 = models.CharField(max_length=40)
    a3 = models.CharField(max_length=40)
    a4 = models.CharField(max_length=40)
    a5 = models.CharField(max_length=40)
    a6 = models.CharField(max_length=40)
    a7 = models.CharField(max_length=40)
    a8 = models.CharField(max_length=40)
    a9 = models.CharField(max_length=40)
    a10 = models.CharField(max_length=40)
    a11 = models.CharField(max_length=40)
    a12 = models.CharField(max_length=40)
    a13 = models.CharField(max_length=40)
    a14 = models.CharField(max_length=40)
    a15 = models.CharField(max_length=40)
    a16 = models.CharField(max_length=40)
    a17 = models.CharField(max_length=40)
    a18 = models.CharField(max_length=40)


class Punto_Grafica_Traccion_Acero(models.Model):
    resultado = models.ForeignKey('Resultado_Traccion_Acero')
    deformacion = models.IntegerField()#deformacion en mm
    carga_kn = models.IntegerField()#Carga kilo newton
    esfuerzo_psi = models.IntegerField()#Esfuerso en psi
    error = models.IntegerField()#porcentaje de Error
    esfuerzo_mpa = models.IntegerField()#esfuerzo mega pascales


'''

class Resultado_Carbones(models.Model):
    orden = models.ForeignKey('Orden_Ensayo')
    verificacion = models.CharField(max_length=20, unique=True)
    # codigo verificacion 2--> laboratorio, 6--> orden, 12 --> para resultado
    jefe = models.CharField(max_length=10)
    encargado = models.CharField(max_length=10)


    mina = models.CharField(max_length=30)
    muestra = models.CharField(max_length=20)
    localizacion = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=40)
    colector = models.CharField(max_length=40)

class Departamento(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=70)


class Carrera(models.Model):
    codigo = models.CharField(max_length=3, primary_key=True)
    nombre = models.CharField(max_length=70)
    departamento = models.ForeignKey('Departamento')


class Profesor(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=50)
    categoria = models.CharField(max_length=2)
    email = models.CharField(max_length=70)
    departamento = models.ForeignKey('Departamento')


class Carga(models.Model):
    carrera = models.ForeignKey('Carrera')
    profesor = models.ForeignKey('Profesor')
    codigo = models.CharField(max_length=5)#codigo de la materia
    nombre = models.CharField(max_length=45)#nombre de la materia
    grupo = models.CharField(max_length=1)
    matriculados = models.IntegerField()


class Sala(models.Model):
    nombre = models.CharField(max_length=15)
    estado = models.IntegerField()


class Restriccion(models.Model):
    sala = models.ForeignKey('Sala')
    turno = models.IntegerField(null=True)
    dia = models.DateField()
    #estado = grupo = models.CharField(max_length=1)
    #si es 1 bloque el dia y si es 0 bloquea un turno


class Prestamo(models.Model):
    turno = models.IntegerField()
    dia = models.DateField()
    fecha_prestamo = models.DateTimeField(auto_now=True)
    sala = models.ForeignKey('Sala')
    carga = models.ForeignKey('Carga')
    usuario = models.ForeignKey('User')

    def __unicode__(self):
        return self.Prestamo


'''
