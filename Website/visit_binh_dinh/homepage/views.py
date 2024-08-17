from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Avg, Case, FloatField, IntegerField, Value, When
)

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.serializers import serialize

from .forms import LoginForm, SignupForm, ProfileForm, SearchForm, FilterForm, SALARY_CHOICE
from .models import locationdatabase, userdatabase, usersearchlogging, userlocationlogging, userratinglogging, usertagweight, weatherdatabase

import ast
import json 
import math
import requests
import datetime
import os
import logging
import shutil
import uuid

from . import Get_tags_weight_copilot

def check_approve_weather(weather_input, location_slug):
    location = locationdatabase.objects.filter(slug=location_slug).first()
    weather_list = location.suitable_weather
    
    print(weather_input, weather_list)
    
    if "any" in weather_list:
        return True
    
    return modify_weather_text(weather_input) in weather_list

def find_max_salary_choice(salary_choices):
    numbers = [int(choice[0]) for choice in salary_choices]
    return max(numbers)
    
def extract_unique_tags(file_path = 'homepage/lang/en_US/tags.txt'):
    unique_tags = set() 
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tags = line.strip().split() 
            unique_tags.update(tags)
            result = [tag.replace('_', ' ').title() for tag in unique_tags]
    return result

def duplicate_weights_file(original_file='weights_common.npy', save_dir='path_to_save_files'):
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        unique_filename = f"weights_{uuid.uuid4().hex}.npy"
        unique_file_path = os.path.join(save_dir, unique_filename)

        shutil.copy2(original_file, unique_file_path)

        return unique_file_path 

    except FileNotFoundError:
        logging.error(f"The original file {original_file} was not found.")
        return None
    except PermissionError:
        logging.error(f"Permission denied when trying to copy {original_file}.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
def load_language_file(filepath):
    with open(filepath, encoding='utf-8') as lang_file:
        return json.load(lang_file)

def check_weather_basic():
    current_date = datetime.datetime.now()
    current_month = current_date.month
    return 4 <= current_month <= 9

def fetch_weather_data():
    api_key = "DlGC49EZHwwBd6yuPPh3aMLedE5h9BT5"
    location_id = "171"
    weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_id}?apikey={api_key}&details=true"

    try:
        response = requests.get(weather_url, timeout=3)
        response.raise_for_status()
        result = response.json()

        if result:
            for day in result["DailyForecasts"]:
                weather_text = day["Day"]["IconPhrase"]
                date = datetime.datetime.strptime(day["Date"], "%Y-%m-%dT%H:%M:%S%z").date()
                min_temp = day["Temperature"]["Minimum"]["Value"]
                max_temp = day["Temperature"]["Maximum"]["Value"]
                min_humidity = day["Day"]["RelativeHumidity"]["Minimum"]
                max_humidity = day["Day"]["RelativeHumidity"]["Maximum"]
                avg_humidity = day["Day"]["RelativeHumidity"]["Average"]

                weatherdatabase.objects.update_or_create(
                    location_id=location_id,
                    date=date,
                    defaults={
                        'weather_text': weather_text,
                        'min_temperature': min_temp,
                        'max_temperature': max_temp,
                        'min_humidity': min_humidity,
                        'max_humidity': max_humidity,
                        'avg_humidity': avg_humidity,
                    },
                )
            return True
        else:
            return False
    except requests.RequestException:
        return False

def check_weather_api(date=''):
    location_id = "171"
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.datetime.now().date()

    weather = weatherdatabase.objects.filter(location_id=location_id, date=date).first()

    if not weather:
        last_entry = weatherdatabase.objects.filter(location_id=location_id).order_by('date').last()
        
        if not last_entry or last_entry.date < datetime.datetime.now().date() + timedelta(days=5):
            if not fetch_weather_data():
                return "Service couldn't respond."

            weather = weatherdatabase.objects.filter(location_id=location_id, date=date).first()
            if not weather:
                return "Service couldn't respond."
    
    weather_text = weather.weather_text
    min_temp = round((weather.min_temperature - 32) * (5/9), 1)
    max_temp = round((weather.max_temperature - 32) * (5/9), 1)
    avg_humidity = weather.avg_humidity
    min_humidity = weather.min_humidity
    max_humidity = weather.max_humidity
    
    weather_info = f"Weather: {weather_text}, Min Temp: {min_temp}°C, Max Temp: {max_temp}°C, Lowest Humidity: {min_humidity}%, Highest Humidity: {max_humidity}%, Average Humidity: {avg_humidity}%"
    weather_tagline = categorize_weather(weather_text)

    return weather_text, weather_tagline, weather_info

