import os
import json
from operator import itemgetter 
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate 
from google.oauth2 import service_account
from flask import current_app

load_dotenv()


class TranslateService:
    def __init__(self):
        if os.getenv("GOOGLE_CREDENTIALS"):
            credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            self.translator = translate.Client(credentials=credentials)
        else:
            self.translator = translate.Client()

    def translate_fields(self, data, target_language='pt', desired_fields=["Title", "Description", "Keywords"]):
        """ 
        Recursively Translate the desired fields of a JSON object to the target language.

        Args:
            data (dict): The JSON object to translate.
            target_language (str): The target language to translate to. Default is 'pt'.
            desired_fields (list): The fields to translate. Default is ["Title", "Description", "Keywords"].

        Returns:
            dict: The translated JSON object.
        """
        strings_to_translate = []
        paths = []

        def collect_strings(d, path=[]):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k in desired_fields:
                        collect_strings(v, path + [k])
            elif isinstance(d, list):
                for idx, item in enumerate(d):
                    collect_strings(item, path + [idx])
            elif isinstance(d, str):
                if d.strip():  
                    strings_to_translate.append(d)
                    paths.append(path)

        collect_strings(data)

        if not strings_to_translate:
            return data

        try:
            result = self.translator.translate(strings_to_translate, target_language=target_language)
            translated_texts = [item['translatedText'] for item in result]
        except Exception as e:
            current_app.logger.error(f"Error translating text: {e}")
            return data
            

        #keeps going through the depth of the nested structure and replace the deepest value(str, the base case of the recursive function) with the translated text
        for translated_text, path in zip(translated_texts, paths):
            d = data
            for p in path[:-1]:
                d = d[p]
            d[path[-1]] = translated_text

        return data
        



