import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .pdf import render_to_pdf
from .forms import FormPersona, FormContacto
from .models import Persona, Titular
from django.http import HttpResponse, FileResponse
from django.db.models import Q
from django.views.generic import View
from django.template.loader import get_template
import requests
import os
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def book_list(request):
    personas = Persona.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(personas, 10)  #  paginate_by 5
    try:
        personas = paginator.page(page)
    except PageNotAnInteger:
        personas = paginator.page(1)
    except EmptyPage:
        personas = paginator.page(paginator.num_pages)
    return render(request, "Personas/listapaginator.html", {"personas": personas})

class email_comprobante(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
        print(path)
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            
            template = get_template('reporte_personas.html')
            print(template)        
            persona = get_object_or_404(Persona,pk=id)
            empresa = Titular.objects.all()
            if persona.email:
                persona = Persona.objects.filter(persona=persona).order_by()
                print(persona)
                context = {
                    'titular': empresa,
                    'fecha_actual': fecha_actual,
                    'personas': persona,
                    'logo': '{}{}'.format(settings.MEDIA_URL, 'logoISSM.jpg')
                }
                
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)
            
                if pisa_status.err:
                    print('error de pisa status')
                    return HttpResponse('Error al generar el PDF', status=500)
            
                # Enviamos el correo electrónico con el PDF adjunto
                mensaje_email="     Cuerpo del Mensaje, adjunto archivo pdf detallando su comprobante \n Cordiales Saludos"
                if persona.sexo == 'Femenino':
                    membresia= "Estimada Clienta "+persona.nombre+", \n \n"
                else:
                    membresia= "Estimado Cliente "+persona.nombre+", \n \n"
                Asunto_del_correo= 'Informe listado'
                pie_del_correo = '\n\n\nEste mail es enviado automáticamente. Por favor, no lo respondas\nEstás recibiendo este mensaje porque has estado en contacto con el ISSM CATAMARCA'
                Cuerpo_del_correo = membresia + mensaje_email + pie_del_correo      
                email = EmailMessage(Asunto_del_correo, Cuerpo_del_correo, settings.EMAIL_HOST_USER, [persona.email])
                print(persona.email)
                email.attach('Comprobante_pdf.pdf', response.getvalue(), 'application/pdf')                
                email.send()               
                #return HttpResponse('Correo enviado con éxito.')
                messages.success(request, 'Correo enviado con éxito.')    
            else:
                messages.error(request, 'Atención: El Titular '+persona.nombre +' No tiene Registrado un EMAIL')                
        except Exception as e:
            # Manejar errores
            messages.error(request, 'Atención: Verifique conexion a Internet')                            
        return redirect('listado')

class email_comprobante2(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT
        if uri.startswith(mUrl):

            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
        return path

    def get(self, request, id, **kwargs):
        try:
            fecha_actual = datetime.datetime.now()
            usuario = request.user
            template = get_template('reporte_personas.html')
            persona = Persona.objects.get(pk=id)
            listado = Persona.objects.all()
            titular = Titular.objects.all()
            if persona.email:
                
                
                context = {
                    'titular': titular,
                    'fecha_actual': fecha_actual,
                    'persona': persona,
                    'reporte': listado,
                    'logo': '{}{}'.format(settings.MEDIA_URL, 'logoISSM.jpg')
                }
                
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                print('Encontro Persona')
                pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)



                if pisa_status.err:
                    print('error pisa')
                    return HttpResponse('Error al generar el PDF', status=500)

                # Enviamos el correo electrónico con el PDF adjunto
                #mensaje_email=" Estimado/a," +{{persona.nombre}}+  " adjunto archivo pdf detallando un listado de nuestros clientes \n Cordiales Saludos"
                mensaje_email = f"Estimado/a, {persona.nombre}, adjunto archivo pdf detallando un listado de nuestros clientes.\nCordiales Saludos"
                print(mensaje_email)
                
                Asunto_del_correo= 'Listado de clientes'
                pie_del_correo = '\n\n\nEste mail es enviado automáticamente. Por favor, no lo respondas\nEstás recibiendo este mensaje porque has estado en contacto con la Empresa de sistemas'
                Cuerpo_del_correo = mensaje_email + pie_del_correo
                email = EmailMessage(Asunto_del_correo, Cuerpo_del_correo, settings.EMAIL_HOST_USER, [persona.email])
                email.attach('listado.pdf', response.getvalue(),'application/pdf')
                email.send()
                print('Enviado')
                #return HttpResponse('Correo enviado con éxito.')
                messages.success(request, 'Correo enviado con éxito.')
            else:
                messages.error(request, 'Atención: El Titular '+persona.apellido +';No tiene Registrado un EMAIL')
        except Exception as e:
         # Manejar errores
             messages.error(request, 'Atención: Verifique conexion a Internet')

        return redirect('listado')


def index(request):
    return render(request,'personas/index.html')

def listado(request):
    personas= Persona.objects.all()
    return render(request,'personas/listado.html',{'personas':personas})

