from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import model, random, os, requests
from faster_whisper import WhisperModel

app = Flask(__name__, static_url_path="/static")
app.secret_key = "password"
aiModel = WhisperModel("tiny")
api = 'https://api.api-ninjas.com/v1/textsimilarity'
key = 'key goes here'

@app.route("/", methods=["GET", "POST"]) # Route for the homepage
def homepage():
    if request.method == "POST":
        return redirect("/login")
    else:
        return render_template("home.html", user = session.get("user"), song = session.get("song"))

@app.route("/login", methods=["GET", "POST"]) # Route for login
def login():
    if session.get("user") != None:
        return redirect(url_for("songSelect")) 
    if request.method == "POST": # Login / Register logic
        username = request.form["usernameField"]
        password = request.form["passwordField"]
        if not username or not password:
            return render_template("login.html", message="Please enter a valid username and password")
        if request.form["action"] == "register":
            state = model.registerNewStudent(username, password)
            if state[0] == "Success":
                session["user"] = username
                session["userID"] = state[1]
                return redirect("/songSelect")
            elif state == "This user already exists":
                return render_template("login.html", message="That username already exists. If that is your account, please login")
            elif state == "Enter a valid username and password":
                return render_template("login.html", message="Enter a valid username and password")
            else: 
                return "something went wrong with the register logic"
        elif request.form["action"] == "login":
            state = model.loginStudent(username, password)
            if state == "Incorrect Login":
                return render_template("login.html", message="Incorrect Username or Password")
            else:
                session["user"] = username
                session["userID"] = state.studentID
                return redirect("/songSelect")
        else:
            return "bad parameter" # This is impossible (redundant line but whatever)
    else:
        return render_template("login.html", user = session.get("user"), song = session.get("song"))


@app.route("/songSelect", methods=["GET", "POST"]) # Route for song select page
def songSelect():
    if session.get("user") == None:
        return redirect(url_for("homepage")) 
    if session.get("song") != None:
        return redirect(url_for("menu"))
    if request.method == "POST":
        session["songID"] = request.form["songs"]
        session["song"] = model.getSong(session.get("songID")).title
        return redirect("/menu")

    else:
        songList = model.getAllSongs()
        return render_template("songselect.html", songList = songList, user = session.get("user"), song = session.get("song"))
    
@app.route("/menu", methods=["GET", "POST"]) # Main menu route
def menu():
    if session.get("user") == None or session.get("song") == None:
        return redirect(url_for("homepage")) 
    session["quizPointer"] = 0
    if session.get("flashcardStuff"):
        session.pop("flashcardStuff")
        session.pop("flashcardPointer")
    if session.get("quizStuff"):
        session.pop("quizStuff")
        session.pop("quizPointer")

    #Check which buttons to lock
    flashCardWords = model.getCurrentFlashcards(session.get("userID"), session.get("songID"))
    quizWord = model.getQuizWords(session.get("userID"), session.get("songID"))
    singWord = model.getLearntWords(session.get("userID"), session.get("songID"))
    if len(flashCardWords) < 1:
        flashcardEnabled = 1
    else: flashcardEnabled = 0

    if len(quizWord) < 10:
        quizEnabled = 10 - len(quizWord)
    else: quizEnabled = 0

    if len(singWord) < 10:
        singEnabled = 10 - len(singWord)
    else: singEnabled = 0
    
    if request.method == "POST":
        match request.form["action"]:
            case "theory":
                return redirect("/menu/theory")
            case "flashcards":
                return redirect("menu/flashcards/card")
            case "quiz":
                return redirect("menu/quiz")
            case "karaoke":
                return redirect("menu/karaoke")
    else:
        return render_template("menu.html", user = session.get("user"), song = session.get("song"), theory=True, flashcard=flashcardEnabled, quiz=quizEnabled, sing=singEnabled)


