#!/usr/bin/env python
# coding: utf-8

# In[684]:


import hashlib
import numpy as np
from random import randint
import mpi4py.MPI as mpi


# In[685]:


class Block :
    
    def __init__(self,blockNumber,nonce,coinbase,transaction,hashPrecedent) : 
        
        self.blockNumber=blockNumber
        self.nonce=nonce
        self.coinbase=coinbase
        self.transaction=transaction
        self.shaSignature=42
        self.hashPrecedent=hashPrecedent
        
    def hashString(self) :
        return(str(self.blockNumber)+str(self.nonce)+self.coinbase.getDataString()+self.transaction.getDataString()+str(self.hashPrecedent))
    
    def incrementNonce(self,i) :
      
        self.nonce+=i
     
    def decrementNonce(self,i) :
      
        self.nonce-=1
        
    
    def _set_shaSignature(self,shaSignature) : 
      
        self.shaSignature=shaSignature
        
    
    def _set_nonce(self,nonce) : 
        
        self.nonce=nonce
    
    
    def __getattr__(self,name) : 
        
        if name == 'blockNumber' :
            return self.blockNumber
        
        if name == 'nonce' :
            return self.nonce
        
        if name == 'coinbase' :
            return self.coinbase
        
        if name == 'transaction' :
            return self.transaction
        
        if name == 'shaSignature' :
            return self.shaSignature
        
        if name == 'hashPrecedent' :
            return self.hashPrecedent

    


# In[686]:


class Transaction : 
    
    def __init__(self,coin,cleFrom,cleTo,n,c) : 
        
        self.coin=coin
        self.cleFrom=cleFrom
        self.cleTo=cleTo
        self.seq=1
        self.signature=signer(str(coin)+str(cleFrom)+str(cleTo),n,c)
        
        
        
        
    
    def _set_seq(self,seq) :
        
        self.seq=seq
        
    
    def _set_signature(self,signature) :
        
        self.signature=signature
        
    
    def getDataString(self) :
    
        data=str(self.coin)+str(self.cleFrom)+str(self.cleTo)
    
        return(data)
    
    
        
    def __getattr__(self,name) : 
        
        if name == 'coin' :
            return self.coin
        
        if name == 'cleFrom' :
            return self.cleFrom
        
        if name == 'cleTo' :
            return self.cleTo
        
        if name == 'seq' :
            return self.seq
        
        if name == 'signature' :
            return self.signature
        
        if name == 'message' : 
            return (str(self.coin)+str(self.cleFrom)+str(self.cleTo))
            
    


# In[687]:


class Coinbase : 
    
    def __init__(self,coin,cleTo) :
        
        self.coin=coin
        self.cleTo=cleTo
        
    def __getattr__(self,name) :
        
        if name == "coin" : 
            return self.coin
        
        if name == "cleTo" : 
            return self.cleTo
        
        
    def getDataString(self) :
    
        data=str(self.coin)+str(self.cleTo)
        
        return(data)
        
        


# In[733]:


def addToBlockchain(Blockchain,coinbase,transaction): 
  
  newBlock=Block(blockNumber=Blockchain[-1].blockNumber+1,nonce=0,coinbase=coinbase,transaction=transaction,hashPrecedent=Blockchain[-1].shaSignature)
  
  minage(newBlock)
  
  Blockchain.append(newBlock)


# In[746]:


def newBlockIntoBlockchain(Blockchain,coinbase,transaction,n,d) : 
    
    if verifier(transaction.signature,transaction.message,n,d)== True :
    
        for block in reversed(Blockchain) : 
        
            if block.transaction.cleFrom==transaction.cleFrom :
                seq=block.transaction.seq
                transaction.seq=seq+1
                break

        addToBlockchain(Blockchain,coinbase,transaction)
    


# In[709]:


def encrypt_string(hash_string):
    sha_signature =         hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


# In[753]:


def minage(block):
    
    rank = mpi.COMM_WORLD.Get_rank()
    size = mpi.COMM_WORLD.Get_size()

    
    hash_string=block.hashString()
    sha_signature=encrypt_string(hash_string)
    block.nonce=rank
    nonce=rank
    
    while not mpi.COMM_WORLD.Iprobe(mpi.ANY_SOURCE, mpi.ANY_TAG):
        if (sha_signature[0]!=str(0) or sha_signature[1]!=str(0) or sha_signature[2]!=str(0) or sha_signature[3]!=str(0))  :  
            hash_string=block.hashString()
            sha_signature=encrypt_string(hash_string)
            block.nonce+=size
            nonce+=size
            
            #print("nonce =",block.nonce,"pour rank =",rank)
        else :
            print("NONCE TROUVÉ pour nonce=",nonce-size,"et sha =",sha_signature)
            for i in range(size) :
                if i!=rank :
                    mpi.COMM_WORLD.send(nonce,dest=i)
            break
        
    nonce-=size
    block.nonce=nonce
    block.shaSignature=sha_signature

def minageSequentielle(block):

    hash_string=block.hashString()
    sha_signature=encrypt_string(hash_string)
    #nonce=block.nonce

    while(sha_signature[0]!=str(0) or sha_signature[1]!=str(0) or sha_signature[2]!=str(0) or sha_signature[3]!=str(0)):
    #while(sha_signature[0]!=str(0)):
        hash_string=block.hashString()
        sha_signature=encrypt_string(hash_string)
        block.nonce+=1
    
    block.nonce-=1
    #block.nonce=nonce
    block.shaSignature=sha_signature
  


