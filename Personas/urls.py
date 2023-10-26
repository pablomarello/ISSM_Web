"""
URL configuration for ISSM_Web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django import views
from django.conf import settings
from django.urls import path, include
from .import views
from .views import book_list


urlpatterns = [
    path('',views.index,name='index'),
    path('listado',views.listado,name='listado'),
    path('nueva/',views.nueva,name='nueva'),
    path('editar/<int:id>',views.editar,name='editar'),
    path('eliminar/<int:id>',views.eliminar,name='eliminar'),
    path('persona_listado/',views.persona_listado,name='persona_listado'), #lista+buscador
    path('reporte_personas',views.generar_lista.as_view(),name='generar_lista'),
    path('change_password/',views.change_password,name='change_password'),
    path('email_comprobante/<int:id>',views.email_comprobante2.as_view(), name="email_comprobante"),
    path('listado_email/',views.listado_email.as_view(),name='listado_email'),
    path('contacto/',views.contacto,name='contacto'),
    path('listapaginator', book_list, name='listapaginator'),
]
