import djclick as click
from random import choice, choices
from clowncollege.models import (
    Clown,
    Acrobat,
    Troupe,
    ClownCollege,
    Location,
)
from django.contrib.auth.models import User

@click.command()
def command():
    names = [
        "António",
        "Melo",
        "Angus",
        "Oblong" "Arthur",
        "Vercoe",
        "Pedlar",
        "Barry",
        "Lubin",
        "Bim",
        "Bom",
        "Carequinha",
        "Cepillín",
        "Charlie",
        "Cairoli",
        "Daniel",
        "Rice",
        "David",
        "Shiner",
    ]
    stage_names = [
        "bing",
        "bong",
        "ping",
        "pong",
        "frosty",
        "bozo",
        "flower",
        "rainbow",
    ]
    troupes = ["flying", "dancing", "jumping", "jumpers", "clowning"]
    street = ["funny", "laughing", "amazing", "grandiose"]
    loc_type = ["st", "ave", "blvd", "circle", "drive"]
    for x in range(0, 10):
        t = Troupe.objects.create(name=f"The {choice(troupes)} Troupe")
        for y in range(0, 3):
            username = f"a{x}@b"
            try:
                user = User.objects.create_superuser(username, password='password')
                c = Clown.objects.create(
                    user_id=user.id,
                    first_name=choice(names),
                    last_name=choice(names),
                    stage_name=" ".join(choices(2, stage_names)),
                )
                a = Acrobat.objects.create(
                    user_id=user.id,
                    first_name=choice(names),
                    last_name=choice(names),
                    stage_name=" ".join(choices(2, stage_names)),
                )
                t.clowns.add(c)
                t.acrobats.add(a)
            except:
                user = User.objects.get(username=username)
        loc = Location.objects.create(line_1=" ".join([choice(street), choice(loc_type)]))
        ClownCollege.objects.create(
            name=f"Clown College {x}", troupe_id=t.id, location_id=loc.id
        )
