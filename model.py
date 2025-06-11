import sqlite3, datetime
import common

def createConnection():
    """Defining database constant"""
    return sqlite3.connect("databasestuff/learning.db")

def registerNewStudent(username: str, password: str):
    """Registers a new student with a username and password, and adds their userID as a new row into the settings database. Initialises their learning progress as well"""
    con = createConnection()
    cur = con.cursor()
    try:
        doesUserExist = cur.execute(f"""
            SELECT * FROM Student WHERE username = ?
        """, (username,)).fetchone()

        if doesUserExist == None:
            cur.execute(f"""
                    INSERT INTO Student (Username, Password) VALUES 
                        (?, ?)
                """, (username, password))
            id = cur.execute(f"""
                    SELECT UserID FROM Student WHERE username=?
                """, (username,)).fetchone()[0]
            
            cur.execute(f"""
                    INSERT INTO Settings (UserID, Volume, Locking, WordsPerDay, CorrectColour, WrongColour, BgColour, TextColour)
                        VALUES ({id}, 100, 1, 15, '00f746', '#f70015', '#bfbfbf', '#000000')
                """)
            words = cur.execute(f"""
                    SELECT WordID FROM Word
        """)
            wordList = words.fetchall()
            for i in wordList:
                wordID = i[0]
                currentDate = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
                cur.execute(f"""
                    INSERT INTO StudentKnowledge (UserID, WordID, Theory, Flashcard, Quiz, ReviewDate)
                            VALUES ({id}, {wordID}, 0, 0, 0, '{currentDate}')
        """)
            con.commit()
            return "Success", id

        else:
            return "This user already exists"
    except Exception as e:
        print("Except in registerNewStudent")
        
    finally:
        con.close()

def loginStudent(username:str, password:str):
    """Checks if there is a matching username and password in the database. If there is, returns an object of that user"""

    con = createConnection()
    cur = con.cursor()

    try:
        student = cur.execute(f"""
        SELECT UserID FROM Student WHERE Username = ? AND Password = ?
    """, (username, password)).fetchone()
        
        if student == None:
            return "Incorrect Login"
        else:
            return getUserDetails(student[0])

    except Exception as e:
        print("Except in loginStudent")         
    finally:
        con.close()

def updateProfilePhoto(UserID: int, photoURI: str):
    """Updates a specified user's profile photo URI"""
    con = createConnection()
    cur = con.cursor()

    try:
        cur.execute(f"""
        UPDATE Student 
        SET PhotoURI = '{photoURI}'
        WHERE UserID = {UserID}
    """)
        
        con.commit()
        con.close()
        return "success"
    except Exception as e:
        print("Except")

def updateProfileSettings(UserID: int, settings: common.Settings):
    """Takes a settings object and replaces a user's current settings with the new settings object"""
    con = createConnection()
    cur = con.cursor()
    try:
        cur.execute(f"""
                UPDATE Settings (Volume, Locking, WordsPerDay, CorrectColour, WrongColour, BgColour, TextColour) WHERE UserID={UserID}
                    VALUES ({settings.volume}, {settings.Locking}, {settings.WordsPerDay}, '{settings.CorrectColour}', '{settings.WrongColour}', '{settings.BgColour}', '{settings.TextColour}')
            """)
        con.commit()
        return "success"
    except Exception as e:
        print("Except")
        
    finally:
        con.close()

def updateTheoryScore(UserID: int, wordID: int, score: int):
    con = createConnection()
    cur = con.cursor()
    try:
        cur.execute(f"""
        UPDATE StudentKnowledge 
        SET Theory = {score}
        WHERE UserID = {UserID} AND WordID = {wordID}
""")
        con.commit()
        return "Success"
    except Exception as e:
        print("Except in updateTheoryScore")
                
    finally:
        con.close()

def resetVocabulary(UserID: int):
    con = createConnection()
    cur = con.cursor()

    try:
        cur.execute(f"""
        UPDATE StudentKnowledge
        SET Theory = 0, Flashcard = 0, Quiz = 0
        WHERE UserID = {UserID}
""")
        con.commit()
        return "Success"
    except Exception as e:
        print("Except")
                
    finally:
        con.close()

