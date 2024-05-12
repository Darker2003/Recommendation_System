from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import LoginForm, SignupForm, ProfileForm, SearchForm, FilterForm
from .models import locationdatabase, userdatabase, usersearchlogging, userlocationlogging
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce

import json 
import math
import requests
import datetime

# Create your views here.
def check_weather_basic():
    current_date = datetime.datetime.now()
    current_month = current_date.month
    return 4 <= current_month <= 9

def check_weather_api():
    return "Save money."
    # api_key = "DlGC49EZHwwBd6yuPPh3aMLedE5h9BT5"
    # location_id = "171"
    # date = ""
    
    # weather_url = f"https://dataservice.accuweather.com/currentconditions/v1/{location_id}/{date}?apikey={api_key}"
    
    # response = requests.get(weather_url, timeout=3)
    # result = response.json()
    
    # if response.ok:
    #     if result:
    #         weather_text = result[0]["WeatherText"]
           
    #         if weather_text == "Sunny":
    #             return "Good weather!"
    #         else:
    #             return "We would not recommend going in this bad weather."
    #     else:
    #         return "Service couldn't response." 
    # else:
    #     if check_weather_basic() is True:
    #         return "Good weather!"
    #     else:
    #         return "We would not recommend going in this bad weather."

def homepage(request, view_amount: int=12, page: int=1):
    context = {}
    
    with open('homepage/lang/en_US/index.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
    
    location_list = locationdatabase.objects.all().values().annotate(
        click_count=Coalesce(
            Subquery(
                userlocationlogging.objects.filter(
                    clicked_location=OuterRef('pk')
                ).values('clicked_location').annotate(
                    click_count=Count('clicked_location')
                ).values('click_count')[:1]
            ), 
            0, 
            output_field=IntegerField()
        )
    ).order_by('-click_count')
    
    context['locationlist'] = location_list[(page-1)*view_amount:page*view_amount]
    
    page_amount = math.ceil(len(location_list)/view_amount)
    context['details'] = [number for number in range(1, page_amount+1)]

    context["searchform"] = SearchForm
    context["filterform"] = FilterForm
    context["weather"] = check_weather_api()
    
    return render(request, 'index.html', context)

def log_in(request):
    context = {}
    context['loginform'] = LoginForm
    
    with open('homepage/lang/en_US/login.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
        
    return render(request, 'login.html', context)

def signup(request):
    context = {}
    context['signupform'] = SignupForm
    
    with open('homepage/lang/en_US/signup.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)

    return render(request, 'signup.html', context)

def profile(request):
    context = {}
    context['profileform'] = ProfileForm
    
    with open('homepage/lang/en_US/profile.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
        
    return render(request, 'profile.html', context)

def signup_register(request):
    context = {}
    with open('homepage/lang/en_US/signup.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
        
    if request.method == "POST":
        form = SignupForm(request.POST)
        context['signupform'] = form
        if form.is_valid():
            # Process form data and save the user
            username = form.cleaned_data['signup_username']
            email = form.cleaned_data['signup_email']
            full_name = form.cleaned_data['signup_fullname']
            jobs = form.cleaned_data['signup_job']
            salary = form.cleaned_data['signup_salary']
            phone = form.cleaned_data['signup_phone']
            password = form.cleaned_data['signup_password']
            # Perform any additional processing before saving the user
            
            # Save the user (assuming you have a User model)
            user = userdatabase.objects.create_user(
                username=username,
                email=email,
                full_name=full_name,
                jobs=jobs,
                salary=salary,
                phone=phone,
                password=password
            )
            
            # Redirect to another page on successful signup
            return redirect(reverse('homepage'))
        else:
            return render(request, 'signup.html', context)
    else:
        form = SignupForm()
        context['signupform'] = form
        return render(request, 'signup.html', context)

def signup_complete(request):
    context = {}
    
    with open('homepage/lang/en_US/signup_complete.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)

    return render(request, 'message.html', context)

def log_in_check(request):
    context = {}
    with open('homepage/lang/en_US/login.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)

    if request.user.is_authenticated:
        return redirect(reverse('homepage'))
        
    if request.method == "POST":
        form = LoginForm(request.POST)
        context['loginform'] = form
        
        if form.is_valid():
            email = form.cleaned_data['login_email']
            password = form.cleaned_data['login_password']
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect(reverse('homepage'))
        else:
            return render(request, 'login.html', context)
    else:
        form = LoginForm()
        context['loginform'] = form
        return render(request, 'login.html', context)

def log_in_complete(request):
    context = {}
    
    with open('homepage/lang/en_US/login_complete.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)

    return render(request, 'message.html', context)

def log_out(request):
    logout(request)
    
    return redirect(reverse('homepage'))

def location_detail(request, slug):
    context = {}
    with open('homepage/lang/en_US/index.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
        
    loc_detail = locationdatabase.objects.get(slug=slug)
    context['loc_detail'] = loc_detail
    context['tag_string'] = " ".join(["#" + "".join(tag.lower().split("_")) for tag in loc_detail.tags.split(" ")])
    
    locationLogging = userlocationlogging()
    
    if request.user.is_authenticated:
        locationLogging.username = userdatabase.objects.get(username=request.user.username)
        locationLogging.clicked_location = loc_detail
        locationLogging.save()
    
    return render(request, 'detailpage.html', context)

def search_request(request):
    context = {}
    context["searchform"] = SearchForm
    
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['search_input']
            url = "http://192.168.1.8:8000/{}".format(question)
            
            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.Timeout as e:
                messages.error(request, "Error: " + "Connection Timeout") 
                return redirect(reverse('homepage'))
            
            if response.status_code == 200:
                data = response.json()["result"]
                fetch_list = []
                
                for name in data:
                    try:
                        fetch_list.append(locationdatabase.objects.get(place_name__iexact=name))
                    except Exception as e:
                        pass
                    
                if not fetch_list:
                    messages.error(request,  "Error: Unable able to find locations based on question.")
                    return redirect(reverse('homepage'))
                
                messages.error(request, "Success!")
                 
            else:
                messages.error(request,  "Error: " + str(response.status_code) + " " + response.text)
                return redirect(reverse('homepage'))
    
    with open('homepage/lang/en_US/index.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
    
    context["searchform"] = SearchForm
    context["filterform"] = FilterForm
    context["locationlist"] = fetch_list
    context["weather"] = check_weather_api()
    
    searchLogging = usersearchlogging()
    
    if request.user.is_authenticated:
        searchLogging.username = userdatabase.objects.get(username=request.user.username)
        searchLogging.search_query = question
        searchLogging.result_query = fetch_list
        searchLogging.save()
    
    return render(request, 'index.html', context)
    