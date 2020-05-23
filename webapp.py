import time
from flask import *
import sys

import psycopg2

#NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)

##################################################################################################
#À LIRE:
#POUR COMPRENDRE COMMENT FONCTIONNE LES FONCTIONS PYTHONS, JE VOUS INVITE À REGARDER LES COMMENTAIRES DE LA PREMIERE FONCTION DISPLAY_REGION()
#À NOTER QUE LA REQUETE SQL DE L'ARBORESCENCE PERMETTANT D'OBTENIR LA LISTE DE DEPARTEMENT OU LE NOMBRE DE FEMME DIPLOMEE EST SUPERIEUR AU NOMBRE D'HOMME DIPLOME 
##################################################################################################
#Page d'accueil
@app.route("/")
def hello():
  return render_template("index.html")

##################################################################################################
@app.route('/success')
def success():
   return 'logged in successfully'

##################################################################################################
@app.route('/error')
def error():
   return render_template("error.html")

################################################################################################## ARBO POUR AFFICHER LA LISTE DES DEPARTEMENTS SELON LA REGION CHOISIE
#Liens régions
@app.route("/regions")
def regions():
  return render_template("regions.html", regions=display_REGIONS())

def display_REGIONS(): #AFFICHE LA LISTE DES REGIONS
  # Try to connect to an existing database
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command = 'select nom from REGIONS ;'
    print('Trying to execute command: ' + command)
    try:
      # Query the database and obtain data as Python objects
      cur.execute(command)
      print("execute ok")
      #retrieve all tuple
      rows = cur.fetchall() #rows => tableau (les lignes du résultat) de listes (les différents attributs du résultat)
      print("fetchall ok")
      return rows
      # Close communication with the database
      cur.close()
      conn.close()
      print('Returning page ' + regions)
      return regions
    except Exception as e :
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)

#Liens dept
@app.route("/regions/<numregion>")
def listedept(numregion=None): #AFFICHE LA LISTE DES DEPARTEMENTS SELON LA REGION CHOISIE
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command='select departements.nom from departements,regions where departements.region=regions.num and regions.nom=%s;'
    print('Trying to execute command: ' + command + ' with %s='+numregion)
    try:
      cur.execute(command,[numregion])
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      cur.close()
      conn.close()
    except Exception as e :
      print (str(e))
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)
  return render_template("dept.html", dept=rows)

##################################################################################################### ARBO POUR OBTENIR LES DEPARTEMENTS OÙ LE NOMBRE DE FEMME DIPLOMEE EST SUPERIEUR AU NOMBRE D'HOMME
#Liens tranches d'âges:
@app.route("/diplomes")
def dip():
    tranches_ages=f("select id, label from tranches_ages;")
    diplomes=f("select * from niveaux_diplomes;")
    return render_template('diplomes.html', tranches_ages=tranches_ages, diplomes=diplomes)

@app.route("/diplomes_2",methods=['POST'])
def dip_2():
    tranches_ages=request.form['tranches_ages']
    diplomes=request.form['diplomes']
    diplomesf=f("select distinct nom, H.annee from nb_diplomes_dept H, nb_diplomes_dept F, departements where departements.num=F.dept and H.age=1 and H.age=F.age and F.niveau=1 and F.niveau=H.niveau and F.num>H.num;".format(diplomes,tranches_ages))
    print(diplomesf)
    return render_template('diplomes_2.html', diplomesf=diplomesf)

def f(command):
    # Try to connect to an existing database
    print('Trying to connect to the database')
    try:
        conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='mdeboute')
        print('Connected to the database')
        cur = conn.cursor()
        print('Trying to execute command: ' + command)
        try:
            # Query the database and obtain data as Python objects
            cur.execute(command)
            print("execute ok")
            #retrieve all tuple
            rows = cur.fetchall() #rows => tableau (les lignes du résultat) de listes (les différents attributs du résultat)
            print("fetchall ok")
            # Close communication with the database
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(str(e))
            redirect(url_for('error'))
    except Exception as e:
        return "Cannot connect to database: " + str(e)

#####################################################################################################
#Liens choix n°1:
@app.route("/choix_de_l_age")
def choix_de_l_age(): #APPELLE CHOIX_LABEL_AGE
  return render_template("choix_de_l_age.html",a=proposition_choix_de_l_age())

def proposition_choix_de_l_age(): #AFFICHE LES DIFFERENTES TRANCHES D'AGES QUE L'ON PEUT SELECTIONNER
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command='select id,label from tranches_ages;'
    try:
      cur.execute(command)
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      cur.close()
      conn.close()
      return rows
    except Exception as e :
      print (str(e))
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)
  
@app.route("/nb_par_age",methods=['POST']) 
def nb_par_age(): #PROPOSE  UN CHOIX DE LABEL AGE
  print("I got the choice !")
  c=request.form['trancheage']
  return render_template("arbo_choix_de_l_age.html",d=arbo_choix_de_l_age(c))

def arbo_choix_de_l_age(c=None): #AFFICHER, DANS L'ORDRE CROISSANT, LE NOMBRE DE DIPLOMES CHAQUE ANNEE POUR LE LABEL CHOISI (PAGE PRECEDENTE) 
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command = "select SUM(num) from nb_diplomes_dept,niveaux_diplomes where age=%s GROUP BY age;"
    print('Trying to execute command: ' + command + ' with %s='+c)
    try:
      cur.execute(command,[c])
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      return rows
      cur.close()
      conn.close()
    except Exception as e :
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)

##################################################################################################### ARBO POUR AFFICHER LE NB DE PERSONNE DIPLOMEE CHAQUE ANNEE SELON LE CURSUS
#Liens choix personnel n°2: 
@app.route("/choix_cursus")
def choix_cursus(): #APPELLE NB_PAR_ANNEE QUAND UN CHOIX A ETE FAIT
  return render_template("choix_cursus.html",g=choix_cursus_affichage())

def choix_cursus_affichage(): #AFFICHE LES DIFFERENTES TRANCHES D'AGES QUE L'ON PEUT SELECTIONNER
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command='select label from niveaux_diplomes;'
    try:
      cur.execute(command)
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      cur.close()
      conn.close()
      return rows
    except Exception as e :
      print (str(e))
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)

@app.route("/nb_par_annee",methods=['POST']) 
def nb_par_annee(): #APPELLE ARBO_CHOIX_CURSUS
  print("I got the choice !")
  a=request.form['niveaudiplome']
  return render_template("arbo_choix_cursus.html",b=arbo_choix_cursus(a))


def arbo_choix_cursus(a=None): #AFFICHER, DANS L'ORDRE CROISSANT, LE NOMBRE DE DIPLOMES CHAQUE ANNEE POUR LE CURSUS CHOISI (PAGE PRECEDENTE) 
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command = 'select annee,SUM(nb_diplomes_dept.num) from departements,nb_diplomes_dept,niveaux_diplomes where departements.num=nb_diplomes_dept.dept and nb_diplomes_dept.niveau=niveaux_diplomes.id and niveaux_diplomes.label=%s GROUP BY annee ORDER BY SUM(nb_diplomes_dept.num) ;'
    print('Trying to execute command: ' + command + ' with %s='+a)
    try:
      cur.execute(command,[a])
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      return rows
      cur.close()
      conn.close()
    except Exception as e :
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)

##################################################################################################### ARBO POUR AFFICHER LE NOMBRE DE PERSONNE DIPLOMEE PAR DEPARTEMENT
#Liens choix personnel n°3:
@app.route("/choix_dept")
def choix_dept(): #APPELLE DISPLAY_DEPT
  return render_template("choix_dept.html",departements=display_dept())

def display_dept(): #AFFICHE TOUS LES DEPARTEMENTS SUR LA PAGE CHOIX_DEPT
  print('Trying to connect to the database')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command = 'select nom from departements ;'
    print('Trying to execute command: ' + command)
    try:
      cur.execute(command)
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      return rows
      cur.close()
      conn.close()
    except Exception as e :
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)

#Liens nb diplômés
@app.route("/choix_dept/<nomdepartement>")
def arbo_choix_dept(nomdepartement=None): #AFFICHE LE NOMBRE DE DIPLOMES PAR DEPARTEMENT (CHOISI SUR LA PAGE PRECENDENTE)
  print('Trying to connect to the database for choixdept')
  try:
    conn = psycopg2.connect(host='dbserver', dbname='bpinaud', user='parvy')
    print('Connected to the database')
    cur = conn.cursor()
    command='select niveau,SUM(nb_diplomes_dept.num) from departements,nb_diplomes_dept where nb_diplomes_dept.dept=departements.num and departements.nom=%s GROUP BY niveau;'
    try:
      cur.execute(command,[nomdepartement])
      print("execute ok")
      rows = cur.fetchall()
      print("fetchall ok")
      cur.close()
      conn.close()
    except Exception as e :
      print (str(e))
      return redirect(url_for('error'))
  except Exception as e :
    return "Cannot connect to database: " + str(e)
  return render_template("arbo_choix_dept.html", nombresdiplomes=rows)

##################################################################################################### NE PAS MODIFIER
#NE SURTOUT PAS MODIFIER
if __name__ == "__main__":
   app.run(debug=True)
