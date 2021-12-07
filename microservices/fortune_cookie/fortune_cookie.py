#!/usr/bin/env python3

"""
Dragon Cafe Fortune Cookie Microservice | Author: Sam Griffith | Org: Alta3 Research Inc.

This Fortune Cookie Microservice is the third part of the monolithic application of a Chinese Restaurant website that has been broken out into it's own service.
"""

# Standard Library Imports
import json
import os
from pathlib import Path
import random
import socket

# 3rd Party Packages
from aiohttp import web
import jinja2
import requests

# Environmental Variables
HOST = os.getenv("FORTUNE_HOST", "0.0.0.0")
LOCAL_IP = socket.gethostbyname(socket.gethostname())
PORT = os.getenv("FTN_PORT", 2229)
REG_ADDR = os.getenv("SR_ADDRESS", "127.0.0.1")
REG_PORT = os.getenv("SR_PORT", 55555)
SERVICE = os.path.basename(__file__).rstrip(".py")


# Establish a new object type, called a Page
class Page:
    def __init__(self, filename, templates_dir=Path("templates"), args={}, cookies={}):
        """
        Create a new instance of an html page to be returned
        :param filename: name of file found in the templates_dir
        """
        self.path = templates_dir
        self.file = templates_dir / filename
        self.args = args
        self.cookies = cookies

    def render(self):
        """ Template in a Jinja2 formatted HTML file and return a web.Response"""
        with open(self.file) as f:
            txt = f.read()
            print(f"Templating in {self.args}")
            # Fill in the template file with any args provided
            j2 = jinja2.Template(txt).render(self.args)
            # Create a response object
            resp = web.Response(text=j2, content_type='text/html')
            # Add any cookies passed to this page as cookies in the response
            for c, j in self.cookies:
                resp.set_cookie(c, j)
            # feed back the web.Response object with the filled out page
            return resp


def routes(app: web.Application) -> None:
    """
    Add paths as available routes and specify which function gets called
    when a path is requested.
    """
    app.add_routes(
        [
            # web.get == HTTP GET
            web.get("/", fortune_cookie),
            web.get("/fortune_cookie", fortune_cookie),
            web.get("/fortune_cookie/fortune", fortune),
            web.get("/fortune", fortune),
        ]
    )


async def fortune_cookie(request) -> web.Response:
    """
    This is the initial landing page for the fortune_cookie service.

    Click on the link provided to retrieve your fortune!
    """
    print(request)
    # Create a page from the fortune_cookie.html template
    page = Page(filename="fortune_cookie.html")
    # Render and return the page
    return page.render()


async def fortune(request) -> web.Response:
    """
    This returns a randomly picked aphorism as a part of the fortune_cookie service.
    """
    print(request)
    # Long list of possible amorphisms (fortunes)
    possible = [
        "People are naturally attracted to you.",
        "You learn from your mistakes... You will learn a lot today.",
        "If you have something good in your life, don't let it go!",
        "What ever you're goal is in life, embrace it visualize it, and for it will be yours.",
        "Your shoes will make you happy today.",
        "You cannot love life until you live the life you love.",
        "Be on the lookout for coming events; They cast their shadows beforehand.",
        "Land is always on the mind of a flying bird.",
        "The man or woman you desire feels the same about you.",
        "Meeting adversity well is the source of your strength.",
        "A dream you have will come true.",
        "Our deeds determine us, as much as we determine our deeds.",
        "Never give up. You're not a failure if you don't give up.",
        "You will become great if you believe in yourself.",
        "There is no greater pleasure than seeing your loved ones prosper.",
        "You will marry your lover.",
        "A very attractive person has a message for you.",
        "You already know the answer to the questions lingering inside your head.",
        "It is now, and in this world, that we must live.",
        "You must try, or hate yourself for not trying.",
        "You can make your own happiness.",
        "The greatest risk is not taking one.",
        "The love of your life is stepping into your planet this summer.",
        "Love can last a lifetime, if you want it to.",
        "Adversity is the parent of virtue.",
        "Serious trouble will bypass you.",
        "A short stranger will soon enter your life with blessings to share.",
        "Now is the time to try something new.",
        "Wealth awaits you very soon.",
        "If you feel you are right, stand firmly by your convictions.",
        "If winter comes, can spring be far behind?",
        "Keep your eye out for someone special.",
        "You are very talented in many ways.",
        "A stranger, is a friend you have not spoken to yet.",
        "A new voyage will fill your life with untold memories.",
        "You will travel to many exotic places in your lifetime.",
        "Your ability for accomplishment will follow with success.",
        "Nothing astonishes men so much as common sense and plain dealing.",
        "Its amazing how much good you can do if you do not care who gets the credit.",
        "Everyone agrees. You are the best.",
        "Life consist not in holding good cards, but in playing those you hold well.",
        "Jealousy doesn't open doors, it closes them!",
        "It's better to be alone sometimes.",
        "When fear hurts you, conquer it and defeat it!",
        "Let the deeds speak.",
        "You will be called in to fulfill a position of high honor and responsibility.",
        "The man on the top of the mountain did not fall there.",
        "You will conquer obstacles to achieve success.",
        "Joys are often the shadows, cast by sorrows.",
        "Fortune favors the brave.",
    ]
    # Select one of the fortunes at random
    fortune_choice = random.choice(possible)
    # Set a key-value pair to pass as args into the template
    args = {"fortune": fortune_choice}
    # Create a page from the fortune.html template
    page = Page(filename="fortune.html", args=args)
    # Render and return the page
    return page.render()


async def register(add_to_registry=True):
    """ Send an HTTP GET to the Service Registry /add path with service info """
    # debug info
    print(f"""
    Service Registry {REG_ADDR}:{REG_PORT}

    Adding to the Service Registry:

    service name     {SERVICE}
    service IP       {LOCAL_IP}
    service port     {PORT}
    """)
    # A parameter is needed for the async call on this function. So we might as well use it!
    if add_to_registry:
        r = requests.get(f"http://{REG_ADDR}:{REG_PORT}/add/{SERVICE}/{LOCAL_IP}/{PORT}")
        print(r.status_code, r.text)


async def unregister(remove_from_registry=True):
    """
    Send an HTTP GET to the Service Registry /remove path with service info """
    if remove_from_registry:
        r = requests.get(f"http://{REG_ADDR}:{REG_PORT}/remove/{SERVICE}/{LOCAL_IP}/{PORT}")
        print(r.status_code)


def main():
    """
    This is the main process for the aiohttp server.

    This works by instantiating the app as a web.Application(),
    then applying the setup function we built in our routes
    function to add routes to our app, then by starting the async
    event loop with web.run_app().
    """

    print("This aiohttp web server is starting up!")
    # Create a web.Application object
    app = web.Application()
    # Add the available routes to our web application
    routes(app)
    # Have the register function be scheduled to run prior to the webserver being initiated
    app.on_startup.append(register)
    # Have the unregister function be scheduled to run as the webserver is being shutdown
    app.on_shutdown.append(unregister)
    # Start the webserver
    web.run_app(app, host=HOST, port=PORT)


# Only run the main() function if this script gets called directly from CLI
if __name__ == "__main__":
    main()
