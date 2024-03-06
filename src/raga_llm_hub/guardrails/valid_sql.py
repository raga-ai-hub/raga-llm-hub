import sqlvalidator


class ValidSql:
    """
    Checks whether provided sql query is correct or not.
    """

    def __init__(
        self,
        prompt,
    ):
        """
        Initializes the ValidSql class.

        Args:
        - prompt: str, the text to be evaluated for nsfw.
        """
        self.prompt = prompt

    def run(self):
        sql_query = sqlvalidator.parse(self.prompt)
        res = ""
        if not sql_query.is_valid():
            res = False
        else:
            res = True

        result = {"prompt": self.prompt, "is_passed": res}

        return result
