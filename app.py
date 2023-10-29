from flask import Flask, render_template, request, jsonify,flash,redirect,url_for,session
from PyPDF2 import PdfReader
from tqdm import tqdm
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

os.environ["OPENAI_API_KEY"] = "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"
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)

        try:
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose another.', 'danger')

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


folder_path = r"C:\Users\Acc User\Desktop\TATA_Chatbot"

# ... (existing code) ...

@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user = session.get(session['user_id'])  

        if request.method == 'POST':
            if 'question' in request.form:
                question = request.form.get('question')
                answer = process_pdf(question)
                return jsonify({'answer': answer})
        else:
            return render_template('dashboard.html', current_user=user)
    flash('You need to login first')
    return redirect(url_for('login'))




def process_pdf(question):
    import os
    pdf_files = [file for file in os.listdir(folder_path) if file.endswith('.pdf')]
    pdf_file_names = [os.path.splitext(file)[0] for file in pdf_files]    
    raw_text = ''
    print("PDF File Names:")
    for pdf_file_name in pdf_file_names:
        file_path=r"C:\Users\Acc User\Desktop\TATA_Chatbot\{}.pdf".format(pdf_file_name)
        # raw_text = ''
        pdf_reader = PdfReader(file_path)
        total_pages = len(pdf_reader.pages)

       
        with tqdm(total=total_pages, desc="Processing PDF") as pbar:
            for i, page in enumerate(pdf_reader.pages):
                content = page.extract_text()
                if content:
                    raw_text += content
                    
                pbar.update(1) 

        
    text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=800,
            chunk_overlap=200,
            length_function=len,
        )
    texts = text_splitter.split_text(raw_text)
        
    embeddings = OpenAIEmbeddings()
    document_search = FAISS.from_texts(texts, embeddings)
    chain = load_qa_chain(OpenAI(), chain_type="stuff")
    print(document_search)
    docs = document_search.similarity_search(question)
    x = chain.run(input_documents=docs, question=question)
    return x

@app.route('/generate_summary', methods=['GET'])
def generate_summary():
    if 'user_id' in session:
        user = session.get(session['user_id'])
        summary_result = process_pdf("give me property details anvika pride in the form like building name, address, size ,owners,etc go on ?")
        
        return render_template('summary.html', current_user=user, summary_result=summary_result)
    flash('You need to login first')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)


