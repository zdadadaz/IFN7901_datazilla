### Example inspired by Tutorial at https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
### However the actual example uses sqlalchemy which uses Object Relational Mapper, which are not covered in this course. I have instead used natural sQL queries for this demo. 

from flask import Flask, render_template, url_for, flash, redirect,request
from forms import RegistrationForm, BlogForm
import sqlite3
import shlex, subprocess
import pandas as pd
import mysql.connector
import random

conn = sqlite3.connect('blog.db')
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

config = {
  'user': 'root',
  'password': 'root',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': 'Anki',
  'raise_on_warnings': True,
}
# conn = mysql.connector.connect(**config)

def addcomma(input):
    return "'"+input+"'"

#Turn the results from the database into a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        conn = mysql.connector.connect(**config)
        c= conn.cursor()
        vName= request.form.get('vName')
        vSeason=request.form.get('vSeason')
        vEpisode=request.form.get('vEpisode')
        if (vName is not None) and (vSeason is not None) and (vEpisode is not None):
            c.execute("SELECT vid FROM Video where vname=%s and season =%s and episode=%s " % (addcomma(vName),addcomma(vSeason),addcomma(vEpisode)) )
            vidExist = c.fetchall()
            
        upfile = request.files.get('file')
        print("print vid=============vidExist===================",vidExist)
        print(not len(vidExist))
        if (upfile is not None) and len(vidExist):
            df = pd.read_excel(upfile) 
            dflen = len(df.columns)
            if dflen==4:
                subset = df[['sstime', 'sftime', 'tran','org']]
                query_insert = "insert into Subtitle(sstime,sftime,translation,org,vid) VALUES ("
            elif dflen==3:
                subset = df[['sstime', 'sftime', 'org']]
                query_insert = "insert into Subtitle(sstime,sftime,org,vid) VALUES ("
            tuples = [tuple(x) for x in subset.values]
            for i in range(len(tuples)):
                elementstr = addcomma(str(tuples[i][0]))
                for j in range(1,dflen):
                    elementstr = ' '.join([elementstr, ",", addcomma(str(tuples[i][j]).replace("'","''"))])
                query = query_insert +  elementstr +","+addcomma(str(vidExist[0][0])) +')'
                # print('query->',query)
                c.execute(query)
                conn.commit()
        else:
            print("no valid vid================================")
        return render_template('upload.html')
    return render_template('upload.html')

@app.route("/")
@app.route("/home")
def home():
    conn = sqlite3.connect('blog.db')

    #Display all blogs from the 'blogs' table
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM blogs")
    posts = c.fetchall()
    return render_template('home.html', posts=posts)

@app.route("/audio",methods=['GET', 'POST'])
def playmp3():
    if request.method == 'POST':
        conn = mysql.connector.connect(**config)
        c= conn.cursor()
        c.execute("SELECT count(*) FROM Subtitle")
        totnum = c.fetchone()
        # print(totnum[0])
        randnum = int(random.random()*(totnum[0]-1))
        # print(randnum)

        low = randnum-1 if (randnum-1 >0) else 1
        high = randnum if (randnum <totnum[0]) else totnum[0]
        c.execute("SELECT * FROM Subtitle where sid>%s and sid <= %s " % (addcomma(str(low)),addcomma(str(high))) )
        clip = c.fetchall()
        print(clip)
        stime = clip[0][1]
        ftime= clip[len(clip)-1][2]
        durtime = ftime-stime
        print("------------------------------------")
        print(stime,ftime, ftime-stime)
        command_line="ffplay -ss " + str(stime) +" -t " + str(durtime) +" -autoexit ./static/data/Bigbang_s08e01.mp3"
        # command_line="ffplay -ss 00:01:03 -t 00:00:03 -autoexit ./static/data/Bigbang_s08e01.mp3"
        args = shlex.split(command_line)
        p = subprocess.Popen(args)
    return render_template('playmp3.html')
    

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        
        #Add the new blog into the 'blogs' table
        query = 'insert into users VALUES (' + "'" + form.username.data + "',"  + "'" + form.email.data + "'," + "'" + form.password.data + "'" + ')' #Build the query
        c.execute(query) #Execute the query
        conn.commit() #Commit the changes

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/blog", methods=['GET', 'POST'])
def blog():
    conn = sqlite3.connect('blog.db')

    #Display all usernames stored in 'users' in the Username field
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    results = c.fetchall()
    users = [(results.index(item), item) for item in results]

    form = BlogForm()
    form.username.choices = users

    if form.validate_on_submit():
        choices = form.username.choices
        user =  (choices[form.username.data][1])
        title = form.title.data
        content = form.content.data

        #Add the new blog into the 'blogs' table in the database
        query = 'insert into blogs (username, title, content) VALUES ('  + "'" + user + "',"  + "'" + title + "'," + "'" + content + "'"+ ')' #Build the query
        c.execute(query) #Execute the query
        conn.commit() #Commit the changes

        flash(f'Blog created for {user}!', 'success')
        return redirect(url_for('home'))
    return render_template('blog.html', title='Blog', form=form)

if __name__ == '__main__':
    app.run(debug=True)

