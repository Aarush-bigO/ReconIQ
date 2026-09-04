with open("apps/web/app/page.tsx", "r") as f:
    content = f.read()

content = content.replace("client.payment_link.create({<br/>", 'client.payment_link.create({"{"}<br/>')
content = content.replace("})", '{"}"})')

with open("apps/web/app/page.tsx", "w") as f:
    f.write(content)
