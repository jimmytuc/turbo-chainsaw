import hashlib
import re
from urllib.parse import urlparse

def get_domain_from_url(url: str) -> str:
    return urlparse(url).netloc

def clean_tag(text):
	final = []
	for text in text:
		clean_text = re.sub('(\n|\t)*', '', text)
		clean_text = clean_text.strip()
		if(clean_text != ''):
			final.append(clean_text)

	return final

def shorturl(url):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _hex = 0x7FFFFFF & int(str(hashlib.md5(url.encode()).hexdigest()), 16)
    code = ""
    for i in range(9):
        index = 0x0000003D & _hex
        code += chars[index]
        _hex = _hex >> 3
    return code