# In[711]:


def isprem(n):	#retourne true si un nombre est premier, false sinon
	if n == 1 or n == 2:		
		return True		
	if n%2 == 0:		
		return False		
	r = n**0.5	
	if r == int(r):		
		return False	
	for x in range(3, int(r), 2):
		if n % x == 0:			
			return False		
	return True


# In[712]:


def coupcoup(k, long):	  #decoupage des chaines de caractere
	d , f = 0 , long	
	l = []	
	while f <= len(k):		
		l.append(k[d:f])		
		d , f = f , f + long	
	m = len(k)%long	
	if m != 0:		
		l.append(k[len(k)-m:])	
	return l


# In[713]:


def pgcd(a,b):	#pgcd	
	while (b>0):		
		r=a%b		
		a,b=b,r		
	return a


# In[714]:


def pgcde(a, b):  #pgcd étendu
	r, u, v = a, 1, 0
	rp, up, vp = b, 0, 1
	
	while rp != 0:
		q = r//rp
		rs, us, vs = r, u, v
		r, u, v = rp, up, vp
		rp, up, vp = (rs - q*rp), (us - q*up), (vs - q*vp)
	
	return (r, u, v)


# In[715]:


def key():  #permet de générer des couples privée/publique, utile pour les tests
	#choix au hasard de deux entiers premiers (n et q)
	p = np.random.choice(1000,1)
	q = np.random.choice(1000,1)
	
	while isprem(p) is False:
		p = np.random.choice(1000,1)
		
	while isprem(q) is False:
		q = np.random.choice(1000,1)
		
	#calcul de n et m
	n = p*q
	m = (p-1)*(q-1)
	
	#recherche de c premier de m (c'est a dire tel que pgcd(m,c)=1 ) et de d = pgcde(m,c) tel que 2 < d < m
	r = 10
	d = 0
	while r != 1 or d <= 2 or d >= m:
		c = np.random.choice(1000,1)
		r, d, v = pgcde(c,m)
		
	n, c, d = int(n), int(c), int(d)
	return {"priv":(n,c), "pub":(n,d)}
	


# In[716]:


def chiffre(n, c, msg):  #on chiffre les messages	
	asc = [str(ord(j)) for j in msg]

	for i, k in enumerate(asc):		
		if len(k) < 3:			
			while len(k) < 3:				
				k = '0' + k			
			asc[i] = k

	ascg = ''.join(asc)	
	d , f = 0 , 4
	while len(ascg)%f != 0: 	
		ascg = ascg + '0'
	l = []	
	while f <= len(ascg):		
		l.append(ascg[d:f])		
		d , f = f , f + 4
	crypt = [str(((int(i))**c)%n) for i in l]	
	return crypt
	


# In[717]:


def dechiffre(n, d, *crypt):  #dechiffrement du message, a partir des clés privée
	resultat = [str((int(i)**d)%n) for i in crypt]
	for i, s in enumerate(resultat):
		
		if len(s) < 4:			
			while len(s) < 4:				
				s = '0' + s			
			resultat[i] = s
		
	g = ''.join(resultat)	
	asci = ''	
	d , f = 0 , 3	
	while f < len(g):		
		asci = asci + chr(int(g[d:f]))		
		d , f = f , f + 3
	
	return asci


# In[718]:


def signer(message,n,c):  #retourne la signature
  m=encrypt_string(message)
  signature=chiffre(n,c,m)
  return(signature)


# In[719]:


def verifier (signature,message,n,d):  #renvoi True si la signature est valide, false sinon
  m=encrypt_string(message)
  s=dechiffre(n,d,*signature)
  m=m[:-1]
  if (s==m):
    return(True)
  else:
    return(False)


# In[720]:


print(key())
#{'priv': (n,c), 'pub': (n,d)


# In[721]:


m="salut c'est moi aurelien bonjour clement"
s=signer(m,290363, 983)
print(s)


# In[722]:


verifier(s,m,290363, 18527)


# In[754]:


n=83749
c=427
d=14723

transaction1=Transaction(coin=16,cleFrom="17ruevauquelin",cleTo="55boulevardstmarcel",n=n,c=c)
transaction2=Transaction(coin=24,cleFrom=transaction1.cleFrom,cleTo=transaction1.cleTo,n=n,c=c)

coinbase1=Coinbase(coin=76,cleTo="17ruevauquelin")
coinbase2=Coinbase(coin=24,cleTo="17ruevauquelin")

transaction1.signature=signer(transaction1.message,n,c)
transaction2.signature=signer(transaction2.message,n,c)

print(transaction1.seq)

Blockchain=[]
premierBlock=Block(blockNumber=1,nonce=0,coinbase=coinbase1,transaction=transaction1,hashPrecedent="0000000000000000000000000000000000000000000000000000000000000000")





Blockchain.append(premierBlock)



hashString=Blockchain[0].hashString()

print("\n")
print(hashString)
print(Blockchain[0].shaSignature)
minage(Blockchain[0])
print("Nonce =",Blockchain[0].nonce)
print(Blockchain[0].shaSignature)

print("\n")

print(verifier(signer(transaction2.message,n,c),transaction2.message,n,d))


newBlockIntoBlockchain(Blockchain,coinbase2,transaction2,n,d)
print(Blockchain[0].nonce)
print(Blockchain[1].nonce)
print(Blockchain[1].shaSignature)




# In[ ]:





# In[ ]:





# In[ ]:




