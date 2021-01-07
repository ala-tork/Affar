import os
from flask import Flask ,render_template,request,redirect,url_for,flash,session
from forms import MyForm ,RegisterForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from flask_mysqldb import MySQL
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
from admin_forms import adminlogin
from functools import wraps #update 0.1
import urllib.request
from datetime import datetime
basedir = os.path.abspath(os.path.dirname(__file__))
app=Flask(__name__)
app.config.from_object('config.config')


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'affar'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'static/uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=5,
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=False,

)

dropzone = Dropzone(app)

#update 0.1

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap

#update 0.1

def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/subscribe', methods=["GET", "POST"])
@not_logged_in
def subscribe():
    form = RegisterForm(request.form)
    if request.method =="POST" and form.validate():
            email= request.form.get("email")
            pseudo=request.form.get("pseudo")
            phone =request.form.get("phone")
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            if password == confirm:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO users (email, pseudo, phone ,password) VALUES (%s,%s,%s,%s)", (email, pseudo, phone ,password))
                    mysql.connection.commit()
                    cur.close()
                    flash('you are successfully registered','success')
                    return redirect(url_for('login'))
            else :
                return render_template('subscribe.html', form=form)
    return render_template('subscribe.html', form=form)



@app.route('/form', methods=['GET', 'POST'])
def form():
    form = MyForm()
    if form.validate_on_submit():
        return '<h1>The username is {}. The password is {}.'.format(form.username.data, form.password.data)
    return render_template('form.html', form=form)


@app.route('/login', methods=["GET", "POST"])
@not_logged_in #update 0.1
def login():
    form = MyForm()
    if request.method =="POST" :
            email= request.form.get("email")
            password = request.form.get("password")
            cur = mysql.connection.cursor()
            result= cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))

            
            if result > 0:
                    data = cur.fetchone()
                    session['logged_in'] = True #update 0.1
                    session['log']=True
                    session['s_pseudo'] = data['pseudo']
                    session['id']=data['id']                   
                    flash('you are successfully loggin in ','success')
                    return render_template('home.html')
            else :
                flash('Email Or Password Are invalid ','danger')
                return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    flash("Vous étes deconnecte","primary")
    return render_template('home.html')


@app.route("/deposerAnnonce",methods=["POST","GET"])
@is_logged_in #update 0.1
def upload():
    form = MyForm()
     
    return render_template('deposer_annonce.html',form=form)


@app.route('/upload', methods=['POST'])
def handle_upload():
    
    cur = mysql.connection.cursor()
    now = datetime.now() 
    title = request.form.get('titre')
    categorie = request.form.get('categorie')
    description = request.form.get('description')
    prix = request.form.get('prix')
    i=0;  # update 0.1
    for key, f in request.files.items():  
            if key.startswith('file'):
                i=i+1 
                f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
                maxx=cur.execute("SELECT MAX(id_produit)  FROM produit")
                result= cur.fetchone()
                if (i==1): 
                    cur.execute("INSERT INTO images (source, id_produit,premier) VALUES (%s, %s,%s)",[f.filename,result['MAX(id_produit)']+1,i])
                    mysql.connection.commit()
                else:
                    cur.execute("INSERT INTO images (source, id_produit) VALUES (%s, %s)",[f.filename, result['MAX(id_produit)']+1])
                    mysql.connection.commit()

    return '', 204

@app.route('/mesannonces', methods=['POST'])
def handle_form():
    title = request.form.get('titre')
    categorie = request.form.get('categorie')
    description = request.form.get('description')
    prix = request.form.get('prix')
    ville = request.form.get('ville')
    now = datetime.now() 
    numero=request.form.get('phone')
    #ville= request.form.get('ville')   
    etat=0 # update 0.1
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO produit (id,title,categorie,description,prix,date_ajout,numero,ville,etat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (session['id'],title, categorie, description ,prix,now,numero,ville,etat))
    mysql.connection.commit()
    cur.close()
    flash('Votre Announce a été Ajouter avec succes','success')
    return redirect(url_for('mesannonces'))

#Mon announces lors d ajouter
@app.route('/mesannonces', methods=["GET", "POST"])
@is_logged_in #update 0.1
def mesannonces():
   cur = mysql.connection.cursor()
   user_id=session['id']
   cur.execute("SELECT distinct pr.id_produit , pr.title , pr.id , pr.categorie , pr.description,pr.prix,pr.date_ajout,.pr.numero,pr.ville,pr.etat,img.source FROM produit as pr , images as img WHERE pr.id_produit=img.id_produit and  img.premier=1 and pr.id=%s ORDER BY pr.date_ajout DESC",[user_id])
   #cur.execute("SELECT * FROM `produit` WHERE id=%s  ORDER BY `date_ajout` DESC",[user_id])
   result = cur.fetchall()
   mysql.connection.commit()
   cur.close()
   return render_template('mesannonces.html',result=result)

