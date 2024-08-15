from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import userdatabase

import datetime

SALARY_CHOICE = [
    ("1", "Under 5.000.000đ"),
    ("2", "5.000.000đ - 10.000.000đ"),
    ("3", "10.000.000đ - 15.000.000đ"),
    ("4", "15.000.000đ - 20.000.000đ"),
    ("5", "20.000.000đ - 30.000.000đ"),
    ("6", "30.000.000đ - 50.000.000đ"),
    ("7", "50.000.000đ - 70.000.000đ"),
    ("8", "70.000.000đ - 100.000.000đ"),
    ("9", "Over 100.000.000đ"),
]

JOB_CHOICE = [
    ("1", "Software Developer"),
    ("2", "Web Developer"),
    ("3", "Data Scientist"),
    ("4", "Project Manager"),
    ("5", "Business Analyst"),
    ("6", "Graphic Designer"),
    ("7", "Marketing Specialist"),
    ("8", "Sales Representative"),
    ("9", "Customer Service Representative"),
    ("10", "Human Resources Specialist"),
    ("11", "Finance Analyst"),
    ("12", "Product Manager"),
    ("13", "Administrative Assistant"),
    ("14", "Consultant"),
    ("15", "Other"),
]

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = userdatabase
        fields = ("username", "email", )
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = userdatabase
        fields = ("username", "email", )
        
class LoginForm(forms.Form):
    login_email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Insert your email here."}),
    )
    login_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Insert your password here."}),
        required=True,
    )
    check_remember = forms.BooleanField(label="checkremember", required=False)

    def clean_login_email(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("login_email")
        
        if email is None:
            raise ValidationError("Email cannot be None.")
        
        if not userdatabase.objects.filter(email=email).exists():
            raise ValidationError("Email does not exist.")

        return email 
    
    def clean_login_password(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("login_email")
        password = cleaned_data.get("login_password")
        
        if not email:
            return None
        
        try:
            database_password = userdatabase.objects.get(email=email).password
        except userdatabase.DoesNotExist:
            raise ValidationError("Email does not exist.", code='invalid')
        
        if not check_password(password, database_password):
            raise ValidationError("Password does not match.")
        
        return password
    
class SignupForm(forms.Form):
    signup_email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Invalid email.")],
        widget=forms.TextInput(attrs={"placeholder": "Insert your email here."}),
    )
    signup_username = forms.CharField(
        max_length="15",
        min_length="6",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your username here."}),
        validators=[
            RegexValidator(
                r"^\S+$", "Username must not contain any whitespace characters."
            )
        ],
    )
    signup_fullname = forms.CharField(
        max_length="50",
        min_length="2",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your name here (Optional)."}
        ),
    )
    signup_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Insert your password here."}),
        required=True,
    )
    signup_repassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Re-enter your password here."}
        ),
        required=True,
    )
    signup_salary = forms.ChoiceField(
        choices=SALARY_CHOICE,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="",
        required=True,
    )
    signup_job = forms.ChoiceField(
        choices=JOB_CHOICE,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="",
        required=True,
    )
    signup_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={"placeholder": "Insert your phone here."}),
    )
    agree_terms = forms.BooleanField(label="agreeterms", required=True)

    def clean_signup_email(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("signup_email")
        
        print(email)
        
        if email is None:
            raise ValidationError("Email cannot be None.")
        
        if userdatabase.objects.filter(email=email).exists():
            raise ValidationError("Email exists.")

        return email 
    
    def clean_signup_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("signup_username")
        
        if username is None:
            raise ValidationError("Username cannot be None.")
        
        if userdatabase.objects.filter(username=username).exists():
            raise ValidationError("Username exists.")
        
        return username
             
    def clean_signup_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("signup_password")
        
        validate_password(password)
        
        return password  
      
    def clean_signup_repassword(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("signup_password")
        repassword = cleaned_data.get("signup_repassword")

        if password != repassword:
            raise ValidationError("Password and confirm password does NOT MATCH.")

        return cleaned_data

class ProfileForm(forms.Form):
    profile_email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"placeholder": "Your email here."})
    )
    profile_fullname = forms.CharField(
        max_length="50",
        min_length="2",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Your name here"}),
    )
    profile_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Your password here."}),
        required=True,
    )
    profile_repassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Re-enter your password here."}
        ),
        required=True,
    )

class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length="150",
        min_length="2",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Search query here.", 'class':"form-control"}))
    
    date_input = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={"type": "date", "id": "birthday", "name": "birthday", "class": "form-control flex-grow-1", 'style': 'width: auto'})
    )
    
    sort_rating = forms.ChoiceField(
        choices=[('default', 'Default'), ('views', 'Views'), ('rating', 'Rating')],
        required=False,
        widget=forms.Select(attrs={"class": "form-select flex-grow-1", 'style': 'width: auto'})
    )
    
    sort_order = forms.ChoiceField(
        choices=[('0', 'Descending'), ('1', 'Ascending')],
        required=False,
        widget=forms.Select(attrs={"class": "form-select flex-grow-1", 'style': 'width: auto'})
    )
        
def extract_unique_tags(file_path = 'homepage/lang/en_US/tags.txt'):
    unique_tags = set() 
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tags = line.strip().split() 
            unique_tags.update(tags)
            result = [tag.replace('_', ' ').title() for tag in unique_tags]
    return result

class FilterForm(forms.Form):  
    search_input = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Search query here."})
    )
    
    date_input = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={"type": "date", "id": "birthday", "name": "birthday", "class": "form-control"})
    )

    tagslist = forms.MultipleChoiceField(
        choices=[], 
        required=False
    )

    sort_rating = forms.ChoiceField(
        choices=[('default', 'Default'), ('views', 'Views'), ('rating', 'Rating')],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    sort_order = forms.ChoiceField(
        choices=[('0', 'Descending'), ('1', 'Ascending')],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    def __init__(self, *args, tagslist=extract_unique_tags(), **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['tagslist'].choices = [(tag, tag) for tag in tagslist]
            
    def render_tagslist(self):
        tags_html = '<div class="d-list">'

        for i, (tag_value, tag_label) in enumerate(self.fields['tagslist'].choices):
            if i < 5:
                tags_html += f'''
                    <input type="checkbox" class="btn-check" id="{tag_value}" name="tagslist" value="{tag_value}" autocomplete="off">
                    <label class="btn btn-outline-primary m-1 tag-btn" for="{tag_value}">{tag_label}</label>
                '''
            else:
                tags_html += f'''
                    <input type="checkbox" class="btn-check" id="{tag_value}" name="tagslist" value="{tag_value}" autocomplete="off">
                    <label class="btn btn-outline-primary m-1 hidden-tag tag-btn" for="{tag_value}">{tag_label}</label>
                '''

        tags_html += '</div>'

        if len(self.fields['tagslist'].choices) > 5:
            tags_html += '''
                <div id="toggle-buttons" class="mt-2">
                    <button id="show-more-button" type="button" class="btn btn-primary btn-sm" onclick="showMoreTags()">Show more</button>
                    <button id="show-less-button" type="button" class="btn btn-primary btn-sm" onclick="showLessTags()" style="display: none;">Show less</button>
                </div>
            '''

        return tags_html
