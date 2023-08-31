from talesofvalor.characters import models


def character_settings(request):
    return {
        'POINT_CAP': models.POINT_CAP,
    }