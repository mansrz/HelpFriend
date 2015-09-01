# -*- encoding: utf-8 -*-
import random
import string

from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from datetime import *
from ofertas_demandas.models import *
from ofertas_demandas.serializers import *

from usuarios.models import *
from django.db.models import Avg
from usuarios.serializers import UsuarioSerializador

"""
Autor: Leonel Ramirez
Nombre de funcion: InicioOferta
Parametros: request
Salida: 
Descripcion: para llamar la pagina oferta inicio
"""

@login_required
def InicioOferta(request):
	args = {}
	args['usuario']=request.user
	args['es_admin']=request.session['es_admin']
	return render_to_response('oferta_inicio.html',args)


@login_required
def InicioDemanda(request):
	args = {}
	args['usuario']=request.user
	args['es_admin']=request.session['es_admin']
	return HttpResponseRedirect('/NotFound/')


"""
Autor: FaustoMora
Nombre de funcion: CrearOfertaCopia
Parametros: request
Salida: HttpResponseRedirect
Descripcion: funcion para redireccion a crear_oferta_copia
"""
@login_required
def CrearOfertaCopia(request):
	if request.GET.get('select_oferta',False):
		args = {}
		args['es_admin']=request.session['es_admin']
		args['usuario']=request.user
		oferta = None
		oferta_id = request.GET['select_oferta']
		oferta = Oferta.objects.get(id_oferta=oferta_id)
		palabra_clave = PalabraClave.objects.filter(ofertas_con_esta_palabra=oferta)
		tags = []
		for t in palabra_clave:
			aux_tag ={'text':t.palabra}
			tags.append(t.palabra.encode('utf-8','ignore'))

		tiempo_disponilbe = oferta.tiempo_para_estar_disponible.split(' ',1)
		oferta_tiempo = int(tiempo_disponilbe[0])

		if tiempo_disponilbe[1] == 'Mes/es':
			oferta_duracion = 0
		else:
			oferta_duracion = 1

		tags_json= json.dumps(tags)
		args['oferta_tiempo']=oferta_tiempo
		args['oferta_duracion']=oferta_duracion
		args['oferta']=oferta
		args['tags']=tags_json
		args.update(csrf(request))
		return render(request,'crear_oferta.html',args)
	else:
		return redirect('/CrearOferta/')

"""
Autor: FaustoMora
Nombre de funcion: CrearOferta
Parametros: request
Salida: HttpResponseRedirect
Descripcion: funcion para redireccion a crear_oferta
"""

@login_required
def CrearOferta(request):
	args = {}
	args['usuario']=request.user
	args['es_admin']=request.session['es_admin']
	args['oferta'] = None
	args.update(csrf(request))
	return render(request,'crear_oferta.html',args)


"""
Autor: FaustoMora
Nombre de funcion: CargarImagenOferta
Parametros: request
Salida: HttpResponse status
Descripcion: funcion para upload de imagnes en crear oferta
"""

@login_required
def CargarImagenOferta(request):
	try:
		print 'cargar oferta imagen'
		imagen = ImagenOferta()
		descripcion = request.POST.get('descripcion',None)
		descripcion = json.loads(descripcion)
		if descripcion:
			aux = request.POST['flowIdentifier']

			for x in descripcion:
				if x['value'] == aux:
					imagen.descripcion=x['descripcion']
		else:
			imagen.descripcion=" "

		id = request.POST['id_oferta']
		imagen.fk_oferta = Oferta.objects.get(id_oferta=id)
		img = request.FILES['file']
		imagen.imagen = img
		imagen.save()
		response = JsonResponse({'save_estado':True})
		return HttpResponse(response.content)
	except:
		response = JsonResponse({'save_estado':False})
		return HttpResponse(response.content)

"""
Autor: FaustoMora
Nombre de funcion: crearDemanda
Parametros: request
Salida: HttpResponseRedirect
Descripcion: funcion para redirect a crear demanda
"""
@login_required
def CrearDemanda(request):
	args = {}
	args['usuario']=request.user
	args['es_admin']=request.session['es_admin']
	args['demanda'] = None
	args.update(csrf(request))
	return render(request,'crear_demanda.html',args)