def modify_weather_text(weather_text):
    weather_text = weather_text.lower()
    
    sunny_keywords = ['sunny', 'clear', 'mostly sunny', 'partly cloudy']
    rain_keywords = ['rain', 'showers', 'thunderstorm', 'drizzle', 'light rain']
    snow_keywords = ['snow', 'sleet', 'hail', 'wintry mix']
    cloudy_keywords = ['cloudy', 'overcast', 'mostly cloudy', 'partly cloudy']
    wind_keywords = ['wind', 'breezy', 'gusty']

    if any(keyword in weather_text for keyword in sunny_keywords):
        return 'sunny'
    elif any(keyword in weather_text for keyword in rain_keywords):
        return 'rain'
    elif any(keyword in weather_text for keyword in snow_keywords):
        return 'snow'
    elif any(keyword in weather_text for keyword in cloudy_keywords):
        return 'cloudy'
    elif any(keyword in weather_text for keyword in wind_keywords):
        return 'wind'
    else:
        return 'other'
    
def categorize_weather(weather_text):
    if "sunny" in weather_text.lower():
        return "Perfect day to enjoy the outdoors!"
    elif "rain" in weather_text.lower():
        return "Better bring an umbrella."
    elif "snow" in weather_text.lower():
        return "Get ready to build a snowman!"
    elif "cloudy" in weather_text.lower():
        return "The sky is overcast, but it could still be a good day for a walk."
    elif "wind" in weather_text.lower():
        return "Hold on to your hat!"
    else:
        return "Current weather is wild. Prepare for anything!"

def calculate_average_rating(place_slug):
    try:
        average_rating = userratinglogging.objects.filter(place_slug__slug=place_slug).aggregate(Avg('ratings'))['ratings__avg']
        return round(average_rating, 1) or 0
    except ObjectDoesNotExist:
        return None

def calculate_total_rating(place_slug):
    try:
        total_rating = len(userratinglogging.objects.filter(place_slug__slug=place_slug))
        return total_rating
    except ObjectDoesNotExist:
        return None
    
def parse_tags(tagslist):
    return [tag.upper().replace(" ", "_") for tag in ast.literal_eval(tagslist[0])]

