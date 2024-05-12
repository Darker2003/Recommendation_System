from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import userdatabase

SALARY_CHOICE = {("1", "1.000.000đ - 3.000.000đ"), ("2", "6.000.000đ - 100.000.000d")}

JOB_CHOICE = {("1", "Student"), ("2", "Other")}

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
    )
    signup_fullname = forms.CharField(
        max_length="50",
        min_length="2",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your name here (Optional)."}
        ),
        validators=[
            RegexValidator(
                r"^\S+$", "Username must not contain any whitespace characters."
            )
        ],
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
        
        if email is None:
            raise ValidationError("Email cannot be None.")
        
        if userdatabase.objects.filter(email=email).exists:
            raise ValidationError("Email exists.")

        return email 
    
    def clean_signup_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("signup_username")
        
        if username is None:
            raise ValidationError("Username cannot be None.")
        
        if userdatabase.objects.filter(username=username).exists:
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
        widget=forms.TextInput(attrs={"placeholder": "Search query here.", 'id':"searchbar"}))
    
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

class FilterForm(forms.Form):
    tags_file_path = 'homepage/lang/en_US/tags.txt'  # Replace with the path to your tags file
    
    search_input = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "smallsearchbar", "placeholder": "Search query here."})
    )
    
    date_input = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "id": "birthday", "name": "birthday"})
    )

    tag_search = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "smallsearchbar", "placeholder": "Search tags"})
    )

    tagslist = forms.MultipleChoiceField(
        choices=[],  # This will be populated dynamically
        required=False
    )

    def __init__(self, *args, tagslist=extract_unique_tags(tags_file_path), **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['tagslist'].choices = [(tag, tag) for tag in tagslist]
        
    def render_tagslist(self):
        tags_html = ''
        for tag_value, tag_label in self.fields['tagslist'].choices:
            tags_html += f'''
                <div class="locationcontainer">
                    <input type="checkbox" id="{tag_value}" class="tag" name="tagslist" value="{tag_value}">
                    <label for="{tag_value}" class="locationtagtext">{tag_label}</label>
                </div>
            '''
        return tags_html