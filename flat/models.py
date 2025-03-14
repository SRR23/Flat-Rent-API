from django.db import models
from user_profile.models import User
from django.utils.text import slugify
from .slug import generate_unique_slug
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
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
        """🔹 Save method to handle image updates and avoid unnecessary queries."""
        updating = self.pk is not None  # Check if the object is being updated

        if updating:
            # Fetch the original object to compare images and check for updates
            original = Flat.objects.get(pk=self.pk)
            
            # Check if any image has been updated, and delete the old image from Cloudinary
            if original:
                if original.image_1 != self.image_1:
                    if original.image_1:
                        self._delete_image_from_cloudinary(original.image_1)
                if original.image_2 != self.image_2:
                    if original.image_2:
                        self._delete_image_from_cloudinary(original.image_2)
                if original.image_3 != self.image_3:
                    if original.image_3:
                        self._delete_image_from_cloudinary(original.image_3)
                if original.image_4 != self.image_4:
                    if original.image_4:
                        self._delete_image_from_cloudinary(original.image_4)
                
            # If the title has changed, generate a new slug
            if original.title != self.title:
                self.slug = generate_unique_slug(self, self.title, update=True)
                
        else:
            # Generate slug only for new objects
            self.slug = generate_unique_slug(self, self.title)

        # Call the parent class save method to store the flat object
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete method to remove images from Cloudinary when flat is deleted."""
        if self.image_1:
            self._delete_image_from_cloudinary(self.image_1)
        if self.image_2:
            self._delete_image_from_cloudinary(self.image_2)
        if self.image_3:
            self._delete_image_from_cloudinary(self.image_3)
        if self.image_4:
            self._delete_image_from_cloudinary(self.image_4)

        # Call the parent class delete method to remove the record from the database
        super().delete(*args, **kwargs)

    def _delete_image_from_cloudinary(self, image_field):
        """Helper function to delete image from Cloudinary."""
        if image_field and image_field.url:
            public_id = image_field.url.split('/')[-1].split('.')[0]  # Extract the public_id from URL
            try:
                destroy(public_id)  # Delete image from Cloudinary
            except Exception as e:
                print(f"Error deleting image from Cloudinary: {e}")

    # def save(self, *args, **kwargs):
    #     """🔹 Optimized save method to prevent unnecessary queries."""
    #     if self.pk:
    #         # Fetch only title, avoid full object retrieval
    #         original_title = self.__class__.objects.filter(pk=self.pk).values_list('title', flat=True).first()
    #         if original_title and original_title != self.title:
    #             self.slug = generate_unique_slug(self, self.title, update=True)
    #     else:
    #         self.slug = generate_unique_slug(self, self.title)

    #     super().save(*args, **kwargs)
        
    
    # def delete(self, *args, **kwargs):
    #     # Handle image_1
    #     if self.image_1:
    #         public_id_1 = self.image_1.public_id  # FIXED
    #         destroy(public_id_1)

    #     # Handle image_2
    #     if self.image_2:
    #         public_id_2 = self.image_2.public_id  # FIXED
    #         destroy(public_id_2)

    #     # Handle image_3
    #     if self.image_3:
    #         public_id_3 = self.image_3.public_id  # FIXED
    #         destroy(public_id_3)

    #     # Handle image_4
    #     if self.image_4:
    #         public_id_4 = self.image_4.public_id  # FIXED
    #         destroy(public_id_4)

    #     # Call the parent class delete method to remove the record from the database
    #     super().delete(*args, **kwargs)


