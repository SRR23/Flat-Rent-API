from django.db import models
from user_profile.models import User
from django.utils.text import slugify
from .slug import generate_unique_slug
from cloudinary.models import CloudinaryField
# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        
class Location(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Flat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flats")
    renters_who_messaged = models.ManyToManyField(User, blank=True, related_name="messaged_flats")  # New field
    category = models.ForeignKey(
        Category, related_name="category_flats", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, related_name="location_flats", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    slug=models.SlugField(null=True, blank=True)

    flat_size = models.IntegerField()
    room = models.IntegerField()
    bath = models.IntegerField()
    kitchen = models.IntegerField()
    price = models.IntegerField(default=0)

    # Cloudinary Image Fields
    image_1 = CloudinaryField("image", blank=True, null=True)
    image_2 = CloudinaryField("image", blank=True, null=True)
    image_3 = CloudinaryField("image", blank=True, null=True)
    image_4 = CloudinaryField("image", blank=True, null=True)

    feature_1 = models.CharField(max_length=255)
    feature_2 = models.CharField(max_length=255)
    feature_3 = models.CharField(max_length=255)
    feature_4 = models.CharField(max_length=255)
    feature_5 = models.CharField(max_length=255)

    description_1 = models.CharField(max_length=255)
    description_2 = models.CharField(max_length=255)
    description_3 = models.CharField(max_length=255)
    description_4 = models.CharField(max_length=255)
    description_5 = models.CharField(max_length=255)

    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # available = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """🔹 Optimized save method to prevent unnecessary queries."""
        if self.pk:
            # Fetch only title, avoid full object retrieval
            original_title = self.__class__.objects.filter(pk=self.pk).values_list('title', flat=True).first()
            if original_title and original_title != self.title:
                self.slug = generate_unique_slug(self, self.title, update=True)
        else:
            self.slug = generate_unique_slug(self, self.title)

        super().save(*args, **kwargs)

