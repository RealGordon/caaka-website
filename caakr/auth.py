from flask import (Blueprint,request,render_template,abort,
                    session,g,redirect,url_for,make_response,
                   get_flashed_messages)

from functools import wraps
from caakr.firestoreModel import User
auth=Blueprint('auth',__name__)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            return redirect('/login/user?url='+request.url)
        return view(**kwargs)

    return wrapped_view



@auth.route('/login/user',methods=("POST",'GET'))
def login():
    t=session.get('logintrial',None)
    #if t:
        #if int(t)>15:
            #abort(404)
    user=User()
    #logging in with session
    user_id=session.get('user_id',None)
    if request.args.get('session'):
        if user_id:
            user.getdbUser(user_id)
            return {'status':"success",'name':user.name}
        else:
            return {'status':"failure"}
            
    data=request.form
    formtype=data.get('formtype')     
    if formtype=="login":
        if data['email'] and data['pwd']:
            user.getSiteUser(data['email'],data['pwd'],data['meth'])
            

    elif formtype=="signup":
        user.createUser(data)
            
    if user.user_id:
        for k in ['user_id','pos','name']:
            session.setdefault(k,user.__dict__[k])
        if data.get('url'):
            return redirect(data.get('url'))
                
        return "success"

    else:
        g.setdefault('error',user.errors.get('account',None))
        t=session.get('logintrial',None)
        if t:
            session['logintrial']=str(int(t)+1)
        else:
            session['logintrial']=str(1)
        for v in user.errors.values():
            msg=v
        return msg
    return render_template('login.html',url=request.args.get('url'),
                           nonevalue=None)
                

        
@auth.route('/fsg77141.txt')
def sitecrawler():
    resp=make_response("   ")
    resp.mimetype = 'text/plain'
    return resp

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logintrial',None)
    session.pop('pos',None)
    return redirect('/')
    
