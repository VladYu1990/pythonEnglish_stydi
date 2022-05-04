# в функции read_new_question попробовать вытянуть все данные по вопросу и вреному ответу за 1 раз

# попробовать разнести функции/классы по разным файлам
# поработать  над цветовой палитрой
# сделать настройки с переключением светлой темы и темной темы
#


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3
from datetime import datetime, timedelta
import datetime
import random
import difflib

now = datetime.datetime.now()
today = str(now.date())

number_of_attempts = 1
number_true_attempts = 1
learned = 1
a = 0
Ans1 = 0
Ans2 = 0
Ans3 = 0
Ans4 = 0
t = '12345'
theme = 0 # 0 - темная,1 светлая, 2 серая, 3 желтая

id_word = '2'
#Question_word = 'вопрос'
#Ans1_correct_resp = 'правильный ответ'
#Ans2_resp = 'не верный 2'
#Ans3_resp = 'не верный 3'
#Ans4_resp = 'не верный 4'
Rand = 0
tap = 0
background_color_clear = [0.4, 0.4, 0.4, 0.4]
background_color_correct = [0, 1, 0, 1]
background_color_incorrect = [1, 0, 0, 1]



class db:
    def create_db(self):
        self.conn = sqlite3.connect('file_db.db')
        self.c = self.conn.cursor()
        self.c.execute(
            'create table if not exists '
            'words'
            '   (id integer primary key,'
            '   word text,'
            '   translation text,'
            '   date_last_read integer,'
            '   date_next_read integer,'
            '   date_last_true integer,'
            '   learned integer,'
            '   number_of_attempts integer,'
            '   number_true_attempts integer)'
        )
        self.conn.commit()

    def add_word(self, word, translation):
        global today
        global now
        date_last_read = now
        date_next_read = now
        number_of_attempts = 0
        number_true_attempts = 0
        self.conn = sqlite3.connect('file_db.db')
        self.c = self.conn.cursor()
        self.c.execute(
            'insert into words('
            'word,'
            'translation,'
            'date_last_read,'
            'date_next_read,'
            'date_last_true,'
            'learned,'
            'number_of_attempts,'
            'number_true_attempts) values (?,?,?,?,0,0,0,0)''',
            (word, translation, date_last_read, date_next_read))
        self.conn.commit()

    def read_new_question(self):  # тут будем формировать вопрос и ответы к нему
        global id_word

        self.conn = sqlite3.connect('file_db.db')
        self.c = self.conn.cursor()

        id_word = self.c.execute('select id from words order by date_next_read limit 1')
        id_word = self.rep_lib(id_word.fetchall())

        Question_word = self.c.execute('select word from words where id = :id_word order by date_next_read limit 1',{'id_word':id_word})
        Question_word = self.rep_lib(Question_word.fetchall())

        Ans1_correct_resp = self.c.execute('select translation from words where id = :id_word order by date_next_read limit 1',{'id_word':id_word})
        Ans1_correct_resp = self.rep_lib(Ans1_correct_resp.fetchall())
        print(Ans1_correct_resp)

        incorr_answers = self.c.execute('select translation from words where id <> :id_word',{'id_word':id_word})
        rows = incorr_answers.fetchall()

        matrix = [[0 for x in '22'] for y in rows]
        count = 0

        for i in rows:
            Ans1_correct_resp = str(Ans1_correct_resp)
            i = self.rep_lib(i)
            matcher = difflib.SequenceMatcher(None, Ans1_correct_resp, i)
            matrix[count][0] = i
            matrix[count][1] = matcher.ratio()
            count = count + 1


        matrix.sort(key = lambda x: x[1], reverse=True)
        Ans2_resp = matrix[0][0] # не попорядку специально
        Ans4_resp = matrix[1][0]
        Ans3_resp = matrix[2][0]

        return (Question_word,Ans1_correct_resp,Ans2_resp,Ans4_resp,Ans3_resp)


    def correct_response(self):  # если ответ был верным
        global now

        Counts = self.c.execute('select number_of_attempts, number_true_attempts from words where id = :id_word order by date_next_read limit 1',{'id_word':id_word})
        Counts = Counts.fetchone()
        number_of_attempts = Counts[0]
        number_true_attempts = Counts[1]

        if number_true_attempts == 0:  # через 2 часа можно
            days_next = now + timedelta(hours=2)
        elif number_true_attempts == 1:  # через день
            days_next = now + timedelta(days=1)
        elif number_true_attempts == 2:  # через 3 дня
            days_next = now + timedelta(days=3)
        elif number_true_attempts == 3:  # 7 дней
            days_next = now + timedelta(days=7)
        elif number_true_attempts > 3:  # 14 дней
            days_next = now + timedelta(days=14)

        number_of_attempts = number_of_attempts + 1
        number_true_attempts = number_true_attempts + 1

        if number_true_attempts > 4:
            learned = 1
        else:
            learned = 0

        self.conn = sqlite3.connect('file_db.db')
        self.c = self.conn.cursor()




        print(number_of_attempts, number_true_attempts)
        self.c.execute(
            """UPDATE words 
            SET date_last_read = ?,
            date_next_read = ? ,
            date_last_true = ?,
            learned = ?,
            number_of_attempts = ?,
            number_true_attempts = ?
            WHERE id = :id_word""",
            (now, days_next, now, learned, number_of_attempts, number_true_attempts, id_word))
        self.conn.commit()
        print('correct')

    def incorrect_response(self):  # если ответ был не верным
        global now
        global id_word

        Counts = self.c.execute('select number_of_attempts, number_true_attempts from words where id = :id_word order by date_next_read limit 1',{'id_word':id_word})
        Counts = Counts.fetchone()
        number_of_attempts = Counts[0]

        number_of_attempts = number_of_attempts + 1
        days_next = now + timedelta(minutes=15)

        self.conn = sqlite3.connect('file_db.db')
        self.c = self.conn.cursor()
        self.c.execute(
            """UPDATE words 
            SET date_last_read = ?,
            date_next_read = ? ,
            number_of_attempts = ?,
            number_true_attempts = 0
            WHERE id = :id_word""",
            (now, days_next, number_of_attempts, id_word))
        self.conn.commit()
        print('wrong')

