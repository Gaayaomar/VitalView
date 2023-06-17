import re
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
import jwt
import random
import time
from .models import Appointment
from .serializers import AppointmentSerializer
from rest_framework.settings import api_settings

from .models import User, BlacklistToken, Assignment

from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import vitalss
from django.core import serializers
import datetime
from rest_framework.request import Request
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authentication import SessionAuthentication


def password_strength(password):
    score = 0
    if len ( password ) < 8:
        return "Le mot de passe est trop court. Il doit comporter au moins 8 caractères."
    else:
        score += 1

    if re.search ( r"\d", password ):
        score += 1

    if re.search ( r"[a-z]", password ) and re.search ( r"[A-Z]", password ):
        score += 1

    if re.search ( r"\W", password ):
        score += 1

    if score == 1:
        return "Faible : Le mot de passe doit comporter des chiffres, des lettres majuscules et minuscules, et des caractères spéciaux."
    elif score == 2:
        return "Moyen : Le mot de passe doit comporter des chiffres, des lettres majuscules et minuscules, et des caractères spéciaux."
    elif score == 3:
        return "Fort : Le mot de passe est assez solide, mais peut être amélioré."
    elif score == 4:
        return "Très fort : Le mot de passe est sûr et sécurisé."


@csrf_exempt
@api_view ( ['POST'] )
def register2(request):
    email = request.data.get ( 'email' )
    password = request.data.get ( 'password' )
    username = request.data.get ( 'username' )
    cpassword = request.data.get ( 'cpassword' )
    role = request.data.get ( 'role' )
    age = request.data.get ( 'age' )
    sex = request.data.get ( 'sex' )
    # photo = request.FILES.get('photo')

    if password != cpassword:
        return Response ( {'msg': 'Les mots de passe ne correspondent pas'} )

    if password_strength ( password ) != "Très fort : Le mot de passe est sûr et sécurisé.":
        return Response ( {'msg': password_strength ( password )} )

    try:
        user = User (
            email=email,
            password=make_password ( password ),
            username=username,
            role=role,
            age=age,
            sex=sex,
            # photo=photo
        )
        user.save ()
        subject = 'Confirmation de création de compte'
        message = 'Bonjour {},\n\nVotre compte a été créé avec succès.'.format ( username )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail ( subject, message, from_email, recipient_list )
        print ( "C'est bon" )
        print("c est bon")

        return Response ( {'msg': 'Utilisateur créé avec succès.'}, status=status.HTTP_201_CREATED )

    except Exception as e:
        return Response ( {'msg': str ( e )} )


@csrf_exempt
@api_view ( ['POST'] )
def login2(request):
    email = request.data.get ( 'email' )
    password = request.data.get ( 'password' )

    try:
        user = authenticate ( request, username=email, password=password )
        print ( user )
        if user is not None:
            try:
                login ( request, user )
            except:
                print("erreur")
            print ( "User authenticated successfully" )

            valid_tokens = BlacklistToken.objects.filter (
                Q ( user=user )
            )
            if valid_tokens.exists ():
                return JsonResponse ( {'msg': "User already logged in."} )
            # Generate JWT token
            access_token = AccessToken.for_user ( user )
            access_token['user_id'] = user.pk
            access_token['email'] = user.email
            access_token['username'] = user.username
            access_token['id'] = user.id
            access_token['role'] = user.role
            token = str ( access_token )

           # BlacklistToken.objects.create (
             #   user=user,
              #  token=token,

            #)



            return JsonResponse ( {'msg': "connected successfully", 'token': token} )

        else:
            print ( "User authentication failed" )
            return JsonResponse ( {'msg': "Invalid email or password"} )
    except Exception as e:
        print ( e )
        return JsonResponse ( {'msg': "An error occurred while trying to log in"} )


@api_view ( ['GET'] )
def get_all_vitals(request):

    user = request.user.id
    vitals = vitalss.objects.filter ( user=user ).order_by ( '-updated_at' )[:10]
    vitals_list = []
    for v in vitals:
        vital_dict = {
            'a': v.a,
            'b': v.b,
            'updated_at': v.updated_at,
            'user_id': v.user_id
        }
        vitals_list.append ( vital_dict )
    return Response ( {'vitals': vitals_list} )


@api_view ( ['GET'] )
def generate_vitals(request):
    user = request.user
    if user.role == "patient":
        while True:
            a = random.randint ( 60, 100 )
            b = random.randint ( 90, 140 )

            user = user
            vitals = vitalss ( a=a, b=b, user=user )
            vitals.save ()

            time.sleep ( 5 )
    else:
        return None


def view_vitals(request):
    vitals = vitalss.objects.all ()

    return Response ( vitals )


@api_view ( ['GET'] )
def tryy(request):
    if request.user.is_authenticated:
        return Response ( {'msg': "User is  authenticated"} )
    else:
        return Response ( {'msg': "not authenticated"} )

@csrf_exempt
def logout2(request):
    if request.method == 'POST':
        BlacklistToken.objects.all ().delete ()
        logout ( request )
        response = JsonResponse ( {'message': 'Logged out successfully'} )
        return response
    else:
        return HttpResponse ( 'Method not allowed', status=405 )


import pickle


@api_view ( (["GET"]) )
def predict_view(request):
    # Load the serialized KNN model
    with open ( 'C:/Users/omar/Downloads/model.pkl', 'rb' ) as file:
        knn_model = pickle.load ( file )

    # Get input data from the request
    age = 18
    sex = 1
    heart_rate = 90
    thalach = 140
    fbs = 70
    chol = 200

    # Preprocess the input data if needed

    # Create a list with the input data
    input_data = [[thalach, fbs, chol, heart_rate, age, sex]]

    # Make predictions using the KNN model
    prediction = knn_model.predict ( input_data )

    # Return the prediction as a response
    return HttpResponse ( f"Prediction: {prediction}" )


