from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import LoginForm, SignupForm, ProfileForm, SearchForm
from .models import locationdatabase, userdatabase, usersearchlogging
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

import json 
import math
import requests

# Create your views here.
def extract_unique_tags(file_path):
    unique_tags = set()  # Using a set to automatically ensure uniqueness
    
    # Open the file
    with open(file_path, 'r', encoding='utf-8') as file:
        # Iterate through each line in the file
        for line in file:
            # Split the line into tags based on spaces
            tags = line.strip().split()  # No need to specify the separator as split() splits on whitespace by default
            # Add each tag to the set
            unique_tags.update(tags)
            result = [tag.replace('_', ' ').title() for tag in unique_tags]
    return result

def homepage(request, view_amount: int=12, page: int=1):
    context = {}
    with open('homepage/lang/en_US/index.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
    
    location_list = locationdatabase.objects.all().values()
    context['locationlist'] = location_list[(page-1)*view_amount:page*view_amount]
    
    page_amount = math.ceil(len(location_list)/view_amount)
    context['details'] = [number for number in range(1, page_amount+1)]
    
    tags_file_path = 'homepage/lang/en_US/tags.txt'  # Replace with the path to your tags file
    unique_tags = extract_unique_tags(tags_file_path)
    context['tagslist'] = unique_tags
    
    context["searchform"] = SearchForm
    
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
    
    return render(request, 'detailpage.html', context)

def search_request(request):
    context = {}
    context["searchform"] = SearchForm
    
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['search_input']
            url = "http://192.168.1.38:8000/{}".format(question)
            
            try:
                response = requests.get(url, timeout=3)
            except requests.exceptions.Timeout as e:
                messages.error(request, "Error: " + "Connection Timeout") 
                return redirect(reverse('homepage'))
            else:
                if response.ok:
                    data = response.json()["result"]
                    fetch_list = []
                    
                    for name in data:
                        try:
                            fetch_list.append(locationdatabase.objects.get(place_name__iexact=name))
                        except Exception as e:
                            pass
                        
                    if not fetch_list:
                        messages.error(request,  "Error: " + "Unable able to find locations based on question.")
                        return redirect(reverse('homepage'))
                else:
                    messages.error(request,  "Error: " + response.status_code + response.text)
                    return redirect(reverse('homepage'))
    
    with open('homepage/lang/en_US/index.json', encoding='utf-8') as lang_file:
        context['lang'] = json.load(lang_file)
        
    context["locationlist"] = fetch_list
    
    searchLogging = usersearchlogging()
    
    if request.user.is_authenticated:
        searchLogging.user = request.user.username
    else:
        searchLogging.user = "a_user"
        
    searchLogging.search_query = question
    searchLogging.result_query = fetch_list
    searchLogging.save()
    
    return render(request, 'index.html', context)
    