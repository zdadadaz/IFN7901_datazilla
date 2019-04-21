### Example inspired by Tutorial at https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
### However the actual example uses sqlalchemy which uses Object Relational Mapper, which are not covered in this course. I have instead used natural sQL queries for this demo. 

from flask import Flask, render_template, url_for, flash, redirect ,request
from forms import RegistrationForm, BlogForm
import datetime
import mysql.connector
from util import json_io
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


config = {
  'user': 'root',
  'password': 'root',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': '7901',
  'raise_on_warnings': True,
}

conn = mysql.connector.connect(**config)
userio = json_io()
currentUser=0

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        currentUser=userio.read()
        if currentUser == 0:
            return redirect(url_for('login_tmp', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#Turn the results from the database into a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# @app.route("/")
# @app.route("/home")
# def home():
#     conn = sqlite3.connect('blog.db')

#     #Display all blogs from the 'blogs' table
#     conn.row_factory = dict_factory
#     c = conn.cursor()
#     c.execute("SELECT * FROM blogs")
#     posts = c.fetchall()
#     return render_template('home.html', posts=posts)


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


# @app.route("/blog", methods=['GET', 'POST'])
# def blog():
#     conn = sqlite3.connect('blog.db')

#     #Display all usernames stored in 'users' in the Username field
#     conn.row_factory = lambda cursor, row: row[0]
#     c = conn.cursor()
#     c.execute("SELECT username FROM users")
#     results = c.fetchall()
#     users = [(results.index(item), item) for item in results]

#     form = BlogForm()
#     form.username.choices = users

#     if form.validate_on_submit():
#         choices = form.username.choices
#         user =  (choices[form.username.data][1])
#         title = form.title.data
#         content = form.content.data

#         #Add the new blog into the 'blogs' table in the database
#         query = 'insert into blogs (username, title, content) VALUES ('  + "'" + user + "',"  + "'" + title + "'," + "'" + content + "'"+ ')' #Build the query
#         c.execute(query) #Execute the query
#         conn.commit() #Commit the changes

#         flash(f'Blog created for {user}!', 'success')
#         return redirect(url_for('home'))
#     return render_template('blog.html', title='Blog', form=form)


@app.route("/", methods=['GET'])
def landing():
    return render_template('landing.html');

@app.route("/login", methods=['GET','POST'])
def login_tmp():
    if request.method == 'POST':
        gCurrentUser={}
        gCurrentUser['currentUser']=request.form.get("userId")
        userio.save_userid(gCurrentUser)
        return redirect(url_for('Posts'))        
    return render_template('login.html');


@app.route("/Posts",methods=['GET', 'POST'])
def Posts():
    if request.method == 'GET':
        # conn = sqlite3.connect('car.db')

        conn = mysql.connector.connect(**config)
        #Display all blogs from the 'blogs' table
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM Post")
        posts = c.fetchall()
        # print(posts[7][13])
        return render_template('Posts.html', posts=posts)
    else:
        conn = mysql.connector.connect(**config)
        carType = (request.form.get("carType"))
        price = (request.form.get("price"))
        brand = (request.form.get("brand"))
        manuYear = (request.form.get("manuYear"))
        location = (request.form.get("location"))
        stars = (request.form.get("stars"))
        # #Display all blogs from the 'blogs' table
        
        cond = 'WHERE '
        count = 0
        if (not (carType is None)):
            count = count+1
            cond=cond + "LOWER(Car_type) LIKE '%"+ carType.lower() +"%'"
        if (not (brand is None)):
            if(count>0):
                cond += " AND "
            count = count+1
            cond=cond + "LOWER(Brand) LIKE '%"+ brand.lower() +"%'"
        if (not (location is None)):
            if(count>0):
                cond += " AND "
            count = count+1
            cond=cond + "LOWER(Location) LIKE '%"+ location.lower() +"%'"
        if (not (stars is None)):
            if(count>0):
                cond += " AND "
            count = count+1
            cond=cond + "Stars = '"+ stars[1]+"'"
        if (not (price is None)):
            if(count>0):
                cond += " AND "
            count = count+1
            if(price=="p0"):
                cond=cond + "Price < 2000" 
            elif(price=="p2"):
                cond=cond + "Price < 4000 AND Price>= 2000" 
            elif(price=="p4"):
                cond=cond + "Price < 6000 AND Price>= 4000" 
            elif(price=="p6"):
                cond=cond + "Price >= 6000"
        if (not (manuYear is None)):
            if(count>0):
                cond += " AND "
            count = count+1
            if(manuYear=="y1"):
                cond=cond + "manu_year like '19%'" 
            elif(manuYear=="y2"):
                cond=cond + "manu_year like '200%'" 
            elif(manuYear=="y3"):
                cond=cond + "manu_year like '201%'" 
           
        # print(cond)
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM Post " + cond)
        posts = c.fetchall()
        return render_template('Posts.html', posts=posts)
#get /Posts/<name> data: {name :}
@app.route('/Posts/<string:name>')
def get_post(name):
    currentUser=userio.read()
    conn = mysql.connector.connect(**config)
    #Display all blogs from the 'blogs' table
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT P.*,U.First_name, U.Last_name FROM Post P,Seller S,User U WHERE P.Uid=S.Uid AND S.Uid=U.Uid AND P.Postid="+name)
    post = c.fetchone()
    return render_template('show.html',post=post, currentUser=currentUser)

@app.route('/Posts/<string:name>/edit', methods=['GET', 'POST'])
def edit_post(name):
    currentUser=userio.read()
    conn = mysql.connector.connect(**config)
    #Display all usernames stored in 'users' in the Username field
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    if (request.method == 'POST'):
        form = CarInfoForm(request.form)
        # user
        c.execute("SELECT Uid,First_name,Last_name FROM User WHERE Uid="+str(currentUser))
        results = c.fetchall()
        users = [(results.index(item), item) for item in results]
        form.username.choices = users
        # specialist
        c.execute("SELECT * FROM Specialist")
        specialist_res = c.fetchall()
        specialist = [(specialist_res.index(item), item) for item in specialist_res]
        form.specialist.choices = specialist
        form.stars.choices = ((0,(1)),(1,(2)),(2,(3)))
        
        if(form.validate_on_submit()):
            specialist = form.specialist.choices[form.specialist.data][1]
            stars = form.stars.choices[form.stars.data][1]
            user =  users[form.username.data][1]
            title = form.title.data
            content = form.content.data
            location= form.location.data
            color   = form.color.data
            carType =form.carType.data
            brand  = form.brand.data
            price  = form.price.data
            manuYear = form.manuYear.data
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
            # Add the new Post into the 'blogs' table in the database
            title = title.replace("'","''")
            content = content.replace("'","''")
            query = 'UPDATE Post SET Date_post='+"'"+timestamp+"'" +',Title='+"'" +title+"'" +',Description='+"'" +content+"'" +',Location='+"'" +location+"'" +',Color='+"'" +color+"'" +',Car_type='+"'" +carType+"'" +',Brand='+"'" +brand+"'" +',Price='+str(price)+',manu_year='+str(manuYear)+',Sid='+str(specialist[0])+',Stars='+str(stars) +' WHERE Postid='+str(name)
            c.execute(query) #Execute the query
            conn.commit() #Commit the changes

            flash(f'Post edited for {user}!', 'success')
            return redirect(url_for('Posts'))
        return render_template('edit.html',title='Blog', form=form)    
        
    elif request.method == 'GET':
        form = CarInfoForm()
        c.execute("SELECT Uid,First_name,Last_name FROM User WHERE Uid="+str(currentUser))
        results = c.fetchall()
        users = [(results.index(item), item) for item in results]
        
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT u.Uid,u.First_name,u.Last_name,p.* FROM Seller s,User u,Post p WHERE p.Uid=s.Uid AND s.Uid=u.Uid AND s.Uid="+str(currentUser)+" AND p.Postid="+name)
        results = c.fetchall()
        # put existing data in column 
        results = results[0]
        # form = CarInfoForm()
        form.username.choices = users
        form.title.data = results[5]
        form.content.data = results[6]
        form.location.data = results[7]
        form.color.data = results[8]
        form.carType.data = results[9]
        form.brand.data = results[10]
        form.price.data = results[11]
        form.manuYear.data = results[12]
        
        # specialist
        c.execute("SELECT * FROM Specialist")
        specialist_res = c.fetchall()
        specialist = [(specialist_res.index(item), item) for item in specialist_res]
        form.specialist.choices = specialist
        form.stars.choices = ((0,(1)),(1,(2)),(2,(3)))
        form.stars.data = results[15]-1
        form.specialist.data = results[14]-1
        return render_template('edit.html',title='Blog', form=form)    
        
# add Post
@app.route("/Posts/new", methods=['GET', 'POST'])
@login_required
def new():
    currentUser=userio.read()
    conn = mysql.connector.connect(**config)
    #Display all usernames stored in 'users' in the Username field
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    
    # number of post
    c.execute("SELECT COUNT(*) FROM Post")
    postnum = c.fetchall()
    postnum = int(postnum[0][0])+1
    # all user list
    if currentUser>0:
        c.execute("SELECT u.Uid,u.First_name,u.Last_name FROM Seller s,User u WHERE s.Uid=u.Uid AND s.Uid="+str(currentUser))
    else:
        c.execute("SELECT u.Uid,u.First_name,u.Last_name FROM User u, Seller s WHERE u.Uid=s.Uid")
    results = c.fetchall()
    users = [(results.index(item), item) for item in results]
    form = CarInfoForm()
    form.username.choices = users
    # specialist
    c.execute("SELECT * FROM Specialist")
    results = c.fetchall()
    specialist = [(results.index(item), item) for item in results]
    form.specialist.choices = specialist
    form.stars.choices = ((0,(1)),(1,(2)),(2,(3)))
    if form.validate_on_submit():
        choices = form.username.choices
        specialist = form.specialist.choices[form.specialist.data][1]
        stars = form.stars.choices[form.stars.data][1]
        user =  (choices[form.username.data][1])
        title = form.title.data
        content = form.content.data
        location= form.location.data
        color   = form.color.data
        carType =form.carType.data
        brand  = form.brand.data
        price  = form.price.data 
        manuYear = form.manuYear.data
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        title = title.replace("'","''")
        content = content.replace("'","''")
        #Add the new Post into the 'blogs' table in the database
        query = 'insert into Post (Postid, Date_post, Title,Description,Location,Color,Car_type,Brand,Price,manu_year,Uid,Sid,Stars) VALUES (' + "'" + str(postnum) + "',"  + "'" + timestamp + "'," + "'" + title + "',"+ "'" + content + "',"  + "'" + location + "'," + "'" + color + "',"+ "'" + carType + "',"  + "'" + brand + "'," + "'" + price + "'," + "'" + manuYear + "'," + "'" + str(user[0]) + "'," + "'" + str(specialist[0]) + "'," + "'" + str(stars) + "'" ')' #Build the query
        c.execute(query) #Execute the query
        conn.commit() #Commit the changes

        flash(f'Blog created for {user}!', 'success')
        return redirect(url_for('Posts'))
    return render_template('new.html', title='Blog', form=form)

@app.route("/Posts/<string:name>", methods=['POST'])
def Post_delete(name):
    conn = mysql.connector.connect(**config)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    query= 'DELETE FROM Post WHERE Postid='+str(name)
    c.execute(query) #Execute the query
    conn.commit() #Commit the changes
    return redirect(url_for('Posts'))


if __name__ == '__main__':
    app.run(debug=True)

