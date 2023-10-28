from django.contrib.auth.models import User
from django.db.models.signals import post_save

from oauth_project.models.modelos import Profile


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print('Profile created!')
        user = User.objects.last()
        if user.id == 16:
            user.is_staff = True
            user.save()
            print(user.is_staff)

post_save.connect(create_profile, sender=User)