#Consulter tous les announces 

@app.route('/offre', methods=["GET", "POST"])

def offre():
   cur = mysql.connection.cursor()
   curso =  mysql.connection.cursor()
   img =  mysql.connection.cursor()
   
   
   #print(images)
   cur.execute("SELECT distinct pr.id_produit , pr.title , pr.id , pr.categorie , pr.description,pr.prix,pr.date_ajout,.pr.numero,pr.ville,img.source FROM produit as pr , images as img WHERE pr.id_produit=img.id_produit and pr.etat=1 and img.premier=1 ORDER BY pr.date_ajout DESC")
   result = cur.fetchall()
   mysql.connection.commit()
   #cur.execute("SELECT img.source from images as img , produit as prt WHERE img.id_produit=%s and img.premier=1",(product_id,))
   if 'view' in request.args:
    product_id = request.args['view']
    session['product_id']=product_id
    curso.execute("SELECT ur.pseudo , ur.id FROM `produit` as pr ,`users` as ur WHERE pr.id=ur.id and pr.id_produit=%s",(product_id,))
    cur.execute("SELECT * FROM produit WHERE id_produit=%s", (product_id,))
    img.execute("SELECT img.source , img.premier FROM produit as pr , images as img WHERE pr.id_produit=img.id_produit and pr.id_produit=%s", (product_id,))
    userss=curso.fetchall()
    product = cur.fetchall()
    images=img.fetchall()
    
    #print(product)
    return render_template('view_offre.html',offres=product,userss=userss,images=images)
   
   return render_template('offre.html',result=result)


@app.route('/chats', methods=["GET", "POST"])
@is_logged_in #update 0.1
def chats():
    form = RegisterForm(request.form)
    idd=request.args['message']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (idd,))
    result=cur.fetchall()
    if request.method =="POST":
        msg =request.form.get("msg")
        cur.execute("INSERT INTO messages (body, msg_by, msg_to ) VALUES (%s,%s,%s)", (msg, session['id'], idd ))
        mysql.connection.commit()
        cur.close()
        flash('Message Envoyer avec success','warning')
        url = '/offre?view=%s' % (session['product_id'])
        return redirect(url)
    return render_template('messages.html',form=form,result=result)


@app.route('/chatting/<string:id>', methods=['GET', 'POST'])
def chatting(id):
    if 'id' in session:
       form = RegisterForm(request.form) 
       cur = mysql.connection.cursor()
       get_result = cur.execute("SELECT * FROM users WHERE id=%s", [id])
       l_data = cur.fetchone()
       if get_result > 0:
            session['name'] = l_data['pseudo']
            myid = session['id'] # my  id 
            session['lid'] = id # target id
            if request.method == 'POST':
                  txt_body = form.body.data
                  print(txt_body)
                  # Create cursor
                  cur = mysql.connection.cursor()
                  cur.execute("INSERT INTO messages(body, msg_by, msg_to) VALUES(%s, %s, %s)", (txt_body, myid, session['lid']))
                  # Commit cursor
                  mysql.connection.commit()
            cur.execute("SELECT DISTINCT usr.id , usr.pseudo FROM messages as msg , users as usr WHERE msg.msg_by=%s and usr.id=msg.msg_to or msg.msg_to=%s and usr.id=msg.msg_by",(myid,myid))
            users = cur.fetchall()

            # Close Connection
            cur.close()
            return render_template('chatting.html', users=users,form=form)
           
    else:
        return redirect(url_for('login'))

@app.route('/discussion', methods=['GET', 'POST'])
def discussion():
    if 'id' in session:
        id = session['lid'] #Target id
        uid = session['id'] # My id
        # Create cursor
        cur = mysql.connection.cursor()
        # Get message
        cur.execute("SELECT * FROM messages WHERE (msg_by=%s AND msg_to=%s) OR (msg_by=%s AND msg_to=%s) "
                    "ORDER BY id ASC", (id, uid, uid, id))
        chats = cur.fetchall()
        # Close Connection
        cur.close()
        return render_template('discussion.html', chats=chats )
    return redirect(url_for('login'))


    #admin log in
@app.route('/admin', methods=["GET", "POST"])
def admin():
    form = adminlogin()
    if request.method =="POST" :
        email= request.form.get("email")
        password= request.form.get("password")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        result = cur.fetchall()
        if len(result)>0:
            #session['admin_log_in']=True
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM admin ")
            last_name= cur.fetchall()
            session["log_in"] = last_name
            session["log"]=True
            return redirect(url_for('produit_not_accepted'))
        else:
            return render_template('admin/pages/login_2.html', form=form)
    return render_template('admin/pages/login_2.html', form=form)
 


@app.route('/admin_out')
def admin_log_out():
    session.clear()
    
    return redirect(url_for('admin'))