"""
Autor: FaustoMora
Nombre de funcion: CrearDemandaCopia
Parametros: request
Salida: HttpResponseRedirect
Descripcion: funcion para redireccion a crear_demanda_copia
"""
@login_required
def CrearDemandaCopia(request):
	if request.GET.get('select_demanda',False):
		args = {}
		args['es_admin']=request.session['es_admin']
		args['usuario']=request.user
		demanda_id = request.GET['select_demanda']
		demanda = Demanda.objects.get(id_demanda=demanda_id)
		palabra_clave = PalabraClave.objects.filter(demandas_con_esta_palabra=demanda)
		tags = []
		for t in palabra_clave:
			aux_tag ={'text':t.palabra}
			tags.append(t.palabra.encode('utf-8','ignore'))

		tiempo_disponilbe = demanda.tiempo_para_estar_disponible.split(' ',1)
		demanda_tiempo = int(tiempo_disponilbe[0])

		if tiempo_disponilbe[1] == 'Mes/es':
			demanda_duracion = 0
		else:
			demanda_duracion = 1

		tags_json= json.dumps(tags)
		args['demanda_tiempo']=demanda_tiempo
		args['demanda_duracion']=demanda_duracion
		args['demanda']=demanda
		args['tags']=tags_json
		args.update(csrf(request))
		return render(request,'crear_demanda.html',args)
	else:
		return redirect('/CrearDemanda/')

"""
Autor: FaustoMora
Nombre de funcion: CargarImagenDemanda
Parametros: request
Salida: HttpResponse status
Descripcion: funcion para upload de imagnes en crear demanda
"""

@login_required
def CargarImagenDemanda(request):
	try:
		imagen = ImagenDemanda()
		descripcion = request.POST.get('descripcion',None)
		descripcion = json.loads(descripcion)
		if descripcion:
			aux = request.POST['flowIdentifier']

			for x in descripcion:
				if x['value'] == aux:
					imagen.descripcion=x['descripcion']
		else:
			imagen.descripcion=" "

		id = request.POST['id_demanda']
		imagen.fk_demanda = Demanda.objects.get(id_demanda=id)
		img = request.FILES['file']
		imagen.imagen = img
		imagen.save()
		response = JsonResponse({'save_estado':True})
		return HttpResponse(response.content)
	except:
		response = JsonResponse({'save_estado':False})
		return HttpResponse(response.content)

