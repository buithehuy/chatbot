from rag.embedder import Embedder

if __name__ == "__main__":
    embedder = Embedder()
    
    v1 = embedder.embed("My favourite food is Pho because its broth is very tasty. I eat Pho every morning")
    print("Độ dài vector:", len(v1)) 
    print("5 số đầu tiên của vector:", v1[:5]) 