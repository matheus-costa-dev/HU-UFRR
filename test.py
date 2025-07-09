file_name = "token.json"

with open(file_name) as f:
  text = f.read()

print(text)

print("finalizado")

with open("test.txt", "w") as f:
  f.write(text)
