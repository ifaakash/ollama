import tiktoken

enc = tiktoken.get_encoding("o200k_base")

#ids = enc.encode("tiktoken is great!")
ids = enc.encode("where is the cat?")
print(ids)


for i in ids:
  print(enc.decode([i]))