@app.route("/menu/theory", methods=["GET", "POST"]) # Theory Route
def theory():
    if session.get("user")  == None:
        return redirect(url_for("homepage")) 

    theory = model.getCurrentTheoryWord(session["userID"], session.get("songID"))
    if theory == None:
        return render_template("theory.html", message="You've finished all the words for this song!", user=session.get("user"), song=session.get("song"))
    if request.method == "GET":
        return render_template("theory.html", term=theory[1], theory=theory[0], user=session.get("user"), song=session.get("song"))

    elif request.method == "POST":
        update = model.updateTheoryScore(session["userID"], theory[1].wordID, 1)
        if update == "Success":
            theory = model.getCurrentTheoryWord(session["userID"], session.get("songID"))
            if theory != None:
                return render_template("theory.html", term=theory[1], theory=theory[0], user=session.get("user"), song=session.get("song"))
            else: return render_template("theory.html", message="You've finished all the words for this song!", user=session.get("user"), song=session.get("song"))
        else:
            return render_template("theory.html", message="error", user=session.get("user"), song=session.get("song"))



@app.route("/logout")
def logout():
    [session.pop(key) for key in list(session.keys()) if not key.startswith('_')] # https://stackoverflow.com/questions/27747578/how-do-i-clear-a-flask-session
    return redirect("/")

@app.route("/changeSong")
def changeSong():
    session["song"] = None
    return redirect("/songSelect")


@app.route("/menu/flashcards/card")
def flashcards():
    if session.get("user") == None:
        return redirect(url_for("homepage")) 
    if session.get("flashcardStuff") is None:
        words = model.getCurrentFlashcards(session["userID"], session.get("songID"))
        flashcardArray = []
        for i in words:
            flashcardArray.append(i.wordID)
        random.shuffle(flashcardArray)
        session["flashcardStuff"] = flashcardArray
        session["flashcardPointer"] = 0
    else:
        flashcardArray = session["flashcardStuff"]
    print(flashcardArray)
    if len(flashcardArray) < 1:
        return redirect("/menu")

    currentWord = model.getWord(flashcardArray[session["flashcardPointer"]])
    currentFlashcard = model.getFlashcard(flashcardArray[session["flashcardPointer"]])
    return render_template("flashcard.html", word = currentWord.term, definition = currentFlashcard.definition, reading = currentFlashcard.reading, sentence = currentFlashcard.sentence, translated = currentFlashcard.sentenceTl, user=session.get("user"), song=session.get("song"))

@app.route("/flashcard-check", methods=["POST"])
def flashcardCheck():
    data = request.json
    flashcardArray = session["flashcardStuff"]
    currentWord = model.getWord(flashcardArray[session["flashcardPointer"]])

    if data["response"] == "yes":
        model.updateFlashcardScore(session["userID"], currentWord.wordID, 1)
        session["flashcardStuff"] = flashcardArray
    elif data["response"] == "no":
        pass
    else: #How did you get here
        return "what"
    
    print(session["flashcardPointer"])
    print(len(session["flashcardStuff"]))
    if session["flashcardPointer"] >= len(session["flashcardStuff"]) - 1:
        return jsonify({"title": "You're done! Head back to the menu to learn more words in theory or practice your skills in the quiz", "finished": True})
    else: session["flashcardPointer"] = session["flashcardPointer"] + 1
    
    nextWord = model.getWord(session["flashcardStuff"][session["flashcardPointer"]])
    nextFlashcard = model.getFlashcard(session["flashcardStuff"][session["flashcardPointer"]])
    return jsonify({"term": nextWord.term, "definition": nextFlashcard.definition, "reading": nextFlashcard.reading, "sentence": nextFlashcard.sentence, "translated": nextFlashcard.sentenceTl})

