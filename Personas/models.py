
from datetime import timezone
from functools import cached_property
#from time import timezone
from django.db import models
from ckeditor.fields import RichTextField

class Contacto(models.Model):
    nombre = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    mensaje = models.TextField(max_length=150)

class Titular(models.Model): #Empresa
    nombre = models.CharField(max_length=25)
    email = models.EmailField(max_length=25,unique=True)
    domicilio = models.CharField(max_length=25)
    provincia = models.CharField(max_length=20)
    pais = models.CharField(max_length=20)
    sexo= models.CharField(max_length=10, default='F', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name='Titular'
        verbose_name_plural= 'Titulares'
        ordering=''

class EstadoCivil(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name='Estado Civil'
        verbose_name_plural= 'Estados Civiles'
        ordering=''

class Persona(models.Model):
    SEXO= [('M','Masculino'),
           ('F','Femenino'),
           ('X', 'Otro')
           ]
    
    dni= models.CharField(max_length=8, verbose_name='D.N.I.', help_text='Ingrese sin puntos', blank=True, null=True) #no requerido
    nombre= models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    fecha_nac = models.DateField(max_length=6, verbose_name='Fecha de nacimiento',default='10/10/10',help_text='dia/mes/año')
    created = models.DateTimeField(auto_now_add=True) #cuando fue creado
    update = models.DateTimeField(auto_now_add=True)  #cuando fue actualizado
    sexo= models.CharField(max_length=10, choices=SEXO, default='F', null=True, blank=True)
    estado_civil= models.ForeignKey(EstadoCivil, on_delete=models.PROTECT)
    vive = models.BooleanField(default=True)
    email = models.EmailField(max_length=250,unique=True,default='nombre@hotmail.com',null=False,blank=False) #requerido
    legajo = RichTextField(default='Legajo de Persona')
    foto = models.ImageField(
        upload_to='imagenes/',  # Ruta donde se guardarán las imágenes
        verbose_name='Foto 4x4',  # Nombre descriptivo para la interfaz de administración
        default='imagenes/avatar.png'
    )


    def __str__(self):
        return f'{self.apellido},{self.nombre}, fecha Nac{self.fecha_nac}'
    
    @cached_property
    def edad(self):
        edad=0
        if self.fecha_nac:
            dias_anual=365.2425
            edad=int((timezone.now().date()-self.fecha_nac).days / dias_anual)
        return edad

    class Meta:
        verbose_name='Persona'
        verbose_name_plural= 'Personas'
        ordering=('apellido','nombre')


# Create your models here.
