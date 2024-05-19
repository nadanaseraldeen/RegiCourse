
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def add_superuser_to_admin_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        admin_group, created = Group.objects.get_or_create(name='admin')
        admin_group.user_set.add(instance)