@api_view ( (["GET"]) )
def get_patients(request):
    patients = User.objects.filter ( role='patient' )
    patients_list = [
        {
            'id': patient.id,
            'username': patient.username,
            'email': patient.email,
            'role': patient.role,

        }
        for patient in patients
    ]
    return Response ( {'patients_list': patients_list} )


@api_view ( (["GET"]) )
def get_doctors(request):
    doctors = User.objects.filter ( role='doctor' )
    doctors_list = [
        {
            'id': doctor.id,
            'username': doctor.username,
            'email': doctor.email,
            'role': doctor.role,
            'date': doctor.date_joined,
            'sex': doctor.sex,
            'age': doctor.age

        }
        for doctor in doctors
    ]
    return Response ( {'doctors_list': doctors_list} )


@csrf_exempt
@api_view ( ['GET'] )
def add_assignment(request, patient_id):
    try:
        doctor = request.user
        patient = User.objects.get ( id=patient_id, role='patient' )
        if Assignment.objects.filter ( patient=patient, doctor=doctor ).exists ():
            return Response ( {'msg': 'Patient is already assigned to this doctor.'} )

        Assignment.objects.create ( patient=patient, doctor=doctor )
        return Response ( {'msg': 'Assignment created successfully.'}, status=status.HTTP_201_CREATED )



    except:
        return Response ( {'msg': 'Error creating assignment.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR )


@api_view ( (["GET"]) )
def get_nbr_patients_filtred_by_sex(request):
    patients_h = User.objects.filter ( role='patient' ).filter ( sex='male' )
    patients_f = User.objects.filter ( role='patient' ).filter ( sex='female' )

    return Response ( {'nbr_homme': len ( patients_h ), 'nbr_femme': len ( patients_f )} )


@api_view ( (["GET"]) )
def patients_of_the_doctor(request):
    doctor = request.user
    assignments = Assignment.objects.filter ( doctor=doctor )
    patients = assignments.values ( 'patient__id', 'patient__username', 'patient__email', 'patient__role' )

    return Response ( {'patients_list': patients} )


@api_view ( ["GET"] )
def get_patients_without(request):
    doctor = request.user
    assigned_patients = Assignment.objects.filter ( doctor=doctor ).values ( 'patient_id' )
    patients = User.objects.filter ( role='patient' ).exclude ( id__in=assigned_patients )

    patients_list = [
        {
            'id': patient.id,
            'username': patient.username,
            'email': patient.email,
            'role': patient.role,
        }
        for patient in patients
    ]

    return Response ( {'patients_list': patients_list} )


@csrf_exempt
@api_view ( ['GET'] )
def delete_assignment(request, patient_id):
    try:
        doctor = request.user
        assignment = Assignment.objects.get ( patient=patient_id, doctor=doctor )
        assignment.delete ()
        return Response ( {'msg': 'Assignment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT )
    except Assignment.DoesNotExist:
        return Response ( {'msg': 'Assignment does not exist or you do not have permission to delete it.'},
                          status=status.HTTP_404_NOT_FOUND )
    except Exception as e:
        return Response ( {'msg': 'Error deleting assignment.', 'error': str ( e )},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR )




@api_view ( ['GET'] )
def get_appointments(request, doctor_id):
    appointments = Appointment.objects.filter ( doctor_id=doctor_id )
    serializer = AppointmentSerializer ( appointments, many=True )
    return Response ( serializer.data, status=status.HTTP_200_OK )


@api_view ( ['POST'] )
def create_appointment(request):
    doctor_id = request.data.get ( 'doctor' )
    start = request.data.get ( 'start' )
    end = request.data.get ( 'end' )

    # Check if the doctor has any overlapping appointments
    if Appointment.objects.filter ( doctor_id=doctor_id, start__lt=end, end__gt=start ).exists ():
        return Response ( {'message': 'Doctor has overlapping appointments'}, status=status.HTTP_400_BAD_REQUEST )

    data = {
        'patient': request.user.id,
        'doctor': doctor_id,
        'start': start,
        'end': end,
        'approved': request.data.get ( 'approved', False )
    }
    serializer = AppointmentSerializer ( data=data )
    if serializer.is_valid ():
        serializer.save ()
        return Response ( {'messgae': 'created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED )
    return Response ( serializer.errors, status=status.HTTP_400_BAD_REQUEST )


@api_view ( ['DELETE'] )
def delete_appointment(request, appointment_id):
    appointment = Appointment.objects.get ( id=appointment_id )
    appointment.delete ()
    return Response ( {'message': 'Appointment deleted successfully'}, status=status.HTTP_204_NO_CONTENT )


@api_view ( ['PUT'] )
def update_appointment(request, appointment_id):
    appointment = Appointment.objects.get ( id=appointment_id )
    data = {
        'patient': request.user.id,
        'doctor': request.doctor,
        'start': request.start,
        'end': request.end,
        'approved': request.data.get ( 'approved', False )
    }
    serializer = AppointmentSerializer ( appointment, data=data )
    if serializer.is_valid ():
        serializer.save ()
        return Response ( serializer.data, status=status.HTTP_200_OK )
    return Response ( serializer.errors, status=status.HTTP_400_BAD_REQUEST )


@api_view ( ['GET'] )
def approve_appointment(request, appointment_id):
    appointment = Appointment.objects.get ( id=appointment_id )
    appointment.approved = True
    appointment.save ()
    return Response ( {'message': 'Appointment approved'}, status=status.HTTP_200_OK )



