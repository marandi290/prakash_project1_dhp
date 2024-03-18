from flask import Flask, render_template, request, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
import psycopg2
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
nltk.download("all")
import json



app = Flask(__name__, static_folder="/var/data/")
oauth = OAuth(app)
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GITHUB_CLIENT_ID'] = "e11bb87d6246014f3d6d"
app.config['GITHUB_CLIENT_SECRET'] = "90fd1ae17126eec83e94f3b77700998c6727f2d9"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)
# GitHub admin usernames for verification
github_admin_usernames = ["marandi290", "atmabodha"]

# Default route
@app.route('/marandi')
def marandi():
    is_admin = False
    github_token = session.get('github_token')
    if github_token:
        github = oauth.create_client('github')
        resp = github.get('user').json()
        username = resp.get('login')
        if username in github_admin_usernames:
            is_admin = True
    return render_template('verify.html', logged_in=github_token is not None, is_admin=is_admin)


# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    session['github_token'] = token
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    
    if 'login' in resp:
        username = resp['login']
        if username in github_admin_usernames:
            conn  = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT ID, url FROM news_table")
            url_list = cur.fetchall()

            conn.commit()
            return render_template("url_view.html", url_list = url_list)   
    
    return render_template("verify.html")


# making connection to database.
def connect_db():
    conn = psycopg2.connect(
        host='dpg-cnmr6o2cn0vc738fmu8g-a', database='text_analyze', user='prakash_python', password='bbbZ0QbEVQdUHEzpKHNWgOpdqyUimwta'               
    )
    return conn
    
@app.route("/",methods=['GET', 'POST'])
def portal():
    return render_template("index.html")

@app.route("/analyze",methods = ['POST'])
def analyze():
    if request.method == "POST":
        # define the cur
        conn = connect_db()
        cur = conn.cursor()
    
        # take url from "indx.html"
        URL = request.form["article_link"]
        URL = str(URL)
    
        # fetch the webpage content
        response = requests.get(URL)
        soup = BeautifulSoup(response.content, "html.parser")
    
        # title of the news
        news_title = soup.title.string
    
        # Find the main content of the article (usually within <p> tags)
        article_text = ""
        for paragraph in soup.find_all("p"):
            article_text += paragraph.get_text() + "\n"

        # Clean the extracted text (remove extra spaces, newlines, etc.)
        main_text = " ".join(article_text.split())                                 # main text, but stop_words are still present.
    
    
        # number of sentences
        sentences = sent_tokenize(main_text)
        num_sentences = len(sentences)
    
        # number of words
        words = word_tokenize(main_text)
        num_words = len(words)
    
        # stop_words
        stop_words = set(stopwords.words("english"))
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        num_stop_words = len(words) - len(filtered_words)
    
        # Find POS Tags
        pos_dict = {}
        x = nltk.pos_tag(words, tagset='universal')
        index = 0
        for tupple in x:
            if tupple[1] not in pos_dict.keys():
                postno = 0
                for tuppl in x[index::]:
                    if tupple[1] == tuppl[1]:
                        postno = postno+1
                pos_dict[tupple[1]] = postno
        with open("pos_dict.json", 'w'):
            # Use json.dump() to write the dictionary to the file
                a = json.dumps(pos_dict)
    
        # join the filtered_words to show
        cleaned_text = " ".join(filtered_words)

        url = str(URL)        # to store to url
        # store it in the database
        # create table
        cur.execute("CREATE TABLE IF NOT EXISTS news_table (Title VARCHAR(500), News VARCHAR(10000), Sentence_no INT, Words_no INT, Stopwords_no INT, Postages VARCHAR(500), url VARCHAR(1000))")
        
    
        cur.execute("INSERT INTO news_table (Title, News, Sentence_no, Words_no, Stopwords_no, Postages, url) VALUES (%s, %s, %s, %s, %s, %s, %s)", (news_title, cleaned_text, num_sentences, num_words, num_stop_words, a, url))
        conn.commit()
    
        # show it on the html page
        cur.execute("SELECT Title, News, Sentence_no, Words_no, Stopwords_no, Postages FROM news_table ORDER BY ctid DESC LIMIT 1")
        data = cur.fetchall()
        conn.commit()
        cur.close()
    
        return render_template("details.html", data=data)

@app.route("/admin",methods=['GET',"POST"])
def admin():
        return render_template('verify.html')
    
@app.route("/verify_admin",methods = ["POST"])
def verify_admin():
    admin_pswd = 'emanuel'
    if request.method == "POST":
        password = request.form['password']
        if password == admin_pswd:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT ID, url FROM news_table")
            url_list = cur.fetchall()

            conn.commit()
            cur.close()

            return render_template("url_view.html", url_list = url_list)

        else:
            return render_template('verify.html')

@app.route("/viewdetail/<id>", methods=["GET", "POST"])
def viewdetail(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT Title, News, Sentence_no, Words_no, Stopwords_no, Postages FROM news_table WHERE ID=%s", (id))
    data = cur.fetchall()
    
    return render_template("details.html", data=data)
if __name__=='__main__':
    app.run(debug=True, port=8000)
    conn = connect_db()
    conn.close()
    