#affichier la liste de utilisateurs
@app.route('/users')
def users():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM produit WHERE etat= 1")
    produit_not_accepted = curso.execute("SELECT * FROM produit WHERE etat = 0")
    users_rows = curso.execute("SELECT * FROM users")
    result = curso.fetchall()
    return render_template('admin/pages/all_users.html', result=result, row=num_rows,users_rows=users_rows,produit_not_accepted=produit_not_accepted)

@app.route('/produit_not_accepted')
def produit_not_accepted():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM produit where etat=1")
    produit_not_accepted = curso.execute("SELECT * FROM produit where etat=0")
    result = curso.fetchall()
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('admin/pages/all_Produit_not_accepted.html', result=result, row=num_rows, produit_not_accepted=produit_not_accepted,
                           users_rows=users_rows)


#affichier le liste de produits
@app.route('/Product_accepted')
def product():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM produit where etat=1")
    result = curso.fetchall()
    produit_not_accepted = curso.execute("SELECT * FROM produit where etat=0")
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('admin/pages/all_product.html',result=result, row=num_rows,users_rows=users_rows,produit_not_accepted=produit_not_accepted)

#ajouter une categorie
@app.route('/add_categorie')
def add_categorie():
    return render_template('admin/pages/add_categorie.html')

#supprimer utilisateur
@app.route('/Delete_user')
def Delete_user():
    user_id = request.args['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", [user_id])
    mysql.connection.commit()
    cur.close()
    flash('deleted successfully','success')
    return redirect(url_for("users"))

#suprimer produit
@app.route('/Delete_Product')
def Delete_product():
    produit_id = request.args['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM produit WHERE id_produit=%s", [produit_id])
    mysql.connection.commit()
    cur.close()
    flash('deleted successfully','success')
    return redirect(url_for("product"))

#accept produit 
@app.route('/accept_Product')
def accept_Product():
    produit_id = request.args['id']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE  produit SET etat=1 WHERE id_produit=%s", [produit_id])
    mysql.connection.commit()
    cur.close()
    flash('deleted successfully','success')
    return redirect(url_for("produit_not_accepted"))

#edit edit user 
@app.route('/edit_user')
def edit_user():
    form = RegisterForm(request.form)
    user_id = request.args['id']
    session["user_id"] = user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s ",[user_id])
    result = cur.fetchall()
    return render_template('edit_user.html',form=form, result=result)


@app.route('/update',methods=["POST"])
def update():
    id=session["user_id"]
    pseudo= request.form['pseudo']
    email= request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET pseudo=%s ,email=%s ,password=%s ,phone=%s WHERE id=%s",[pseudo,email,password,phone,id])
    mysql.connection.commit()
    cur.close()
    session.clear()
    return redirect(url_for('users'))

#edit user au niveau de client 
@app.route('/edit_user1')
def edit_user1():
    form = RegisterForm(request.form)
    user_id = request.args['id']
    session["user_id"] = user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s ",[user_id])
    result = cur.fetchall()
    return render_template('edit_user1.html',form=form, result=result)  


#edit produit
@app.route('/edit_Product')
def edit_Product():
    form = MyForm()
    produit_id=request.args['id']
    session["produit_id"]=produit_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM produit WHERE id_produit=%s ",[produit_id])
    result = cur.fetchall()
    return render_template('edit_anonce.html',form = form , result=result)

@app.route('/update_anonce',methods=["POST"])
def upload_anonce():
    id=session["produit_id"]
    title= request.form['titre']
    categorie= request.form['categorie']
    description = request.form['description']
    prix = request.form['prix']
    numero = request.form['numero']
    ville = request.form['departement']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE produit SET title=%s ,categorie=%s ,description=%s ,prix=%s, numero=%s ,ville=%s WHERE id_produit=%s",[title,categorie,description,prix,numero,ville,id])
    mysql.connection.commit()
    cur.close()
    session.clear()
    return redirect(url_for('product'))

#edit produit client
@app.route('/edit_Product_client')
def edit_Product_client():
    form = MyForm()
    produit_id=request.args['id']
    session["produit_id"]=produit_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM produit WHERE id_produit=%s ",[produit_id])
    result = cur.fetchall()
    return render_template('edit_anonce_client.html',form = form , result=result)

@app.route('/user_product')
def user_product():
    id = request.args['id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM produit where id=%s",[id])
    result = cur.fetchall()

    cur.execute("SELECT * FROM users where id=%s",[id])
    users = cur.fetchall()
    cur.close()
    return render_template('admin/pages/user_product.html',result=result,users=users)


@app.route('/Delete_Product_client')
def Delete_Product_client():
    produit_id = request.args['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM produit WHERE id_produit=%s", [produit_id])
    mysql.connection.commit()
    cur.close()
    flash('deleted successfully','success')
    return redirect(url_for("mesannonces"))