@app.route("/menu/quiz")
def quiz():
    if session.get("quizStuff") is None:
        words = model.getQuizWords(session["userID"], session.get("songID"))
        quizArray = []
        for i in words:
            quizArray.append(i.wordID)
        random.shuffle(quizArray)
        session["quizStuff"] = quizArray
        session["quizPointer"] = 0
    else:
        quizArray = session["quizStuff"] 

    

    correctWord = model.getWord(quizArray[session["quizPointer"]])
    optionsArray = random.sample(quizArray, len(quizArray))
    optionsArray.remove(correctWord.wordID)
    correctWordFlashcard = model.getFlashcard(correctWord.wordID)

    correctOption = random.randint(1, 4)
    options = {1: "", 2: "", 3: "", 4: ""}
    options[correctOption] = correctWord.term
    session["correctWord"] = correctWord.wordID
    for i in options:
        if i != correctOption:
            options[i] = model.getWord(optionsArray[i]).term

    return render_template("quiz.html", option1=options[1], option2=options[2], option3=options[3], option4=options[4], user=session.get("user"), song=session.get("song"), definition=correctWordFlashcard.definition)

@app.route("/submit-answer", methods=["POST"])
def answer():
    data = request.json
    print(data["definition"])
    quizArray = session["quizStuff"]
    userSelected = model.getWordFromTerm(data["term"]).wordID
    correctResponse = session["correctWord"]
    isCorrect = userSelected == correctResponse
    if isCorrect:
        model.updateQuizScore(session["userID"], correctResponse, 1)
        session["quizStuff"] = quizArray
    else:
        print("its wrong")

    print(session["quizPointer"])
    print(len(session["quizStuff"]))
    if session["quizPointer"] >= len(session["quizStuff"]) - 1:
        #we finished all the words for now
        return jsonify({"finished": True, "correctTerm": model.getWord(correctResponse).term})
    else:
        session["quizPointer"] = session["quizPointer"] + 1
    return jsonify({"correctTerm": model.getWord(correctResponse).term})


@app.route("/menu/karaoke/")
def karaoke():
    song = model.getSongFromTitle(session.get("song"))
    return render_template("karaoke.html", songID = song.songID, user=session.get("user"), song=session.get("song"))

@app.route("/menu/karaoke/upload", methods=["POST"])
def save():
    audio = request.files.get('audio')
    if audio:
        save_path = os.path.join('uploads', audio.filename)
        os.makedirs('uploads', exist_ok=True)
        audio.save(save_path)
        print("files recived and saved")
    transciption = aiModel.transcribe(os.path.abspath(save_path), language="ja")
    text = ""
    for segment in transciption[0]:
        text = text + segment.text
    print("succesfully transcribed")
    #We make the API request
    lyrics = model.getFullLyrics(model.getSongFromTitle(session.get("song")).songID)

    if text is not None:
        body = {'text_1': text, 'text_2': lyrics}
        response = requests.post(api, headers={'X-Api-Key': 'rPzjz8THll4Nm/PlkFsM8A==qBVKItJEBgGJQL0j'}, json=body, timeout=60)
        if response.status_code == 200:
            session["karaokeScore"] = response.json()["similarity"] * 100
        else:
            print("Error:", response.status_code, response.text)
            session["karaokeScore"] = 0
    else:
        session["karaokeScore"] = 0

    os.remove(save_path)
    if session["karaokeScore"] < 20:
        #Scored terribly
        message = "You need to improve your pronouciation... or you couldn't read very much."
        rank = "D"
    elif session["karaokeScore"] < 40:
        #Scored ok
        message = "You were able to read some of it. Keep trying"
        rank = "C"
    elif session["karaokeScore"] < 60:
        #Scored satisfactory
        message = "You read most of it. Well done, and aim for a higher rank"
        rank = "B"
    elif session["karaokeScore"] < 80:
        #Scored well
        message = "You're reading almost everything! Just work on your pronouciation and you'll get it all in no time"
        rank = "A"
    elif session["karaokeScore"] < 95:
        #Scored excellent
        message = "Well done! Amazing score"
        rank = "S"
    else:
        #Scored perfect
        message = "You scored a perfect run. Amazing"
        rank = "SS"
    print(session["karaokeScore"])
    return jsonify({"rank": rank, "message": message})
