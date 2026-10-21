import json, pathlib
from jsonschema import Draft202012Validator, RefResolver

root=pathlib.Path(__file__).parents[1]
p=root/'contracts/schemas/v1'
e=root/'contracts/exemples/v1'
schemas={x.name:json.loads(x.read_text()) for x in p.glob('*.schema.json')}
errs=[]
for fn,d in schemas.items():
 try:
  Draft202012Validator.check_schema(d)
 except Exception as e: errs.append((fn,'schema',str(e)))
for f in sorted(p.glob('*.schema.json')):
 ex=e/(f.name.replace('.schema.json','.json'))
 if not ex.exists(): continue
 inst=json.loads(ex.read_text())
 try:
  v=Draft202012Validator(schemas[f.name],resolver=RefResolver(f.as_uri(),schemas[f.name]))
  ee=list(v.iter_errors(inst))
  if ee: errs.append((f.name,'example',[x.message for x in ee]))
 except Exception as exx: errs.append((f.name,'runtime',str(exx)))
print(f'schemas_checked {len(schemas)} message_pairs {len(list(e.glob("*.json")))}')
if errs:
 print('\\n'.join(map(str,errs))); raise SystemExit(1)
print('all Draft2020-12 schemas valid; all message examples valid; refs resolved')
