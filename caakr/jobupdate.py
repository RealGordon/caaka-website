from flask import (Blueprint,request,session,abort,g,render_template,redirect)
from caakr.firestoreModel import db #User,get_db
from google.cloud import storage,firestore
import datetime as dt
from flask.globals import current_app
from caakr.settings import CAAKA_LOCAL,JSON_CREDENTIALS
#from google.cloud.exceptions import NotFound
import functools
from werkzeug.utils import secure_filename
#from google.cloud.firestore_v1.field_path import render_field_path
ALLOWED_EXTENSIONS={'doc', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}
bp=Blueprint('job',__name__)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            abort(404)
        return view(**kwargs)

    return wrapped_view


@bp.route('/update/job',methods=('POST',))
@login_required
def writejob():
    msg='job has been written'
    raw_form=request.form
    form={}
    form.update(raw_form)
    form['documents']=raw_form.getlist('documents')
    form['industries']=raw_form.getlist('industries')
    db.collection('jobs').add(form)
    return ' '.join((request.form['employer'],msg))
def allowed_file(filename,category=None):
    ALLOWED_POSTERS={'jpg','png','jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           (ALLOWED_POSTERS if category else ALLOWED_EXTENSIONS) 
def getfile(j_id=None,bucket_name=None,category=None):
    """gets the uploaded CV and other docs AND SAVES IT TO GOOGLE STORAGE"""
    form=request.form
    files=request.files

    #get user id
    user_id=session.get('user_id')
    # Initializing cloud storage bucket
    if not CAAKA_LOCAL:
            storage_client = storage.Client()
            #FLASK SETTING.
    else:
        storage_client=storage.Client.from_service_account_json(
               JSON_CREDENTIALS)
    bucket_name = bucket_name or "cv_filescaakawebsite"
    bucket=storage_client.bucket(bucket_name)
    
    #try:
        #bucket = storage_client.get_bucket(bucket_name)
    #except NotFound:
        #bucket = storage_client.create_bucket(bucket_name)
    
    #checking for allowed file types
    g.failed_files=failed_files=[]
    g.uploaded_files=uploaded_files={}
    for doc_type in files:
        filename=secure_filename(files[doc_type].filename)
        if not allowed_file(filename,category):
            failed_files.append(filename)
    else:
        if failed_files:
            return False
    #uploading the files to cloud storage
    errors=[]
    blob_names=[]
    advertpostid=form.get('advertpostid')
    for doc_type,doc in files.items():
            filename=secure_filename(doc.filename)
            destination_blob_name= 'cand'+dt.datetime.today().isoformat().split(
                '.')[0].replace(':','_')
            blob = bucket.blob(destination_blob_name)
            try:    
                blob.upload_from_file(doc)
            except Exception as e:
                failed_files.append(filename)
                errors.append(str(e))
                break
            metadata={'user_id':str(user_id),"filename":filename}
            if form:
                metadata.update(form.copy())
                metadata.pop('advertpostid',None)
                industry='industries'
                if 'industry' in form:
                    industry='industry'
                if form.get(industry):
                    data=""
                    for i in form.getlist(industry):
                        data+=(i+', ')
                    metadata['industries']=data
                    metadata.pop('industry',None)
                other=form.get("other")
                if other:
                    metadata['industries']=(metadata.get('industries')+other) if metadata.get('industries',False) else other
                    del metadata['other']
                metadata.pop('otherindustry',None)
            if not category:
                for k,v in metadata.items():
                    metadata[k]=str(v)
                blob.metadata = metadata
                blob.patch()
            else:
                #poster
                if '1' in metadata:
                    del metadata['1']
                metadata['info']=[]
                metadata['position']=[]
                for k,v in form.items():
                    if ('position' in k) or ('info' in k):
                        metadata[k[:(len(k)-1)]].append(v.title())
                        del metadata[k]
                metadata.update(blob_name='https://storage.googleapis.com/'+
                                bucket_name+'/'+destination_blob_name,
                                date=dt.date.today().toordinal())
                db.collection(category).add(metadata)
            uploaded_files[doc_type]=filename
            blob_names.append(destination_blob_name)                
            #except Exception as e:
                #failed_files.append(filename) 
##                data={'error':str(e),'time':dt.date.today().toordinal(),
##                      'user':user_id,'type':doc_type,
##                      'filename':filename}
##                if form:
##                    data.update(form)
##                    errors.append(data)
##                    break
    else:
        if category!= 'posters' and uploaded_files:
            if user_id:
                if j_id:
                    db.collection('users').document(user_id).set(
                        {j_id:firestore.ArrayUnion([
                        [k,v] for k,v in uploaded_files.items()])},merge=True)
                else:
                    db.collection('submittedcvs').document(user_id).set(
                        {'uploaded_files':{'filenames':firestore.ArrayUnion(         
                        list(uploaded_files.keys())
                                        ),
                                        'type':firestore.ArrayUnion(
                                          list(uploaded_files.values())),  
                        'blob_names':firestore.ArrayUnion(blob_names)},           
                        'advertpostid':firestore.ArrayUnion([advertpostid]),
                        'forwarded':firestore.ArrayUnion([False])},
                        merge=True)
            else:
                db.collection('submittedcvs').add(
                    {'uploaded_files':{'filenames':firestore.ArrayUnion(         
                        list(uploaded_files.values())
                                        ),
                        'type':firestore.ArrayUnion(
                                list(uploaded_files.values())), 
                     'blob_names':firestore.ArrayUnion(blob_names)},
                     'advertpostid':advertpostid,
                     'forwarded':False})
    #registering errors and successfully uploaded files
    if errors:
        if j_id:
            db.collection('errors').document(user_id).set(
                {j_id:errors},merge=True)
        else:
            db.collection('errors').add({'errors':errors})
        return False
        
    return True

@bp.route('/upload/CV',methods=('POST',))
def uploadCV():
    if getfile():
        return render_template('uploadCVsuccess.html')
    return render_template('uploadCV2.html')

@bp.route('/apply/job/<j_id>',methods=('POST','GET'))
def applyJob(j_id):
    if request.method=='POST':
        if getfile(j_id):
            return render_template('uploadCVsuccess.html')
        else:
            job=db.collection('jobs').document(j_id).get()
            if job.exists:
                job=job.to_dict()
                job['error']="Error ocurred, upload CV again"
            else:
                return redirect('/')
    return render_template('applyCVforjob.html',job=job)

def send_message_json(form):
    "upload message to cloud storage"
    #FLASK SETTING.
    if not CAAKA_LOCAL:
        storage_client = storage.Client()
            
    else:
        storage_client=storage.Client.from_service_account_json(
               JSON_CREDENTIALS)
    from flask import json
    import tempfile
    destination_blob_name = 'mes'+dt.datetime.today().isoformat().split(
            '.')[0].replace(':','_')
    bucket_name = "caakaclientmessages"
    bucket=storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    with tempfile.SpooledTemporaryFile(max_size=1000000,mode="w+t") as fp:
         json.dump(form,fp)
         fp.seek(0)
         blob.upload_from_file(fp)
    form['date']=dt.date.today().toordinal()
    form['blob_name']=destination_blob_name
    form['forwarded']=False
    db.collection('enquiries').add(form)
    return True
    
    
@bp.route('/submit/<doc>',methods=('POST',))
def homepage_cv_submit(doc):
    "submit CV or contact message on homepage"
    if doc=="CV":
        if not getfile():
            abort(404)
        return "success"
    form=request.form.copy()
    if not form:
        return "no data in the form",404
    #data={}
    #for k,v in form.items():
        #data[k]=v  
    if send_message_json(form):
        return "success"
    return "sending message (gcs) failed",500
    
    
        
@bp.route('/admin/submit/poster',methods=('POST',))
@login_required
def submit_poster():
    "submit poster for home page"
    if getfile(bucket_name="caakajobposters",category='posters'):
        return "success"
    else:
        abort(404)
        
    
    
    

