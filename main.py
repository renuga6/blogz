from flask import Flask,redirect,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db=SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    created_on = db.Column(db.DateTime)

    def __init__(self,title,body):
        self.title=title
        self.body=body
        self.created_on= datetime.utcnow()

    def is_valid(self):
    
       if self.title and self.body and self.created_on:
            return True
       else:
            return False


@app.route("/")
def index():

    all_records = Entry.query.all() 

    return render_template('all_entry.html',title="Build a Blog",all_entries = all_records)
  

@app.route("/blog")
def disp_blog_entries():
    entry_id = request.args.get('id')
    entry = Entry.query.get(entry_id)
    return render_template('single_entry.html', title="Blog Entry", entry=entry)

@app.route("/new_entry",methods=['POST','GET'])
def new_entry():

    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        entrobj = Entry(title_name,body_name)

        if entrobj.is_valid():
            db.session.add(entrobj)
            db.session.commit()

            return redirect('/')    
        
        else:
            
            return render_template('new_entry.html',title="Create new blog entry",new_entry_title=entrobj.title,
                new_entry_body=entrobj.body,errorvar="Please check your entry for errors. Both a title and a body are required.")
   

    return render_template('new_entry.html',title="Add a Blog")

if __name__ == '__main__':
    app.run()    

