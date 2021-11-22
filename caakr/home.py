from flask import (Blueprint,render_template,g,session,abort,redirect)
from flask.globals import current_app
from caakr.settings import CAAKA_LOCAL
from caakr.firestoreModel import db
import datetime as dt
#from caakr.jobupdate import getfile
#from caakr.auth import login_required
bp=Blueprint('home',__name__)
@bp.route('/home/indexdata')
def index():
    dline=dt.date.today() 
    c_r=db.collection('jobs')
    d=[]
    posts="No post available"
    status=False
    d_s=c_r.where('deadline','>',dline.toordinal()).limit(7).stream()
    for doc in d_s:
        d.append(doc)
    else:
        if not d:
            d_s=c_r.where('deadline','<',dline.toordinal()).limit(7).stream()
            for doc in d_s:
                d.append(doc)
        g.data=d
        g.deadline=dline
    if d:
        posts=render_template('jobposts.html')
        status=True
    data=dict(menu='fail',post=posts,poststatus=status,pos=session.get('pos'))
    if session.get('user_id'):
        name=session.get('name')
        if session.get('pos')=='staff':
            menu="""<button class="w3-bar-item w3-button"  href="#">{}</button>
<a class="w3-bar-item w3-button" href="#">Check CVs</a>
  <a class="w3-bar-item w3-button" target="_blank" href="/static/jobupdate">Add Job</a>
  """.format(name)
        else:
            menu="""<button class="w3-bar-item w3-button"  href="#">{}</button>
<a class="w3-bar-item w3-button"  href="/static/uploadCV" target="_blank">Submit CV</button>""".format(name)
        logout='<a class="w3-bar-item w3-button" href="/logout">logout</a>'
        menu += logout
        data['menu']=menu
            
    return data


@bp.route('/home/get/poster')
def get_poster():
    d_s=db.collection('posters').order_by(
        'date',direction='DESCENDING').limit(1).stream()
    for doc in d_s:
        data=doc.to_dict()
        delta=dt.date.fromordinal(data['date']).isoformat()
        data['date']=delta
        return data
    abort(404)



#flask homepage
if CAAKA_LOCAL:
    @bp.route('/')
    def flask_home():
        with current_app.open_resource('../www/index.html') as f:
            data=f.read()
        return data
    @bp.route('/favicon.ico')
    def flask_favicon():
        return redirect('/static/favicon.ico')

        
    
    
    
        