def editar(request,id):
    persona = get_object_or_404(Persona,pk=id)
    if request.method == 'POST':
        formpersona = FormPersona(request.POST,instance=persona)
        if formpersona.is_valid():
            formpersona.save()
            return redirect('listado')
        else:
            messages.error(request, 'Hubo un error en la operación.')
    else:
        formpersona = FormPersona(instance=persona)
        return render(request,'personas/editar.html',{'formpersona':formpersona})

def contacto(request):
    form_contacto= FormContacto()
    if request.method == 'POST':
        form_contacto = FormContacto(request.POST)
        if form_contacto.is_valid():
            nombre = request.POST['nombre']
            email = request.POST['email']
            mensaje = request.POST['mensaje']
            # Envía el correo electrónico
            send_mail(
                'Contacto - Empresa',
                f'Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}',
                'tu_email@dominio.com',# Dirección de correo electrónico del remitente
                ['correo_destino@dominio.com'], # Lista de destinatarios o solo 1
                fail_silently=False,
            )
            messages.success(request, 'Correo enviado con éxito')
        else:
            messages.error('Error. Por favor verifica que los datos esten correctos')
        # Lógica adicional, como enviar una respuesta o redirigir a una página de agradecimiento
    return render(request, 'personas/contacto.html', {'form_contacto':form_contacto})


def nueva(request):
    if request.method == 'POST':
    
        formpersona=FormPersona(request.POST, request.FILES)
        if formpersona.is_valid():
            formpersona.save()
            return redirect('listado')
        else:
            messages.error(request, 'Hubo un error en la operación.')
            
    else:
        formpersona=FormPersona()
    return render(request,'personas/nuevo.html',{'formpersona':formpersona})

def persona_listado(request):
    busqueda = request.POST.get('buscar')
    personas= Persona.objects.all().order_by('apellido','nombre')
    cantidad = len(personas)
    encontrados = cantidad
    if busqueda:
        personas= Persona.objects.filter(
            Q(dni_icontains=busqueda) |
            Q(apellido_icontains=busqueda)|
            Q(nombre_icontains=busqueda) |
            Q(email_icontains=busqueda)
            ).distinct().order_by('apellido','nombre')
        encontrados=len(personas)
    return render(request,'persona/persona_lista.html',
                  {"personas":personas,
                   "cantidad": cantidad,
                   "encontrados": encontrados})

def eliminar(request, id):
    borrar_persona = get_object_or_404(Persona, pk=id)
    borrar_persona.delete()
    return redirect('listado')

class generar_lista(View):
    def link_callback(self,uri,rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
        
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' %(sUrl, mUrl)
            )
        return path

    def get(self, request, *args,**kwrags):
        template = get_template('reporte_personas.html')
        context= {
            'reporte': Persona.objects.all(),
            'logo': '{}{}'.format(settings.MEDIA_URL, 'logoISSM.jpg')
            }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="report.pdf"' #para que el archivo se descargue automaticante
        pisaStatus = pisa.CreatePDF(
            html, dest=response,
            link_callback=self.link_callback
            )
        if pisaStatus.err:
            return HttpResponse ('Ocurrió un error <pre>' + html + '</pre>')   
        return response
    
@login_required #medida de seguridad p que un usuario no logeado no pueda ingresar sin logearse
def change_password(request):
    return PasswordChangeView.as_view(
         template_name= 'registration/change_password.html',
        success_url= reverse_lazy('index') 
    ) (request)



class listado_email(View):
    def link_callback(self,uri,rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
        
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' %(sUrl, mUrl)
            )
        return path

    def get(self, request, *args,**kwrags):
        template = get_template('reporte_personas.html')
        context= {
            'reporte': Persona.objects.all(),
            'logo': '{}{}'.format(settings.MEDIA_URL, 'logoISSM.jpg')
            }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="report.pdf"' #para que el archivo se descargue automaticante
        pisaStatus = pisa.CreatePDF(
            html, dest=response,
            link_callback=self.link_callback
            )
        if pisaStatus.err:
            return HttpResponse ('Ocurrió un error <pre>' + html + '</pre>')
        titular= 'plmarello@gmail.com'
        persona = get_object_or_404(Persona, pk=1)
        print(persona.email)
        email = EmailMessage('asunto', 'Cuerpo_del_correo', settings.EMAIL_HOST_USER, [persona.email])
        email.attach('Comprobante_pdf.pdf', response.getvalue(), 'application/pdf')                
        email.send()           
        #return HttpResponse('Correo enviado con éxito.')
        messages.success(request, 'Correo enviado con éxito.')   
        return response

    #def get(self,request,*args,**kwrags):
       #template_name='reporte_personas.html'
        #listapersonas=Persona.objects.all()
        #data = {
            #'count':listapersonas.count(),
            #'listapersonas':listapersonas
        #}
        #pdf=render_to_pdf(template_name,data)
        #return HttpResponse(pdf,content_type='aapplication/pdf')
# Create your views here.
