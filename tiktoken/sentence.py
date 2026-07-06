from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
docs = ["the cat sat on the mat", "a feline rested on the rug", "I deployed a container"]
query = "where is the cat?"
doc_emb = model.encode(docs)
q_emb = model.encode(query)
print(q_emb)
#scores = util.cos_sim(q_emb, doc_emb)
#print(scores)
