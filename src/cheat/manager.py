from .. import misc


def main():
    ret = misc.get_choice(
        question="Select your work",
        options=[
            {"desc": "Download new cheatcode", "selector":1}
        ],
        answer="Choice"
    )

    print(ret, type(ret))