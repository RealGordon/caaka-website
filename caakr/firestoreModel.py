from flask.globals import current_app
from google.cloud.firestore_v1.field_path import render_field_path
from google.cloud import firestore
import datetime as dt
from caakr.settings import CAAKA_LOCAL,JSON_CREDENTIALS
from werkzeug.security import generate_password_hash,check_password_hash

if CAAKA_LOCAL:
    #from firebase_admin import  firestore ,initialize_app,credentials
    #firebase_credentials_file_path = JSON_CREDENTIALS
    #cred = credentials.Certificate(firebase_credentials_file_path)
    #initialize_app(cred)
    #db = firestore.Client(project='trial-datastore-native-92696')
    db=firestore.Client.from_service_account_json(JSON_CREDENTIALS)
    #import grpc
    #from google.cloud.firestore_v1.gapic import firestore_client
    #from google.cloud.firestore_v1.gapic.transports import firestore_grpc_transport
    #channel = grpc.insecure_channel("localhost:8080")
    #transport = firestore_grpc_transport.FirestoreGrpcTransport(channel=channel)
    #db._firestore_api_internal = firestore_client.FirestoreClient(transport=transport)
else:
    db=firestore.Client()


class User:
    def __init__(self,name=None,email=None,ref=None):
        self.name=name
        self.email=email
        self.doc_ref=ref
        self.errors={}
        self.user_id=None
        self.labels=['name','phone','email','birthdate','school','pos']
    def createUser(self,data):
        s=db.collection('users').where('email','==',data['email']).stream()
        for doc in s:
            if doc.exists:
                self.errors['account']='Account already exits'
                return None
        else:
            d={}
            for i in ['pwdrepeat','formtype']:
                data.pop(i,None)
            for k,v in data.items():
                if v:
                    if k=='pwd':
                        v=generate_password_hash(v)
                    elif k=='birthdate':
                        v=dt.date.fromisoformat(v).toordinal()
                    d.update({k:v})
            d.update(dj=dt.date.today().isoformat(),pos='user')
            self.doc_ref=db.collection('users').add(d)[1]
            self.user_id=self.doc_ref.id
            self.pos='staff'
            self.name=data['name']
            #self.updateUserSex(data['sex'])
            #for i in ['email','phone']:
                #if i not in d:
                    #d[i]=''                            
            #db.collection('users').document('new_users').set({
                #'u':firestore.ArrayUnion([d.email]),
                #'n':firestore.ArrayUnion([d.name]),
                #'p':firestore.ArrayUnion([d.phone])},True)
    @staticmethod        
    def updateUserSex(sex="M",m=None):
        if not m:
            m='sex'
            doc_ref=db.collection('statistics').document(m)
            if sex=="M" or sex=="F":
                doc_ref.update({render_field_path([
                'users',str(dt.date.today().year),sex]):firestore.Increment(1)})        
    def getdbUser(self,user_id):
        """   (user_id)
        get a user from db using session id"""     
        d=db.collection('users').document(user_id).get(self.labels)
        if d.exists:
            self.__dict__.update(d.to_dict())
            self.doc_ref=d.reference
            self.user_id=user_id
        else:
            s=db.collection('users').where('user_id','==',user_id).select(
                self.labels[:]).limit(1).stream()
            for doc in s:
                self.doc_ref=doc.reference
                self.__dict__.update(doc.to_dict())
                self.user_id=user_id
                return True
            else:
                return None
        return True
      
    def getSiteUser(self,email,pwd,e):
        l=self.labels[:]
        l.append('pwd')
        if e=="e":
            s=db.collection("users").where('email','==',email).select(
                l).stream()
        else:
            s=db.collection("users").where('phone','==',email).select(
                l).stream()
        for doc in s:
            if doc.exists:
                if check_password_hash(doc.get('pwd'),pwd):
                    self.doc_ref=doc.reference
                    self.user_id=doc.id
                    self.__dict__.update(doc.to_dict())
                    self.__dict__.pop('pwd',None) 
                else:
                    self.errors.update(password='wrong password')
                return True
                    
        
        else:
            self.errors.update(account='account does not exist')
            return False     
        
