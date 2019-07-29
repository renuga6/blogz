from flask import Flask,redirect,render_template,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db=SQLAlchemy(app)
app.secret_key='mira'

class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    owner_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime)

    def __init__(self,title,body,owner):

        self.title=title
        self.body=body
        self.owner=owner
        self.created_on= datetime.utcnow()

    def is_valid(self):
    
       if self.title and self.body and self.created_on:
            return True
       else:
            return False


class User(db.Model):

    id = db.Column(db.Integer,primary_key=True)   
    email = db.Column(db.String(120),unique=True) 
    password = db.Column(db.String(120)) 
    blogentries = db.relationship('Entry',backref='owner')

    def __init__(self,email,password):
        self.email = email
        self.password = password  


@app.before_request        
def require_login(): 

    allowed_routes=['login','signup','index','userblog','allblog','disp_blog_entries'] 
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')     


@app.route("/login",methods=['POST','GET'])
def login():

    if request.method == 'POST':
       username=request.form['username'] 
       password=request.form['password']
       user =User.query.filter_by(email=username).first()
       if user and user.password == password:
           session['email'] = username
           return redirect('/blog')
       else:
            return '<h1> Error </h1>'
    return render_template('login.html')


@app.route("/signup",methods=['POST','GET'])
def signup():

    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == 'POST':
       username=request.form['username']
       password=request.form['password']
       verify=request.form['verify']

       existing_user=User.query.filter_by(email=username).first()
       if len(username) < 3:
            username_error = "Usernames must be longer than 3 characters."
            if username == "":
                username_error = "Please enter a desired username."
        
       if  len(password) < 3:
            password_error = "Password must be longer than 3 characters."
            if password == "":
                password_error = "Please enter a valid password."

       if password != verify:
           verify_error = "Passwords must match."         
          
       if not username_error and not password_error and not verify_error:   
            if not existing_user:
                new_user=User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = username
                return redirect('/')
            else:
                username_error = "Username already exist"  
    return render_template('signup.html',username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)


@app.route("/")
def index():

    all_records = User.query.all() 
    return render_template('index.html',title="Build a Blog",users = all_records)

@app.route("/userblog")  
def userblog():
    user_id = request.args.get('userid')
    owner=User.query.filter_by(id = user_id).first()
    all_records = Entry.query.filter_by(owner=owner).all() 
    return render_template('all_entry.html',title="Build a Blog",all_entries = all_records)

@app.route("/allblog")  
def allblog():
    
    all_records = Entry.query.all() 
    return render_template('all_entry.html',title="Build a Blog",all_entries = all_records)


@app.route("/blog")
def disp_blog_entries():

    entry_id = request.args.get('id')
    if entry_id is None:
        owner=User.query.filter_by(email=session['email']).first() 
        all_records = Entry.query.filter_by(owner=owner).all() 
        return render_template('all_entry.html',title="Build a Blog",all_entries = all_records)
    else:
        entry = Entry.query.get(entry_id)
        return render_template('single_entry.html', title="Blog Entry", entry=entry)


@app.route("/new_entry",methods=['POST','GET'])
def new_entry():


    owner=User.query.filter_by(email=session['email']).first()    
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        
        entrobj = Entry(title_name,body_name,owner)

        if entrobj.is_valid():
            db.session.add(entrobj)
            db.session.commit()

            return redirect('/blog?id='+str(entrobj.id))    
        else:
            
            return render_template('new_entry.html',title="Create new blog entry",new_entry_title=entrobj.title,
                new_entry_body=entrobj.body,errorvar="Please check your entry for errors. Both a title and a body are required.")
   
    return render_template('new_entry.html',title="Add a Blog")


@app.route('/logout')
def logout():

    del session['email']
    return redirect('/')


if __name__ == '__main__':
    app.run()    

