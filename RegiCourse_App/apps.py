from django.apps import AppConfig


class RegicourseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RegiCourse_App'

    def ready(self):
        import RegiCourse_App.signals
