from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    path ( '', views.login2 , name="api_login" ),
    path ( 'register/', views.register2 , name="register"),
    path ( 'data/', views.get_all_vitals , name="get_data"),
    path ( 'generate_vitals/', views.generate_vitals , name="get_data"),
    path ( 'view_vitals/', views.view_vitals , name="view"),
    path ( 'try/', views.tryy , name="view"),
    path ( 'logout/', views.logout2, name="logout" ),
    path ( 'model', views.predict_view, name="predict" ),
    path ( 'patients', views.get_patients, name="patients_list" ),
    path ( 'doctors', views.get_doctors, name="doctors_list" ),
    path('patients_by_sex',views.get_nbr_patients_filtred_by_sex),
    path ( 'assignments/add/<int:patient_id>/', views.add_assignment, name='add_assignment' ),
    path ( 'patients_of_doctor', views.patients_of_the_doctor, name="list" ),
    path ( 'patients_without', views.get_patients_without, name="list2" ),
    path ( 'deleate_patient/<int:patient_id>', views.delete_assignment, name="deleate" ),
    path ( 'create_appointement', views.create_appointment ),
    path ( 'deleate_appointement/<int:appointment_id>', views.delete_appointment ),
    path ( 'approve_appointement/<int:appointment_id>', views.approve_appointment ),
    path ( 'get_appointements/<int:doctor_id>', views.get_appointments ),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)