def updateFlashcardScore(UserID: int, wordID: int, score: int):
    con = createConnection()
    cur = con.cursor()

    try:
        currentScore = cur.execute(f"""
            SELECT Flashcard
            FROM StudentKnowledge
            WHERE UserID = {UserID} AND WordID = {wordID}
        """).fetchone()
        newscore = currentScore[0] + score
        cur.execute(f"""
        UPDATE StudentKnowledge 
        SET Flashcard = {newscore}
        WHERE UserID = {UserID} AND WordID = {wordID}""")
        con.commit()
    except Exception as e:
        print("Except in updateFlashcardScore")
                
    finally:
        con.close()

def updateQuizScore(UserID: int, wordID: int, score:int):
    con = createConnection()
    cur = con.cursor()
    try:
        cur.execute(f"""
            UPDATE StudentKnowledge 
            SET Quiz = {score}
            WHERE UserID = {UserID} AND WordID = {wordID}""")
        con.commit()
    except Exception as e:
        print("Except in updateQuizScore")
                
    finally:
        con.close()

def getWordIncorrectOptions(wordID: int, type: str):
    con = createConnection()
    cur = con.cursor()
    returnValue = []

    
    optionIDs = cur.execute(f"""
    SELECT IncorrectOptionID FROM WordIncorrectOption WHERE WordID = {wordID}
""").fetchall()
    for i in optionIDs:
        incorrectoptions = cur.execute(f"""
        SELECT Content FROM IncorrectOption WHERE ID={i[0]} AND Type = '{type}'
    """).fetchall()
        for i in incorrectoptions:
            returnValue.append(i[0])
    try:        
        return returnValue
    
    except Exception as e:
        print("Except in getWordIncorrectOptions")
                
    finally:
        con.close()

