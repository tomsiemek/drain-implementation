from preprocessor_init import regexes
import re

class Preprocessor:
    def __init__(self):
        self.regexes = {}
        for name, regex in regexes.items():
            self.regexes[name] = re.compile(regex)
    def preprocess(self, message: str):
        message_stripped = message.strip()
        tokens = message_stripped.split()
        processed_tokens = []
        for token in tokens:
            new_token = token
            for name, regex in self.regexes.items():
                (new_token, number_of_subs) = regex.subn(name, token)
                if number_of_subs > 0:
                    break
            processed_tokens.append(new_token)
        return processed_tokens
