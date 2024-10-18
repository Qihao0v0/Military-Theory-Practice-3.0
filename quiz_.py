import sqlite3
import os

def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS 和 Linux
        os.system('clear')

def wait():
    input('按Enter继续')

def create_save_db():
    conn = sqlite3.connect('save.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS radio_results (
            id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkbox_results (
            id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tof_results (
            id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

def get_questions():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, question, answer, option_1, option_2, option_3, option_4, option_5 FROM radio_data')
    radio_questions = cursor.fetchall()

    cursor.execute('SELECT id, question, answer, option_1, option_2, option_3, option_4, option_5 FROM checkbox_data')
    checkbox_questions = cursor.fetchall()

    cursor.execute('SELECT id, question, answer FROM tof_data')
    tof_questions = cursor.fetchall()

    conn.close()
    
    return radio_questions, checkbox_questions, tof_questions

def update_save_db(conn, question_type, question_id, correct):
    cursor = conn.cursor()
    if question_type == 'radio':
        if correct:
            cursor.execute('''
                INSERT INTO radio_results (id, correct_count) VALUES (?, 1)
                ON CONFLICT(id) DO UPDATE SET correct_count = correct_count + 1
            ''', (question_id,))
        else:
            cursor.execute('''
                INSERT INTO radio_results (id, correct_count) VALUES (?, 0)
                ON CONFLICT(id) DO UPDATE SET correct_count = 0
            ''', (question_id,))
    elif question_type == 'checkbox':
        if correct:
            cursor.execute('''
                INSERT INTO checkbox_results (id, correct_count) VALUES (?, 1)
                ON CONFLICT(id) DO UPDATE SET correct_count = correct_count + 1
            ''', (question_id,))
        else:
            cursor.execute('''
                INSERT INTO checkbox_results (id, correct_count) VALUES (?, 0)
                ON CONFLICT(id) DO UPDATE SET correct_count = 0
            ''', (question_id,))
    elif question_type == 'tof':
        if correct:
            cursor.execute('''
                INSERT INTO tof_results (id, correct_count) VALUES (?, 1)
                ON CONFLICT(id) DO UPDATE SET correct_count = correct_count + 1
            ''', (question_id,))
        else:
            cursor.execute('''
                INSERT INTO tof_results (id, correct_count) VALUES (?, 0)
                ON CONFLICT(id) DO UPDATE SET correct_count = 0
            ''', (question_id,))
    conn.commit()

def normalize_answer(user_input):
    user_input = user_input.upper()
    
    normalized = ""
    for char in user_input:
        if char.isdigit():
            num = int(char)
            if 1 <= num <= 26:
                normalized += chr(num + 64)  
            else:
                normalized += char  
        else:
            normalized += char
    return normalized

def display_options(options):
    for i, option in enumerate(options, start=1):
        if option:
            print(f"{i}. {option}")

def main():
    save_conn = create_save_db()
    radio_questions, checkbox_questions, tof_questions = get_questions()
    print("Military-Theory-Practice-3.0")
    print("制作由：欣奇好")
    print("github.com/Qihao0v0/Military-Theory-Practice-3.0")
    print("——————————————")
    print("请选择题目类型:")
    print("1. 单选题")
    print("2. 多选题")
    print("3. 判断题")
    print("4. 全部练习")
    print("——————————————")
    choice = input("请输入选项（1-4）: ")

    skip_threshold = int(input("请输入跳过正确次数的阈值（例如输入3跳过已正确3次的题目）: "))

    all_questions = []
    if choice == '1':
        all_questions = [(qid, qtext, answer, 'radio', options) for qid, qtext, answer, *options in radio_questions]
    elif choice == '2':
        all_questions = [(qid, qtext, answer, 'checkbox', options) for qid, qtext, answer, *options in checkbox_questions]
    elif choice == '3':
        all_questions = [(qid, qtext, answer, 'tof') for qid, qtext, answer in tof_questions]
    elif choice == '4':
        all_questions = [
            (qid, qtext, answer, 'radio', options) for qid, qtext, answer, *options in radio_questions
        ] + [
            (qid, qtext, answer, 'checkbox', options) for qid, qtext, answer, *options in checkbox_questions
        ] + [
            (qid, qtext, answer, 'tof') for qid, qtext, answer in tof_questions
        ]
    else:
        print("无效选项，程序退出。")
        wait()
        return

    for question in all_questions:
        clear_screen()
        question_id, question_text, answer, qtype = question[:4]
        options = question[4] if len(question) > 4 else []

        cursor = save_conn.cursor()
        cursor.execute(f'SELECT correct_count FROM {qtype}_results WHERE id = ?', (question_id,))
        result = cursor.fetchone()
        correct_count = result[0] if result else 0

        if correct_count >= skip_threshold:
            print(f"题目 {question_id} 已正确过{skip_threshold}次，跳过该题。")
            wait()
            continue

        print(f"题目 {question_id} ({qtype}): {question_text}")
        if qtype in ['radio', 'checkbox']:
            display_options(options)

        user_input = input("请输入答案: ")

        normalized_input = normalize_answer(user_input)

        if qtype == 'radio' or qtype == 'checkbox':
            if normalized_input.strip() == answer.strip():
                print("正确！")
                update_save_db(save_conn, qtype, question_id, correct=True)
                wait()
            else:
                print(f"错误！正确答案是: {answer}")
                update_save_db(save_conn, qtype, question_id, correct=False)
                wait()

        elif qtype == 'tof':
            if normalized_input.strip() in ['对', '1', 'A']:
                correct_answer = '对'
            elif normalized_input.strip() in ['错', '2', 'B']:
                correct_answer = '错'
            else:
                print(f"无效输入！正确答案是: {answer}")
                wait()
                continue  

            if correct_answer == answer:
                print("正确！")
                update_save_db(save_conn, qtype, question_id, correct=True)
                wait()
            else:
                print(f"错误！正确答案是: {answer}")
                update_save_db(save_conn, qtype, question_id, correct=False)
                wait()

    save_conn.close()

if __name__ == '__main__':
    main()