class Screen1(Screen):
    def paint(self):
        pass

    def rep_lib(self, str1):
        str1 = str(str1)
        lib = ['(',')',',','"','\'','[',']']
        for i in lib:
            str1 = str1.replace(i, '')
        return str1

    def new_question(self):
        # db.qet_answer_and_question #создать функцию возврашает массив 1 - вопрос 2 - верный ответ 3-5 не верные ответы
        d = db.read_new_question(self)
        print(d)
        global Rand
        Question_word = d[0]
        Ans1_correct_resp = d[1]
        Ans2_resp = d[2]
        Ans3_resp = d[3]
        Ans4_resp = d[4]


        self.answer1.background_color = background_color_clear
        self.answer2.background_color = background_color_clear
        self.answer3.background_color = background_color_clear
        self.answer4.background_color = background_color_clear
        self.question.text = Question_word
        print(a)
        Rand = random.randint(1, 4)
        if Rand == 1:
            self.answer1.text = Ans1_correct_resp
            self.answer2.text = Ans2_resp
            self.answer3.text = Ans3_resp
            self.answer4.text = Ans4_resp
        elif Rand == 2:
            self.answer1.text = Ans2_resp
            self.answer2.text = Ans1_correct_resp
            self.answer3.text = Ans3_resp
            self.answer4.text = Ans4_resp
        elif Rand == 3:
            self.answer1.text = Ans3_resp
            self.answer2.text = Ans2_resp
            self.answer3.text = Ans1_correct_resp
            self.answer4.text = Ans4_resp
        elif Rand == 4:
            self.answer1.text = Ans4_resp
            self.answer2.text = Ans2_resp
            self.answer3.text = Ans3_resp
            self.answer4.text = Ans1_correct_resp
        else:
            sys.exit()

    def check_response(self, num, a):
        global Rand
        global background_color_correct
        global background_color_incorrect
        num = num
        a = a
        if Rand == num:
            a.background_color = background_color_correct
            db.correct_response(self)
        else:
            a.background_color = background_color_incorrect
            db.incorrect_response(self)
            if Rand == 1:
                self.answer1.background_color = background_color_correct
            elif Rand == 2:
                self.answer2.background_color = background_color_correct
            elif Rand == 3:
                self.answer3.background_color = background_color_correct
            elif Rand == 4:
                self.answer4.background_color = background_color_correct
            else:
                print('ой')

    def question_formation(self):
        global Ans1
        global Ans2
        global Ans3
        global Ans4
        self.question.text = str(test_text)
        self.answer1.text = 'быть'
        self.answer2.text = 'не быть'
        self.answer3.text = 'это ли вопрос?'
        self.answer4.text = 'это не вопрос!'
        Ans1 = 1
        Ans2 = 0
        Ans3 = 0
        Ans4 = 0


class Screen2(Screen):
    pass


class Screen_add(Screen):

    def clear_input(self):
        self.screen_add_input_english_word.text = 'add_English_word'
        self.screen_add_input_translation.text = 'add_translation'

    def add_db_word(self):
        wordE = self.screen_add_input_english_word.text
        wordT = self.screen_add_input_translation.text
        print(wordE)
        print(wordT)
        db.add_word(self, wordE, wordT)


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my1.kv")


class MyApp(App):
    def build(self):
        # Screen1.def_test(Screen1)
        return kv


if __name__ == "__main__":
    MyApp().run()
