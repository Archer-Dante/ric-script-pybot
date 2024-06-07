# OLD STUFF
#
# from googletrans import Translator                      # гугл-перевод через API обёртку
# from yandexfreetranslate import YandexFreeTranslate     # яндекс-перевод через фетчинг
# # from deepl import DeepLCLI                            # deepl-перевод через фетчинг ... не работает :(
# from textblob import TextBlob
#
# gt = Translator()
# yt = YandexFreeTranslate(api="ios")
# # print(gt.translate('안녕하세요.'))
# # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
#
# message = "이 문장은 한글로 쓰여졌습니다."
#
# lang = gt.detect(message).lang
# print(lang)
#
#
# print(yt.translate("auto", "en", message))



import translators as ts
from pyaspeller import YandexSpeller

speller = YandexSpeller()


class CodeFlagConverter:
    def __init__(self):
        self.flags = {
            "en": "🇬🇧",
            "ru": "🇷🇺",
            "ua": "🇺🇦",
            "fr": "🇫🇷",
            "de": "🇩🇪",
            "cn": "🇨🇳",
            "br": "🇵🇹",
            "pt": "🇵🇹",
            "pl": "🇵🇱"
        }

    def get_flag(self, country_code):
        return self.flags.get(country_code.lower())

async def translate(message: str, translator: str, lang: str):

    fixed = speller.spelled(message)
    print(fixed)

    response = ts.translate_text(fixed, translator=translator, to_language=lang)

    while "< " in response or " >" in response or "# " in response or " #" in response:
        response = response.replace("< ", "<")
        response = response.replace(" >", ">")
        response = response.replace(" #", "#")
        response = response.replace("# ", "#")

    return response
