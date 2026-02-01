
from rest_framework.exceptions import ValidationError


class VideoLinkValidator():

    def __init__(self, field=None):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)

        if not value:
            return

        youtube_domain = "youtube.com"
        if youtube_domain not in value.lower():
            raise ValidationError("Недопустимый формат ссылки")