"""
Autor: Rolando Sornoza, Roberto Yoncon, David Vinces
Nombre de funcion: verCualquierOferta
Parametros: request
Salida: http
Descripcion: funcion para ver una oferta publicada
"""
@login_required
def verCualquierOferta(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']

	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario
		try:
			oferta = Oferta.objects.get(id_oferta = id_oferta)
			args['oferta'] = oferta
		except:
			args['mensaje_error'] = "La oferta no se encuentra en la red, lo sentimos."
			return render_to_response('problema_oferta.html',args)

		try:
			membresiaOferta = MiembroEquipo.objects.get(fk_participante = usuario.id_perfil, fk_oferta_en_que_participa = oferta.id_oferta)
			estadoMembresia = membresiaOferta.estado_membresia
			args['estadoMembresia'] = estadoMembresia
		except Exception as e:
			args['estadoMembresia'] = 2


		if oferta.publicada == 0 :
			args.update(csrf(request))
			args['mensaje_error'] = "La oferta "+oferta.nombre+", no esta actualmente publicada."
			return render_to_response('problema_oferta.html',args)

		else:
			participantes = MiembroEquipo.objects.filter(fk_oferta_en_que_participa=id_oferta,estado_membresia=1)
			propietario = MiembroEquipo.objects.get(fk_oferta_en_que_participa=id_oferta,estado_membresia=1,es_propietario=1).fk_participante
			comentariosOferta = ComentarioCalificacion.objects.filter(fk_oferta_id=id_oferta)
			args['miComentario'] = ComentarioCalificacion.objects.filter(fk_oferta_id=id_oferta, fk_usuario_id=usuario).count
			calificacionOferta = oferta.calificacion_total
			try:
				palabras_claves = oferta.palabras_clave.all()
			except Exception as e:
				palabras_claves =  ["Null", "Null", "Null", "Null"]


		args.update(csrf(request))
		args['participantes'] = participantes
		args['palabras_claves'] = palabras_claves
		args['comentariosOferta'] = comentariosOferta
		args['calificacionOferta'] = str(calificacionOferta)
		args['propietario'] = propietario
		return render_to_response('oferta_ver_otra.html',args)

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')


"""
Autor: Pedro Iniguez
Nombre de funcion: administrarOferta
Parametros: request
Salida:
Descripcion: funcion para administrar mi oferta publicada.
"""

@login_required
def administrar_Oferta(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']
	print 'mi id antes'+id_oferta
	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario
	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

	oferta = Oferta.objects.get(id_oferta = id_oferta)
	print oferta.id_oferta


	if (oferta.publicada == 0):
		print 'No publicada'
		#return HttpResponseRedirect('/NotFound/')
	membresiaOferta = MiembroEquipo.objects.all().filter(fk_participante = usuario.id_perfil, fk_oferta_en_que_participa = id_oferta, es_propietario = 1).first()

	if membresiaOferta is None:
		return HttpResponseRedirect('/NotFound/')


	solicitudes=MiembroEquipo.objects.all().filter(fk_oferta_en_que_participa = id_oferta, estado_membresia=0)

	participantes = MiembroEquipo.objects.all().filter(fk_oferta_en_que_participa=oferta.id_oferta,estado_membresia=1,activo =1)

	equipoDueno = MiembroEquipo.objects.all().filter(es_propietario=1, fk_oferta_en_que_participa=oferta.id_oferta).first()
	try:
		palabras_claves = oferta.palabras_clave.all()
	except Exception as e:
		palabras_claves =  ["Null", "Null", "Null", "Null"]

	args['palabras_claves'] = palabras_claves
	args['comentariosPendientes'] = ComentarioCalificacion.objects.filter(fk_oferta = oferta.id_oferta, estado_comentario=0)
	args['comentariosAceptados']=ComentarioCalificacion.objects.filter(fk_oferta = oferta.id_oferta, estado_comentario=1).count
	args.update(csrf(request))
	args['dueno'] = equipoDueno.fk_participante.first_name + ' ' + equipoDueno.fk_participante.last_name
	args['institucion_nombre'] = request.session['institucion_nombre']
	args['oferta'] = oferta
	calificacionOferta = oferta.calificacion_total
	args['calificacionOferta'] = str(calificacionOferta)
	args['participantes'] = participantes
	args['solicitudes']=solicitudes
	return render_to_response('administrar_oferta.html',args)

"""
Autor: Pedro Iniguez
Nombre de funcion: administarBorrador
Parametros: request
Salida:
Descripcion: funcion para administrar mi oferta publicada.
"""

@login_required
def administrar_Borrador(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']

	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

	try:
		oferta = Oferta.objects.get(id_oferta = id_oferta)
	except:
		return HttpResponseRedirect('/NotFound/')
	if (oferta.publicada == 1):
		return HttpResponseRedirect('/NotFound/')
	membresiaOferta = MiembroEquipo.objects.all().filter(fk_participante = usuario.id_perfil, fk_oferta_en_que_participa = id_oferta, es_propietario = 1).first()

	if membresiaOferta is None:
		return HttpResponseRedirect('/NotFound/')

	equipoDueno = MiembroEquipo.objects.all().filter(es_propietario=1, fk_oferta_en_que_participa=oferta.id_oferta).first()

	galeria = ImagenOferta.objects.all().filter(fk_oferta = oferta.id_oferta)

	args.update(csrf(request))
	args['dueno'] = equipoDueno.fk_participante.first_name + ' ' + equipoDueno.fk_participante.last_name
	args['institucion_nombre'] = request.session['institucion_nombre']
	args['oferta'] = oferta
	args['galeria'] = galeria
	args['imagen_principal'] = galeria.first()
	return render_to_response('administrar_borrador.html',args)

"""
Autor: Roberto Yoncon
Nombre de funcion: editar_borrador
Parametros: request, id de una oferta
Salida: 
Descripcion: funcion para editar un borrador
"""
@login_required
def editar_borrador(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']
	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

	try:
		oferta = Oferta.objects.get(id_oferta = id_oferta)
	except:
		return HttpResponseRedirect('/NotFound/')
	if (oferta.publicada == 1):
		return HttpResponseRedirect('/NotFound/')
	membresiaOferta = MiembroEquipo.objects.all().filter(fk_participante = usuario.id_perfil, fk_oferta_en_que_participa = id_oferta, es_propietario = 1).first()

	if membresiaOferta is None:
		return HttpResponseRedirect('/NotFound/')

	if request.method == 'POST':
		#seccion de informacion
		nombre = request.POST['nombre_oferta']
		tipo = request.POST['select_tipo_oferta']
		descripcion = request.POST['descripcion_oferta']
		dominio = request.POST['oferta_dominio']
		subdominio = request.POST['oferta_sub_dominio']
		#tags = request.POST['oferta_tags'] #Aun no usado
		#seccion de perfiles
		perfilCliente = request.POST.get('oferta_descripcion_perfil', None)
		perfilBeneficiario = request.POST.get('oferta_beneficiario_perfil', None)
		#seccion de business canvas
		canvasSocioClave = request.POST.get('canvas_socio_clave', None)
		canvasActividadesClave = request.POST.get('canvas_actividades_clave', None)
		canvasRecursos = request.POST.get('canvas_recrusos_clave', None)
		canvasPropuesta = request.POST.get('canvas_propuesta_valor', None)
		canvasRelaciones = request.POST.get('canvas_ralaciones_clientes', None)
		canvasCanales = request.POST.get('canvas_canales_distribucion', None)
		canvasSegmentos = request.POST.get('canvas_segmentos_clientes', None)
		canvasEstructura = request.POST.get('canvas_estructura_costos', None)
		canvasFuentes = request.POST.get('canvas_fuente_ingresos', None)
		#seccion de industria
		tendencias = request.POST.get('oferta_tendencias', None)
		solucionesAlternativas = request.POST.get('ofertas_alternativas_soluciones', None)
		#para Diagrama de Porter
		porterCompetidores = request.POST.get('diagramapoter_competidores', None)
		porterConsumidores = request.POST.get('diagramapoter_consumidores', None)
		porterSustitutos = request.POST.get('diagramapoter_sustitutos', None)
		porterProveedores = request.POST.get('diagramapoter_proveedores', None)
		porterNuevos = request.POST.get('diagramapoter_nuevos_entrantes', None)
		#seccion de estado/Logros
		tiempoDisponible = request.POST.get('oferta_tiempo_disponibilidad', None)
		tiempoUnidad = request.POST.get('select_oferta_tiempo', None)
		propiedadIntelectual = request.POST.get('oferta_propiedad_intelectual', None)
		evidenciaTraccion = request.POST.get('oferta_evidencia_traccion', None)

		ofertaEditada = oferta
		ofertaEditada.nombre = nombre
		ofertaEditada.tipo = tipo
		ofertaEditada.descripcion = descripcion

		ofertaEditada.dominio = dominio
		ofertaEditada.subdominio = subdominio

		ofertaEditada.perfil_cliente = perfilCliente
		ofertaEditada.perfil_beneficiario = perfilBeneficiario

		if ofertaEditada.fk_diagrama_canvas is None:
			ofertaEditada.fk_diagrama_canvas = None
		else:
			ofertaEditada.fk_diagrama_canvas.asociaciones_clave = canvasSocioClave
			ofertaEditada.fk_diagrama_canvas.actividades_clave = canvasActividadesClave
			ofertaEditada.fk_diagrama_canvas.recursos_clave = canvasRecursos
			ofertaEditada.fk_diagrama_canvas.propuesta_valor = canvasPropuesta
			ofertaEditada.fk_diagrama_canvas.relacion_clientes = canvasRelaciones
			ofertaEditada.fk_diagrama_canvas.canales_distribucion = canvasCanales
			ofertaEditada.fk_diagrama_canvas.segmento_mercado = canvasSegmentos
			ofertaEditada.fk_diagrama_canvas.estructura_costos = canvasEstructura
			ofertaEditada.fk_diagrama_canvas.fuente_ingresos = canvasFuentes
			ofertaEditada.fk_diagrama_canvas.save()
			
		#seccion de industria
		ofertaEditada.cuadro_tendencias_relevantes = tendencias
		ofertaEditada.descripcion_soluciones_existentes = solucionesAlternativas
		#para Diagrama de Porter
		if ofertaEditada.fk_diagrama_competidores is None:
			ofertaEditada.fk_diagrama_competidores = None
		else:
			ofertaEditada.fk_diagrama_competidores.competidores = porterCompetidores
			ofertaEditada.fk_diagrama_competidores.consumidores = porterConsumidores
			ofertaEditada.fk_diagrama_competidores.sustitutos = porterSustitutos
			ofertaEditada.fk_diagrama_competidores.proveedores = porterProveedores
			ofertaEditada.fk_diagrama_competidores.nuevosMiembros = porterNuevos
			ofertaEditada.fk_diagrama_competidores.save()
			
		#seccion de estado/Logros
		#ofertaEditada = tiempoDisponible
		#ofertaEditada = tiempoUnidad
		ofertaEditada.estado_propieada_intelectual = propiedadIntelectual
		ofertaEditada.evidencia_traccion = evidenciaTraccion

		ofertaEditada.save()

		args.update(csrf(request))
		args['institucion_nombre'] = request.session['institucion_nombre']
		args['oferta'] = ofertaEditada
		return render_to_response('administrar_borrador.html',args)

	else:
		args.update(csrf(request))
		args['institucion_nombre'] = request.session['institucion_nombre']
		args['oferta'] = oferta
		return render_to_response('editar_borrador.html',args)



"""
Autor: David Vinces
Nombre de la funcion: listaComentariosAceptados
Entrada:
Salida: Muestra la lista de Comentarios Aceptados de una oferta
Descripción:Esta función permite mostrar el listado de comentarios aceptados de una oferta
"""
@login_required
def listaComentariosAceptados(request):
	print 'listaComentariosAceptados :: ajax con id '+ request.GET['oferta']
	if request.is_ajax():
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.GET['oferta'])
			listaComentarios= ComentarioCalificacion.objects.filter(fk_oferta = oferta.id_oferta)
			args['listaComentarios'] = listaComentarios
			args['oferta']=oferta
			args.update(csrf(request))
			return render(request,'comentario_oferta.html',args)
		except Oferta.DoesNotExist:
			print '>> Oferta no existe'
		except ComentarioCalificacion.DoesNotExist:
			print '>> Comentario no existe'
		except:
			print '>> Excepcion no controlada'
	else:
		return redirect('/NotFound')


"""
Autor: Ray Montiel
Nombre de la funcion: equipoOferta
Entrada:
Salida: Muestra el equipo de una oferta
Descripción:Esta función permite mostrar el equipo de una oferta
"""
@login_required
def equipoOferta(request):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']
	if usuario is not None:
		args['usuario'] = usuario
	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	if request.is_ajax():
		print 'estoy en el ajax'
		try:
			oferta = Oferta.objects.get(id_oferta=request.GET['oferta'])
			listaEquipo= MiembroEquipo.objects.filter(fk_oferta_en_que_participa = oferta.id_oferta)
			args['listaEquipo'] = listaEquipo
			args['oferta']=oferta
			args.update(csrf(request))
			return render(request,'equipo_oferta.html',args)

		except Oferta.DoesNotExist:
			print 'esa oferta no existe '
			return redirect('/')
		except MiembroEquipo.DoesNotExist:
			print 'Este pana no tiene amigos :/'
			return redirect('/')
		except:
			print 'ya me jodi =('
			return redirect('/')
	else:
		return redirect('/NotFound')

@login_required
def equipoEditableOferta(request):

	if request.is_ajax():
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.GET['oferta'])
			listaEquipo= MiembroEquipo.objects.filter(fk_oferta_en_que_participa = oferta.id_oferta, estado_membresia=1)
			args['listaEquipo'] = listaEquipo
			args['oferta']=oferta
			args.update(csrf(request))
			return render(request,'equipo_editable.html',args)

		except Oferta.DoesNotExist:
			print 'esa oferta no existe '
			return redirect('/')
		except MiembroEquipo.DoesNotExist:
			print 'Este pana no tiene amigos :/'
			return redirect('/')
		except:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return redirect('/NotFound')



"""
Autor: Ray Montiel
Nombre de la funcion: AutocompletarParticipante
Entrada:
Salida: Muestra los usuarios disponibles para agregarlos a la oferta
Descripción:Esta función permite mostrar los participantes autocompletando sus nombres y usernames
"""
class AutocompletarParticipante(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self,request,*args,**kwargs):
		user = request.query_params.get('term',None)
		usuarios = User.objects.filter(username__icontains=user)[:5]
		serializador = UsuarioSerializador(usuarios,many=True)
		response = Response(serializador.data)
		return response



"""
Autor: Ray Montiel
Nombre de la funcion: solicitarMembresiaOferta
Entrada:
Salida:
Descripción:Envia una solicitud para participar en una Oferta
"""
@login_required
def solicitarMembresiaOferta(request):
	if request.method=="POST":
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.POST['oferta'])
			print request.POST['oferta']
			print request.user

			solicitudMembresia = MiembroEquipo.objects.get(fk_oferta_en_que_participa=oferta.id_oferta,fk_participante=request.user.id)

			if solicitudMembresia is not None and solicitudMembresia.estado==-1 :
				solicitudMembresia.rol_participante = "Miembro del Equipo de la Oferta"
				solicitudMembresia.estado_membresia = 0
				solicitudMembresia.fecha_aceptacion = datetime.datetime.now()
				solicitudMembresia.comentario_peticion= request.POST['comentario_peticion']
				solicitudMembresia.save()
				print 'se actualizo parece'
				response = JsonResponse({'save_estado':True})
				return HttpResponse(response.content)

		except Oferta.DoesNotExist:
			args['mensaje_error'] = "La oferta no se encuentra en la red, lo sentimos."
			return render_to_response('problema_oferta.html',args)
		except MiembroEquipo.DoesNotExist:
				solicitudMembresia = MiembroEquipo()
				solicitudMembresia.es_propietario = False
				solicitudMembresia.rol_participante = "Miembro del Equipo de la Oferta"
				solicitudMembresia.estado_membresia = 0
				solicitudMembresia.fk_participante = request.user.perfil
				solicitudMembresia.fk_oferta_en_que_participa = oferta
				solicitudMembresia.fecha_aceptacion = datetime.datetime.now()
				solicitudMembresia.comentario_peticion= request.POST['comentario_peticion']
				solicitudMembresia.save()
				print 'se guardo parece'
				response = JsonResponse({'save_estado':True})
				return HttpResponse(response.content)
		except:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return redirect('/')

"""
Autor: Ray Montiel
Nombre de la funcion: agregarParticipante
Entrada: nombre de usuario y rol
Salida:
Descripción:Agrega a un participante a una oferta
"""
def agregarParticipante(request):
	if request.method=="POST":
		session = request.session['id_usuario']
		usuario = Perfil.objects.get(id=session)
		args = {}
		participante = Perfil.objects.get(username = request.POST['particOferta'])
		rol = request.POST['rolNuevoIntegrante']
		ofertaAdmin = request.POST['ofertaAdmin']
		if usuario is not None:
			#Guardo en la variable de sesion a usuario.
			args['usuario'] = usuario
			print usuario.username
		else:
			args['error'] = "Error al cargar los datos"
			return HttpResponseRedirect('/NotFound/')

		try:
			oferta = Oferta.objects.get(id_oferta=ofertaAdmin)
			membresia = MiembroEquipo.objects.get(fk_oferta_en_que_participa=oferta.id_oferta,fk_participante = participante)

			if membresia is not None:
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

		except Oferta.DoesNotExist:
			args['mensaje_error'] = "La oferta no se encuentra en la red, lo sentimos."
			return render_to_response('problema_oferta.html',args)
		except MiembroEquipo.DoesNotExist:
			print 'Membresia no existe'
			membresia = MiembroEquipo()
			membresia.es_propietario = False
			membresia.rol_participante = rol
			membresia.estado_membresia = 1
			membresia.fk_participante = participante.perfil
			membresia.fk_oferta_en_que_participa = oferta
			membresia.fecha_aceptacion = datetime.datetime.now()
			membresia.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	else:
		return HttpResponseRedirect('/Not Found')

"""
Autor: Roberto Yoncon
Nombre de funcion: publicar_borrador
Parametros: request, id de una oferta
Salida: 
Descripcion: cambia el estado de una oferta de 0 a 1, mostrandola como publicada
"""
@login_required
def publicar_borrador(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']

	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

	try:
		oferta = Oferta.objects.get(id_oferta = id_oferta)
	except:
		return HttpResponseRedirect('/NotFound/')
	if (oferta.publicada == 1):
		return HttpResponseRedirect('/NotFound/')

	oferta.fecha_publicacion = datetime.datetime.now()
	oferta.publicada = 1
	oferta.save()
	args['oferta'] = oferta
	return render_to_response('oferta_inicio.html',args)



"""
Autor: Roberto Yoncon
Nombre de funcion: eliminar_borrador
Parametros: request, id de una oferta
Salida: 
Descripcion: elimina un borrador de oferta de la base de datos
"""
@login_required
def eliminar_borrador(request, id_oferta):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']

	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

	try:
		oferta = Oferta.objects.get(id_oferta = id_oferta)
	except:
		return HttpResponseRedirect('/NotFound/')

	oferta.delete()
	return render_to_response('oferta_inicio.html',args)


"""Autor: Angel Guale

"""
def aceptar_peticion(request):
	if request.method=="POST":
		session = request.session['id_usuario']
		usuario = Perfil.objects.get(id=session)
		id_user_peticion=request.POST["id_user_peticion"]
		id_oferta=request.POST["id_oferta"]
		rol_participante=request.POST["rol"]
		args = {}
		oferta=Oferta.objects.get(id_oferta=id_oferta);
		solicitudMembresia = MiembroEquipo.objects.filter(fk_oferta_en_que_participa=id_oferta,fk_participante=id_user_peticion).first()
		if solicitudMembresia is not None:
			solicitudMembresia.estado_membresia=1
			solicitudMembresia.rol_participante=rol_participante
			solicitudMembresia.save()

			return HttpResponse("ok")
		else:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return HttpResponseRedirect('NotFound');

"""Autor: Angel Guale

"""
def rechazar_peticion(request):
	if request.method=="POST":
		session = request.session['id_usuario']
		usuario = Perfil.objects.get(id=session)
		id_user_peticion=request.POST["id_user_peticion"]
		id_oferta=request.POST["id_oferta"]
		#rol_participante=request.POST["rol"]
		args = {}
		oferta=Oferta.objects.get(id_oferta=id_oferta);
		solicitudMembresia = MiembroEquipo.objects.filter(fk_oferta_en_que_participa=id_oferta,fk_participante=id_user_peticion).first()
		if solicitudMembresia is not None:
			solicitudMembresia.estado_membresia=-1
			solicitudMembresia.save()
			#response = JsonResponse({'aceptado':"True"})
			#return HttpResponse(response.content)
			return HttpResponse("ok")
		else:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return HttpResponseRedirect('NotFound');


def editar_rol_membresia(request):
	if request.method=="POST":
		session = request.session['id_usuario']
		usuario = Perfil.objects.get(id=session)
		id_user_peticion=request.POST["id_user_editable"]
		id_oferta=request.POST["id_oferta"]
		rol_participante=request.POST["rol"]
		args = {}
		oferta=Oferta.objects.get(id_oferta=id_oferta);
		solicitudMembresia = MiembroEquipo.objects.filter(fk_oferta_en_que_participa=id_oferta,fk_participante=id_user_peticion).first()
		if solicitudMembresia is not None:
			solicitudMembresia.rol_participante=rol_participante
			solicitudMembresia.save()
			#response = JsonResponse({'aceptado':"True"})
			#return HttpResponse(response.content)
			return HttpResponse("ok")
		else:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return HttpResponseRedirect('NotFound');

def editar_estado_membresia(request):
	if request.method=="POST":
		session = request.session['id_usuario']
		usuario = Perfil.objects.get(id=session)
		id_user_peticion=request.POST["id_user_editable"]
		id_oferta=request.POST["id_oferta"]
		estado_str=request.POST["estado"]
		activo=1
		if estado_str=="ACTIVO":
			activo=1
		else:
			activo=0
		args = {}
		oferta=Oferta.objects.get(id_oferta=id_oferta);
		solicitudMembresia = MiembroEquipo.objects.filter(fk_oferta_en_que_participa=id_oferta,fk_participante=id_user_peticion).first()
		if solicitudMembresia is not None:
			solicitudMembresia.activo=activo
			solicitudMembresia.save()
			#response = JsonResponse({'aceptado':"True"})
			#return HttpResponse(response.content)
			return HttpResponse("ok")
		else:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return HttpResponseRedirect('NotFound');




"""
Autor: David Vinces
Nombre de funcion: aceptarComentario
Parametros: request, id de un comentario
Salida: 
Descripcion: cambia el estado de un comentario de una oferta para que sea visible
"""
@login_required
def aceptarComentario(request, id_comentario):
	try:
		comentario = ComentarioCalificacion.objects.get(id_comentario_calificacion = id_comentario)
		comentario.estado_comentario = 1
		oferta_id = comentario.fk_oferta.id_oferta
		comentario.save()
	except:
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
	return HttpResponseRedirect('/administrarOferta/'+str(oferta_id))

"""
Autor: David Vinces
Nombre de funcion: rechazarComentario
Parametros: request, id de un comentario
Salida: 
Descripcion: cambia el estado de un comentario de una oferta para eliminarlo
"""
@login_required
def rechazarComentario(request, id_comentario):
	try:
		comentario = ComentarioCalificacion.objects.get(id_comentario_calificacion = id_comentario)
		comentario.estado_comentario=-1
		oferta_id = comentario.fk_oferta.id_oferta
		comentario.save()
	except:
		return HttpResponseRedirect('/NotFound/')
	
	return HttpResponseRedirect('/administrarOferta/'+str(oferta_id))


"""
Autor: David Vinces
Nombre de funcion: crearComentario
Parametros: request
Salida: 
Descripcion: crea un comentario de una oferta con estado_comentario=0, es decir pendiente
"""
@login_required
def enviarComentario(request):
	if request.method=="POST":
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.POST['oferta'])
			usuario = Perfil.objects.get(id=request.user.id)
			calificacion = request.POST['calificacion']
			mensaje = request.POST['comentario_peticion']
			comentario = ComentarioCalificacion()
			comentario.calificacion = calificacion
			comentario.comentario = mensaje
			comentario.estado_comentario=0
			comentario.fecha_comentario = datetime.datetime.now()
			comentario.fk_oferta = oferta
			comentario.fk_usuario = usuario
			comentario.save()
			promedio_calificacion = ComentarioCalificacion.objects.filter(fk_oferta=request.POST['oferta']).aggregate(average_cal=Avg('calificacion'))
			oferta.calificacion_total = promedio_calificacion["average_cal"]
			oferta.save()
			response = JsonResponse({})
			return HttpResponse(response.content)
		except Exception as e:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return redirect('/')



"""
Autor: Rolando Sornoza
Nombre de funcion: verCualquierDemaanda
Parametros: request
Salida: http
Descripcion: funcion para ver una demanda publicada
"""
@login_required
def verCualquierDemanda(request, id_demanda):
	session = request.session['id_usuario']
	usuario = Perfil.objects.get(id=session)
	args = {}
	args['es_admin']=request.session['es_admin']
	if usuario is not None:
		#Guardo en la variable de sesion a usuario.
		args['usuario'] = usuario
		try:
			demanda = Demanda.objects.get(id_demanda = id_demanda)
			args['demanda'] = demanda
		except:
			args['mensaje_error'] = "La Demanda no se encuentra en la red, lo sentimos."
			return render_to_response('problema_oferta.html',args)


		if demanda.publicada == 1 :
			args.update(csrf(request))
			args['mensaje_error'] = "La demanda "+demanda.nombre+", no esta actualmente publicada."
			return render_to_response('problema_oferta.html',args)

		else:
			propietario = demanda.fk_perfil
			comentariosDemanda = ComentarioDemanda.objects.filter(fk_demanda =id_demanda)
			args['numComentarios'] = ComentarioDemanda.objects.filter(fk_demanda=id_demanda, fk_usuario_id=usuario).count
			try:
				palabras_claves = demanda.palabras_clave.all()
			except Exception as e:
				palabras_claves =  ["Null", "Null", "Null", "Null"]


		args.update(csrf(request))
		args['palabras_claves'] = palabras_claves
		args['comentariosDemanda'] = comentariosDemanda
		args['propietario'] = propietario
		return render_to_response('demanda_ver_otra.html',args)

	else:
		args['error'] = "Error al cargar los datos"
		return HttpResponseRedirect('/NotFound/')

"""
Autor: Andres Sornoza
Nombre de funcion: enviarComentarioDemanda
Parametros: request
Salida:
Descripcion: crea un comentario de una demanda con estado_comentario=0, es decir pendiente
"""
@login_required
def enviarComentarioDemanda(request):"""
	if request.method=="POST":
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.POST['oferta'])
			usuario = Perfil.objects.get(id=request.user.id)
			calificacion = request.POST['calificacion']
			mensaje = request.POST['comentario_peticion']
			comentario = ComentarioCalificacion()
			comentario.calificacion = calificacion
			comentario.comentario = mensaje
			comentario.estado_comentario=0
			comentario.fecha_comentario = datetime.datetime.now()
			comentario.fk_oferta = oferta
			comentario.fk_usuario = usuario
			comentario.save()
			promedio_calificacion = ComentarioCalificacion.objects.filter(fk_oferta=request.POST['oferta']).aggregate(average_cal=Avg('calificacion'))
			oferta.calificacion_total = promedio_calificacion["average_cal"]
			oferta.save()
			response = JsonResponse({})
			return HttpResponse(response.content)
		except Exception as e:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		return redirect('/')"""

"""
Autor: Andres Sornoza
Nombre de la funcion: listaComentariosAceptadosDemandas
Entrada:
Salida: Muestra la lista de Comentarios Aceptados de una demanda
Descripción:Esta función permite mostrar el listado de comentarios aceptados de una oferta
"""
@login_required
def listaComentariosAceptadosDemandas(request):
	"""print 'listaComentariosAceptadosDemandas :: ajax con id '+ request.GET['oferta']
	if request.is_ajax():
		args={}
		try:
			oferta = Oferta.objects.get(id_oferta=request.GET['oferta'])
			listaComentarios= ComentarioCalificacion.objects.filter(fk_oferta = oferta.id_oferta)
			args['listaComentarios'] = listaComentarios
			args['oferta']=oferta
			args.update(csrf(request))
			return render(request,'comentario_oferta.html',args)
		except Oferta.DoesNotExist:
			print '>> Oferta no existe'
		except ComentarioCalificacion.DoesNotExist:
			print '>> Comentario no existe'
		except:
			print '>> Excepcion no controlada'
	else:
		return redirect('/NotFound')"""

