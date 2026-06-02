import subprocess
import urllib.parse
from memory import set_memory, get_memory
def open_brave():
    subprocess.Popen(["brave"])
    return "Brave opened."


def open_terminal():
    subprocess.Popen(["kitty"])
    return "Terminal opened."


def search_web(query):
    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    subprocess.Popen(["brave", url])

    return f"Searched for {query}"

def remember_name(name):
    return set_memory("name", name)


def get_name():
    name = get_memory("name")
    if name:
        return f"Your name is {name}"
    return "I don't know your name yet."

TOOLS = {
    "open_brave": open_brave,
    "open_terminal": open_terminal,
    "search_web": search_web,
    "remember_name": remember_name,
    "get_name": get_name,
}
