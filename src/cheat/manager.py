from .. import misc


def main():
    ret = misc.get_choice(
        question="Select your work",
        options=[
            {"desc": "Update Title ID", "selector":1, "return":"update-title-id"},
            {"desc": "Update cheatcode database", "selector":2, "return":"update-cheatcode-db"}
        ]
    )

    print(ret, type(ret))