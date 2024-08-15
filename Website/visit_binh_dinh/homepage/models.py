from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db import models
from django.conf import settings
    
# Create your models here.
class locationdatabase(models.Model):
    place_id = models.BigAutoField(primary_key=True)
    place_name = models.CharField(max_length=100, unique=True)
    place_desc = models.CharField(max_length=800)
    address = models.CharField(max_length=100, default="Quy Nhon")
    ratings = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to='location_images/')
    tags = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=False, unique=True) 
    suitable_weather = models.JSONField(default=list)
    view_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.place_id}.{self.place_name}"
    
    def get_absolute_url(self):
        return reverse("location_detail", kwargs={"slug": self.slug})
    
    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, password=password, **extra_fields)

class userdatabase(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    personid = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, default='default_username')
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    jobs = models.CharField(max_length=100, default=0)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(validators=[phone_regex], max_length=17)
    user_location = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True) 
    weights_file = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}.{self.email}"

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
class userlocationlogging(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    username = models.ForeignKey('userdatabase', on_delete=models.CASCADE, null=True)
    clicked_location = models.ForeignKey('locationdatabase', on_delete=models.CASCADE)
    clicked_date = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now=True)
    
class usersearchlogging(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    username = models.ForeignKey('userdatabase', on_delete=models.CASCADE, null=True)
    search_query = models.TextField()
    result_query = models.TextField(null=True)
    search_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.log_id}, {self.username}, {self.search_query}, {self.result_query}, {self.processed}"
    
class commentreview(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    content = models.ForeignKey('locationdatabase', on_delete=models.CASCADE)
    user = models.ForeignKey('userdatabase', on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.comment_id}.{self.user}"
    
class userratinglogging(models.Model):
    place_slug = models.ForeignKey('locationdatabase', on_delete=models.CASCADE)
    user = models.ForeignKey('userdatabase', on_delete=models.CASCADE)
    ratings = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

class usertagweight(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.CharField(max_length=50)
    weight = models.FloatField(default=0.5)

    class Meta:
        unique_together = ('user', 'tag')

    def __str__(self):
        return f'{self.user.username} - {self.tag}: {self.weight}'

    def adjust_weight(self, adjustment, decay_factor=0.95):
        self.weight *= decay_factor
        self.weight = self.weight + adjustment
        self.save()