def annotate_weather_priority(location_list, weather_category):
    return location_list.annotate(
        weather_priority=Case(
            When(tags__icontains=weather_category, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    )  

def get_user_weights_file(user):
    if user is None:
        return os.path.join('homepage', 'weights', 'weights_common.npy')
    
    if user.weights_file and os.path.exists(user.weights_file):
        return user.weights_file

    unique_weights_file = os.path.join('homepage', 'weights', f'weights_{uuid.uuid4().hex}.npy')
    user.weights_file = unique_weights_file

    try:
        shutil.copy(os.path.join('homepage', 'weights', 'weights_common.npy'), unique_weights_file)
    except IOError as e:
        return None

    Get_tags_weight_copilot.registration_weight(user.salary, user.weights_file)
    user.save()
    return unique_weights_file


def fetch_question_tags(question):
    url = f"http://127.0.0.1:7860/model/get_question_tags/{question}"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json().get("question_tags", [])
        return [" ".join([location.replace(" ", "_") for location in data])]
    
    except requests.RequestException:
        return None
    
def get_locations_by_similarity(data, weights_file, sort_order=False):
    name_list = Get_tags_weight_copilot.suggest_destination(data, file_path=weights_file, sort=sort_order, top_n=12)["name"]
    fetch_list = []

    for name in name_list:
        try:
            fetch_list.append(locationdatabase.objects.get(place_name__iexact=name))
        except locationdatabase.DoesNotExist:
            pass

    return fetch_list

def log_search_result(request, question, fetch_list):
    if request.user.is_authenticated:
        user = userdatabase.objects.get(username=request.user.username)
        usersearchlogging.objects.create(username=user, search_query=question, result_query=fetch_list)
       
def adjust_tag_weights(user, tags, adjustment):
    for tag in tags:
        user_tag_weight, created = usertagweight.objects.get_or_create(user=user, tag=tag)
        user_tag_weight.adjust_weight(adjustment)

def get_weighted_locations(user, location_list):
    user_weights = usertagweight.objects.filter(user=user).order_by('-weight')
    all_tags = extract_unique_tags()

    user_tag_weights = {weight.tag: weight.weight for weight in user_weights}

    cases = []
    penalties = []
    penalty_value = 0.1

    for tag in all_tags:
        if tag in user_tag_weights:
            cases.append(
                When(tags__icontains=tag, then=Value(user_tag_weights[tag]))
            )
        else:
            penalties.append(
                When(tags__icontains=tag, then=Value(penalty_value))
            )

    location_list = location_list.annotate(
        user_weight=Case(
            *cases,
            default=Value(penalty_value),
            output_field=FloatField()
        ) + Case(
            *penalties,
            default=Value(penalty_value),
            output_field=FloatField()
        )
    )
    
    print(location_list[0])

    return location_list

def sort_locations(location_list, sort_rating, sort_order, user):
    if user and user.is_authenticated:
        return sort_user_locations(location_list, sort_rating, sort_order, user)
    else:
        return sort_public_locations(location_list, sort_rating, sort_order)

def sort_user_locations(location_list, sort_rating, sort_order, user):
    if sort_rating == 'rating':
        location_list = location_list.annotate(average_rating=Avg('userratinglogging__ratings'))
        order_field = 'average_rating'
    elif sort_rating == 'views':
        order_field = 'view_count'
    else:
        location_list = get_weighted_locations(user, location_list)
        order_field = 'user_weight'

    return apply_order(location_list, order_field, sort_order)

def sort_public_locations(location_list, sort_rating, sort_order):
    order_field = 'average_rating' if sort_rating == 'rating' else 'view_count'
    return apply_order(location_list, order_field, sort_order)

def apply_order(location_list, order_field, sort_order):
    order = '' if sort_order == '1' else '-'
    return location_list.order_by(order + order_field)

def paginate_location_list(location_list, page, view_amount):
    start = (page - 1) * view_amount
    end = start + view_amount
    return location_list[start:end]

def initialize_context():
    return {
        "searchform": SearchForm(),
        "filterform": FilterForm(),
        'lang': load_language_file('homepage/lang/en_US/index.json'),
    }
     
def homepage(request, page: int = 1):
    context = initialize_context()

    view_amount = int(request.GET.get('view_amount', 12))
    sort_rating = request.GET.get('sort_rating', 'views')
    sort_order = request.GET.get('sort_order', '0')
    search_input = request.GET.get('search_input', '')
    date_input = request.GET.get('date_input', '')
    tagslist = request.GET.getlist('tagslist', '')

    form = FilterForm(initial={
        'search_input': search_input,
        'date_input': date_input,
        'sort_rating': sort_rating,
        'sort_order': sort_order,
        'tag_search': tagslist,
    })
    location_list = locationdatabase.objects.all()
    
    if search_input:
        location_list = location_list.filter(place_name__icontains=search_input)

    if not location_list.exists():
        context["search_logging"] = "We are sorry. We weren't able to find any locations that match your search preferences."

    if tagslist:
        tags = parse_tags(tagslist)
        for tag in tags:
            location_list = location_list.filter(tags__icontains=tag)

    current_weather, weather_tagline, weather_info = check_weather_api(date=date_input)
    
    location_list = annotate_weather_priority(location_list, current_weather)
    location_list = sort_locations(location_list, sort_rating, sort_order, request.user)
    paginated_list = paginate_location_list(location_list, page, view_amount)

    for location in paginated_list:
        location.average_rating = calculate_average_rating(location.slug)
        location.total_rating = calculate_total_rating(location.slug)
        location.weather_approve = check_approve_weather(current_weather, location.slug)

    context.update({
        'locationlist': paginated_list,
        'details': range(1, math.ceil(len(location_list) / view_amount) + 1),
        "filterform": form,
        "weather": weather_tagline + " " + weather_info,
        'request': request,
    })

    return render(request, 'index.html', context)

@csrf_protect
def search_request(request):
    context = initialize_context()

    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['search_input']
            sort_mode = form.cleaned_data['sort_rating']
            sort_order = [True if form.cleaned_data['sort_order'] == '0' else False][0]
            current_weather, weather_tagline, weather_info = check_weather_api()
            
            user = request.user if request.user.is_authenticated else None
            
            weights_file = get_user_weights_file(user)
            if weights_file is None:
                context["search_logging"] = "Error: Unable to create weights file."
                return render(request, 'index.html', context)

            data = fetch_question_tags(question)
            print(data)
            if data is None:
                context["search_logging"] = "Error: Connection Timeout or Server Error"
                return render(request, 'index.html', context)
            
            try:
                if user:  
                    unprocessed_logs = usersearchlogging.objects.filter(username=user, processed=False).order_by('-search_date')[0]

                if unprocessed_logs:
                    Get_tags_weight_copilot.history_weights(ast.literal_eval(unprocessed_logs.result_query), 0.1, weights=user.weights_file)
                    unprocessed_logs.processed = True
                    unprocessed_logs.save()
            except Exception as e:
                print('Unexpected error.')            
            
            fetch_list = get_locations_by_similarity(data, weights_file, not sort_order)
            if not fetch_list:
                context["search_logging"] = "Error: Unable to find locations based on question."
                return render(request, 'index.html', context)

            log_search_result(request, question, data)
            context["search_logging"] = "Success! Please scroll down for your result."

            for location in fetch_list:
                location.average_rating = calculate_average_rating(location.slug)
                location.total_rating = calculate_total_rating(location.slug)
                location.weather_approve = check_approve_weather(current_weather, location.slug)
        
            if sort_mode == 'rating':
                fetch_list.sort(key=lambda x: x.average_rating, reverse=sort_order)
            elif sort_mode == 'views':
                fetch_list.sort(key=lambda x: x.view_count, reverse=sort_order)
            
            context.update({
                "locationlist": fetch_list,
                "locationlist_json": serialize('json', fetch_list),
                "weather": weather_tagline + " " + weather_info,
                "question_tags": data,
                "show_rating": True
            })
            return render(request, 'index.html', context)

    return render(request, 'index.html', context)

def filter_locations(request):
    if request.method == "GET":
        form = FilterForm(request.GET)
        if form.is_valid():
            search_input = form.cleaned_data['search_input']
            date_input = form.cleaned_data['date_input']
            tagslist = form.cleaned_data['tagslist']
            sort_rating = form.cleaned_data['sort_rating']
            sort_order = form.cleaned_data['sort_order']
            
            query_params = {}
            if search_input:
                query_params['search_input'] = search_input
            if date_input:
                query_params['date_input'] = date_input.strftime('%Y-%m-%d')
            if tagslist:
                query_params['tagslist'] = tagslist

            query_params['sort_rating'] = sort_rating
            query_params['sort_order'] = sort_order
                
            query_string = urlencode(query_params)

            return redirect(f"{reverse('homepage')}?{query_string}#searchsection")
    
    return redirect(reverse('homepage'))

def log_in(request):
    context = {
        'loginform': LoginForm,
        'lang': load_language_file('homepage/lang/en_US/login.json')
    }
    return render(request, 'login.html', context)

def signup(request):
    context = {
        'signupform': SignupForm,
        'lang': load_language_file('homepage/lang/en_US/signup.json')
    }
    return render(request, 'signup.html', context)

def profile(request):
    context = {
        'profileform': ProfileForm,
        'lang': load_language_file('homepage/lang/en_US/profile.json')
    }

    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = ProfileForm(instance=user)

    context = {
        'profileform': form,
        'lang': load_language_file('homepage/lang/en_US/profile.json')
    }
    return render(request, 'profile.html', context)

@csrf_protect
def signup_register(request):
    context = {'lang': load_language_file('homepage/lang/en_US/signup.json')}
    User = get_user_model()  # Use this to refer to the user model

    if request.method == "POST":
        form = SignupForm(request.POST)
        context['signupform'] = form
        if form.is_valid():
            username = form.cleaned_data['signup_username']
            email = form.cleaned_data['signup_email']

            if User.objects.filter(username=username).exists():
                form.add_error('signup_username', 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                form.add_error('signup_email', 'Email already exists.')
            else:
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        full_name=form.cleaned_data['signup_fullname'],
                        jobs=form.cleaned_data['signup_job'],
                        salary=form.cleaned_data['signup_salary'],
                        phone=form.cleaned_data['signup_phone'],
                        password=form.cleaned_data['signup_password']
                    )
                    return redirect(reverse('homepage'))
                except Exception as e:
                    form.add_error(None, f"An unexpected error occurred: {e}")

        return render(request, 'signup.html', context)
    else:
        context['signupform'] = SignupForm()
        return render(request, 'signup.html', context)


def signup_complete(request):
    context = {'lang': load_language_file('homepage/lang/en_US/signup_complete.json')}
    return render(request, 'message.html', context)

@csrf_protect
def log_in_check(request):
    context = {'lang': load_language_file('homepage/lang/en_US/login.json')}

    if request.user.is_authenticated:
        return redirect(reverse('homepage'))

    if request.method == "POST":
        form = LoginForm(request.POST)
        context['loginform'] = form

        if form.is_valid():
            email = form.cleaned_data['login_email']
            password = form.cleaned_data['login_password']

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect(reverse('homepage'))
            else:
                messages.error(request, "Invalid email or password.")
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html', context)
    else:
        context['loginform'] = LoginForm()
        return render(request, 'login.html', context)

def log_in_complete(request):
    context = {'lang': load_language_file('homepage/lang/en_US/login_complete.json')}
    return render(request, 'message.html', context)

def log_out(request):
    logout(request)
    return redirect(reverse('homepage'))

@csrf_protect
def location_detail(request, slug):
    context = {'lang': load_language_file('homepage/lang/en_US/index.json')}

    try:
        loc_detail = locationdatabase.objects.get(slug=slug)
    except locationdatabase.DoesNotExist:
        messages.error(request, "Location does not exist.")
        return redirect(reverse('homepage'))

    loc_rating = calculate_average_rating(loc_detail.slug)
    
    context['loc_rating'] = loc_rating
    context['loc_detail'] = loc_detail
    context['tag_string'] = " ".join(([f"#{tag.lower().replace('_', '')}" for tag in loc_detail.tags.split()]))

    if request.user.is_authenticated:
        user = userdatabase.objects.get(username=request.user.username)
        adjust_tag_weights(user, loc_detail.tags.split(), adjustment=0.05)
        
        try:
            user_location_log = userlocationlogging.objects.filter(username=user, clicked_location=loc_detail).latest('last_viewed')
        except userlocationlogging.DoesNotExist:
            user_location_log = None
        
        if user_location_log is None or user_location_log.last_viewed < timezone.now() - timedelta(minutes=1):
            if user_location_log:
                user_location_log.last_viewed = timezone.now()
            else:
                user_location_log = userlocationlogging.objects.create(
                    username=user,
                    clicked_location=loc_detail,
                    last_viewed=timezone.now()
                )
            
            loc_detail.view_count += 1
            loc_detail.save()

        user_location_log.save()

        user_rating = userratinglogging.objects.filter(place_slug=loc_detail, user=user).first()
        context['rating_number'] = user_rating.ratings if user_rating else None
    else:
        context['rating_number'] = None

    return render(request, 'detailpage.html', context)

@csrf_protect
def rate_location(request, slug):
    if request.method == 'GET':
        rating = request.GET.get('rating', 0)
        rating = int(rating) if rating.isdigit() else 0

        if request.user.is_authenticated and rating != 0:
            try:
                loc_detail = locationdatabase.objects.get(slug=slug)
                user = userdatabase.objects.get(username=request.user.username)
                userratinglogging.objects.update_or_create(
                    place_slug=loc_detail,
                    user=user,
                    defaults={'ratings': rating}
                )
                
                adjustment = (rating - 3) * 0.1 
                adjust_tag_weights(user, loc_detail.tags.split(), adjustment)
                
            except locationdatabase.DoesNotExist:
                pass
            except Exception as e:
                pass
        else:
            pass
        
    return redirect(reverse('location_detail', args=[slug]))

@require_POST
def rate_result(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))
        question_tags = ast.literal_eval(data.get('question_tags', '[]'))
        location_id = data.get('location_id')
        user = request.user

        if rating != 0 and location_id:
            try:
                location = locationdatabase.objects.get(place_id=location_id)
                weights_file = get_user_weights_file(user)

                Get_tags_weight_copilot.customize_weights(
                    rating=rating, destination_name=location.place_name, question_tags=question_tags,
                    weights=weights_file
                )
                Get_tags_weight_copilot.compare_and_print_differences(weights_file)
                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request."})