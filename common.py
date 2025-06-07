import datetime

class Settings():
    def __init__(self, studentID: int, volume: int, locking: int, dailywords: int, correctcolour: str, incorrectcolour: str, bgcolour: str, textcolour: str):
        self.studentID = studentID
        self.volume = volume
        self.locking = locking
        self.dailywords = dailywords
        self.correctcolour = correctcolour
        self.incorrectcolour = incorrectcolour
        self.bgcolour = bgcolour
        self.textcolour = textcolour

class Song():
    def __init__(self, songID: int, title: str, titleUnicode: str, audioURI:str, videoURI:str, artist:str):
        self.songID = songID
        self.title = title
        self.titleUnicode = titleUnicode
        self.audioURI = audioURI
        self.videoURI = videoURI
        self.artist = artist

class Word():
    def __init__(self, wordID: int, term: str):
        self.wordID = wordID
        self.term = term
    def __str__(self):
        return self.term
class Theory():
    def __init__(self, content: str):
        self.content = content

class Student(UserMixin):
    def __init__(self, studentID: int, username: str, password: str, photoURI: str):
        self.studentID = studentID
        self.username = username
        self.password = password
        self.photoURI = photoURI

class StudentKnowledge():
    def __init__(self, studentID: int, wordID: int, theory: int, flashcard: int, quiz: int, reviewdate: datetime.date):
        self.studentID = studentID
        self.wordID = wordID
        self.theory = theory
        self.flashcard = flashcard
        self.quiz = quiz
        self.reviewdate = reviewdate

class Flashcard():
    def __init__(self, wordID: int, definition: str, reading: str, sentence: str, sentenceTl: str, score = 0):
        self.wordID = wordID
        self.definition = definition
        self.reading = reading
        self.sentence = sentence
        self.sentenceTl = sentenceTl
        self.score = score