def getSong(songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        title = cur.execute(f"""
        SELECT Title FROM Song WHERE SongID = {songID}
    """).fetchone()[0]
        
        titleUnicode = cur.execute(f"""
        SELECT TitleUnicode FROM Song WHERE SongID = {songID}
    """).fetchone()[0]
        
        audioURI = cur.execute(f"""
        SELECT AudioURI FROM Song WHERE SongID = {songID}
    """).fetchone()[0]
        
        videoURI = cur.execute(f"""
        SELECT VideoURI FROM Song WHERE SongID = {songID}
    """).fetchone()[0]
        
        artist = cur.execute(f"""
        SELECT Artist FROM Song WHERE SongID = {songID}
    """).fetchone()[0]
        returnObject = common.Song(songID, title, titleUnicode, audioURI, videoURI, artist)
        return returnObject

    except Exception as e:
        print("Except in getSong")
                
    finally:
        con.close()

def getWord(wordID: int):
    con = createConnection()
    cur = con.cursor()
    
    try:
        term = cur.execute(f"""
        SELECT Term FROM Word WHERE WordID = {wordID}
    """).fetchone()[0]
        returnObject = common.Word(wordID, term)
        return returnObject
    
    except Exception as e:
        print("Except in getWord")
        
                
    finally:
        con.close()

def getTheory(wordID: int):
    con = createConnection()
    cur = con.cursor()

    try:
        theory = cur.execute(f"""
        SELECT Content FROM Theory WHERE WordID = {wordID};
    """).fetchall()
        return theory
        
    except Exception as e:
        print("Except in getTheory")
        
    finally:
        con.close()

def getUserDetails(userID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        username = cur.execute(f"""
        SELECT Username FROM Student WHERE UserID = {userID}
    """).fetchone()[0]
        
        password = cur.execute(f"""
        SELECT Password FROM Student WHERE UserID = {userID}
    """).fetchone()[0]
        
        photoURI = cur.execute(f"""
        SELECT PhotoURI FROM Student WHERE UserID = {userID}
    """).fetchone()[0]
        
        returnObject = common.Student(userID, username, password, photoURI)
        return returnObject
    except Exception as e:
        print("Except")
                
    finally:
        con.close()

def getFlashcard(wordID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        definition = cur.execute(f"""
        SELECT Definition FROM Flashcard WHERE WordID = {wordID}
    """).fetchone()[0]
        
        reading = cur.execute(f"""
        SELECT Reading FROM Flashcard WHERE WordID = {wordID}
    """).fetchone()[0]
        
        sentence = cur.execute(f"""
        SELECT Sentence FROM Flashcard WHERE WordID = {wordID}
    """).fetchone()[0]
        
        sentenceTl = cur.execute(f"""
        SELECT SentenceTranslation FROM Flashcard WHERE WordID = {wordID}
    """).fetchone()[0]
        
        returnObject = common.Flashcard(wordID, definition, reading, sentence, sentenceTl, )
        return returnObject
    except Exception as e:
        print("Except in getFlashcard")
                
    finally:
        con.close()

def getStudentVocab(UserID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        wordID = cur.execute(f"""
        SELECT WordID FROM StudentKnowledge WHERE UserID = {UserID}
    """).fetchall()
        
        theory = cur.execute(f"""
        SELECT Theory FROM StudentKnowledge WHERE UserID = {UserID}
    """).fetchall()
        
        flashcard = cur.execute(f"""
        SELECT Flashcard FROM StudentKnowledge WHERE UserID = {UserID}
    """).fetchall()

        quiz = cur.execute(f"""
        SELECT Quiz FROM StudentKnowledge WHERE UserID = {UserID}
    """).fetchall()

        reviewDate = cur.execute(f"""
        SELECT ReviewDate FROM StudentKnowledge WHERE UserID = {UserID}
    """).fetchall()
        
        returnObject = common.StudentKnowledge(UserID, wordID, theory, flashcard, quiz, reviewDate)
        return returnObject
    except Exception as e:
        print("Except")
                
    finally:
        con.close()

def getStudentSongVocab(UserID: int, songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        wordID = cur.execute(f"""
        SELECT WordID FROM StudentKnowledge WHERE UserID = {UserID} AND SongID = {songID}
    """).fetchall()
        
        theory = cur.execute(f"""
        SELECT Theory FROM StudentKnowledge WHERE UserID = {UserID} AND SongID = {songID}
    """).fetchall
        
        flashcard = cur.execute(f"""
        SELECT Flashcard FROM StudentKnowledge WHERE UserID = {UserID} AND SongID = {songID}
    """).fetchall

        quiz = cur.execute(f"""
        SELECT Quiz FROM StudentKnowledge WHERE UserID = {UserID} AND SongID = {songID}
    """).fetchall

        reviewDate = cur.execute(f"""
        SELECT ReviewDate FROM StudentKnowledge WHERE UserID = {UserID} AND SongID = {songID}
    """).fetchall
        
        returnObject = common.StudentKnowledge(UserID, wordID, theory, flashcard, quiz, reviewDate)
        return returnObject
    except Exception as e:
        print("Except")
                
    finally:
        con.close()

def getAllSongs():
    con = createConnection()
    cur = con.cursor()

    try:
        songList = cur.execute("""
            SELECT * FROM Song
        """).fetchall()
        returnList = []
        for song in songList:
            obj = common.Song(song[0], song[1], song[2], song[3], song[4], song[5])
            returnList.append(obj)
        return returnList
    except Exception as e:
        print("Except")
                
    finally:
        con.close()

def getSongLyrics(songID: int):
    con = createConnection()
    cur = con.cursor()
    returnobj = []
    try:
        lyrics = cur.execute(f"""
            SELECT WordID FROM Lyric WHERE SongID= {songID}
        """).fetchall()
        for i in lyrics:
            wordObj = getWord(i[0])
            returnobj.append(wordObj)
        return returnobj
    except Exception as e:
        print("Except")
        
                
    finally:
        con.close()

def getCurrentTheoryWord(studentID: int, songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        unleanrtWordID = cur.execute(f"""
        SELECT w.WordID
            FROM StudentKnowledge sk
            JOIN Lyric l ON sk.WordID = l.WordID
            JOIN Word w ON sk.WordID = w.WordID
        WHERE sk.Theory = 0
        AND sk.UserID = {studentID}
        AND l.SongID = {songID};

    """).fetchone()[0]
        
        unleanrtWord = getTheory(unleanrtWordID)[0][0].split(";")
        term = getWord(unleanrtWordID)

        return unleanrtWord, term
    
    except Exception as e:
        print("Except in getCurrentTheoryWord")
    finally:
        con.close()    

def getCurrentFlashcards(studentID: int, songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        flashcards = cur.execute(f"""
            SELECT DISTINCT f.WordID, f.Definition, f.Reading, f.Sentence, f.SentenceTranslation, sk.Flashcard 
                FROM StudentKnowledge sk
                JOIN Lyric l ON sk.WordID = l.WordID
                JOIN Flashcard f ON sk.WordID = f.WordID
            AND sk.UserID = {studentID}
            AND l.songID = {songID}
            AND sk.Theory = 1;
    """).fetchall()
        
        returnArray = []

        for i in flashcards:
            returnArray.append(common.Flashcard(wordID=i[0], definition=i[1], reading=i[2], sentence=i[3], sentenceTl=i[4], score=i[5]))
        
        return returnArray
    except Exception as e:
        print("Except")
        
    finally:
        con.close()

def getQuizWords(studentID: int, songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        unleanrtWord = cur.execute(f"""
        SELECT DISTINCT w.WordID
            FROM StudentKnowledge sk
            JOIN Word w ON sk.WordID = w.WordID
            JOIN Lyric l ON sk.WordID = l.WordID
        WHERE sk.Theory = 1
        AND sk.Flashcard >= 1
        AND sk.UserID = {studentID}
        AND l.SongID = {songID};
    """).fetchall()
        idArray = []
        returnArray = []
        for i in unleanrtWord:
            idArray.append(i[0])
        for i in idArray:
            returnArray.append(getWord(i))
        return returnArray
    
    except Exception as e:
        print("Except in getQuizWords")
        
    finally:
        con.close()    

def getWordFromDefinition(definition: str):
    con = createConnection()
    cur = con.cursor()
    try:
        wordID = cur.execute(f"""
        SELECT WordID FROM Flashcard WHERE Definition = ?
    """, (definition,)).fetchone()[0]
        returnObject = getWord(wordID)
        return returnObject
    
    except Exception as e:
        print("Except in getWordFromDefinition")
        
        print(e)
    finally:
        con.close()

def getWordFromTerm(term: str):
    con = createConnection()
    cur = con.cursor()
    try:
        wordID = cur.execute(f"""
        SELECT WordID FROM Word WHERE Term = ?
    """, (term,)).fetchone()[0]
        returnObject = getWord(wordID)
        return returnObject
    
    except Exception as e:
        print("Except in getWordFromTerm")
        
                
    finally:
        con.close()

def getSongFromTitle(title: str):
    con = createConnection()
    cur = con.cursor()
    try:
        song = cur.execute(f"""
        SELECT SongID FROM Song WHERE title = ?
    """, (title,)).fetchone()[0]

        return getSong(song)
    
    except Exception as e:
        print("Except in getSongFromTitle")
        
                
    finally:
        con.close()

def getFullLyrics(songID: int):
    con = createConnection()
    cur = con.cursor()
    try:
        lyrics = cur.execute(f"""
        SELECT Lyrics FROM FullSongLyrics WHERE SongID = {songID}
    """).fetchone()[0]

        return lyrics
    
    except Exception as e:
        print("Except in getFullLyrics")        
    finally:
        con.close()

def getLearntWords(studentID: int, songID:int):
    con = createConnection()
    cur = con.cursor()
    try:
        unleanrtWord = cur.execute(f"""
        SELECT DISTINCT w.WordID
            FROM StudentKnowledge sk
            JOIN Word w ON sk.WordID = w.WordID
            JOIN Lyric l ON sk.WordID = l.WordID
        WHERE sk.Theory = 1
        AND sk.Flashcard >= 1
        AND sk.Quiz >= 1
        AND sk.UserID = {studentID}
        AND l.SongID = {songID};
    """).fetchall()
        idArray = []
        returnArray = []
        for i in unleanrtWord:
            idArray.append(i[0])
        for i in idArray:
            returnArray.append(getWord(i))
        return returnArray
    
    except Exception as e:
        print("Except in getLearntWords")
    finally:
        con.close()  

