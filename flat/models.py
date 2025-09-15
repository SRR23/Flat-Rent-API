from django.db import models
from user_profile.models import User
from django.utils.text import slugify
from .slug import generate_unique_slug
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy


class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Location(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Flat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flats")
    renters_who_messaged = models.ManyToManyField(User, blank=True, related_name="messaged_flats")
    category = models.ForeignKey(
        Category, related_name="category_flats", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, related_name="location_flats", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    washroom = models.IntegerField()
    commode = models.BooleanField(default=True)
    water_supply = models.BooleanField(default=True)
    floor = models.CharField(max_length=50, default='')
    tiles = models.BooleanField(default=True)
    kitchen = models.BooleanField(default=True)
    cctv = models.BooleanField(default=False)
    roof_top_uses = models.BooleanField(default=False)
    garage = models.BooleanField(default=False)

    image_1 = CloudinaryField("image", blank=True, null=True)
    image_2 = CloudinaryField("image", blank=True, null=True)
    image_3 = CloudinaryField("image", blank=True, null=True)
    image_4 = CloudinaryField("image", blank=True, null=True)
    image_5 = CloudinaryField("image", blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Handle slug generation and image updates."""
        updating = self.pk is not None

        if updating:
            original = Flat.objects.get(pk=self.pk)
            if original:
                if original.image_1 != self.image_1 and original.image_1:
                    self._delete_image_from_cloudinary(original.image_1)
                if original.image_2 != self.image_2 and original.image_2:
                    self._delete_image_from_cloudinary(original.image_2)
                if original.image_3 != self.image_3 and original.image_3:
                    self._delete_image_from_cloudinary(original.image_3)
                if original.image_4 != self.image_4 and original.image_4:
                    self._delete_image_from_cloudinary(original.image_4)
                if original.title != self.title:
                    self.slug = generate_unique_slug(self, self.title, update=True)
        else:
            self.slug = generate_unique_slug(self, self.title)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Remove images from Cloudinary when flat is deleted."""
        for image_field in [self.image_1, self.image_2, self.image_3, self.image_4]:
            if image_field:
                self._delete_image_from_cloudinary(image_field)
        super().delete(*args, **kwargs)

    def _delete_image_from_cloudinary(self, image_field):
        """Helper function to delete image from Cloudinary."""
        if image_field and image_field.url:
            public_id = image_field.url.split('/')[-1].split('.')[0]
            try:
                destroy(public_id)
            except Exception as e:
                print(f"Error deleting image from Cloudinary: {e}")


class Family(models.Model):
    flat = models.ForeignKey(
        Flat, 
        on_delete=models.CASCADE, 
        related_name="family_details"
    )
    bed_room = models.IntegerField()
    dining_room = models.BooleanField(default=True)
    drawing_room = models.BooleanField(default=True)
    balcony = models.BooleanField(default=False)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()

    class Meta:
        verbose_name = "Family Flat"
        verbose_name_plural = "Family Flats"

    def __str__(self):
        return f"Family Details for {self.flat.title}"


class Bachelor(models.Model):
    flat = models.ForeignKey(
        Flat, 
        on_delete=models.CASCADE, 
        related_name="bachelor_details"
    )
    available_seats = models.CharField(max_length=50)
    dining_charge = models.DecimalField(max_digits=10, decimal_places=2)
    meal_rate_range = models.CharField(max_length=100)
    extra_cost_range = models.CharField(max_length=100)
    expected_total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_members = models.CharField(max_length=50)
    khala_facility = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Bachelor Flat"
        verbose_name_plural = "Bachelor Flats"

    def __str__(self):
        return f"Bachelor Details for {self.flat.title}"


class Shop(models.Model):
    flat = models.ForeignKey(
        Flat, 
        on_delete=models.CASCADE, 
        related_name="shop_details"
    )
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    square_feet = models.IntegerField()
    preaching_space = models.BooleanField(default=True)
    address = models.TextField()

    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return f"Shop Details for {self.flat.title}"