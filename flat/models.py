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
    available = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate a unique slug for the blog
        # This method is called before saving the object
        # It checks if the object is being updated or created
        # If the object is being updated, it checks if the title has changed
        # If the title has changed, it generates a new slug
        # If the object is new, it generates a new slug

        updating = self.pk is not None  # Check if the object is being updated

        if updating:
            # Fetch the original object to check if the title has changed
            original = Flat.objects.get(pk=self.pk)
            if original.title != self.title:  # Check if the title has changed
                self.slug = generate_unique_slug(
                    self, self.title, update=True
                )  # Generate a new slug
        else:
            # Generate slug only for new objects
            self.slug = generate_unique_slug(self, self.title)

        super().save(*args, **kwargs)
