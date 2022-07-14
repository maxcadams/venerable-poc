import json

x = 5
string = "aye"

p = f"""{{
       "transactions": "{x}",
       "matches": "{string}"
}}"""

print(p)

pjson = json.loads(p)

print(type(p))
print(type(pjson))

print(pjson)