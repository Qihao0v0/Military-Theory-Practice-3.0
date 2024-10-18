import sqlite3
import os

def clear_screen():
    # 判断操作系统并执行相应的清屏命令
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS 和 Linux
        os.system('clear')

def wait():
    input('按Enter继续')

def create_save_db():
    """创建或连接到save_old.db数据库，确保其存在。"""
    conn = sqlite3.connect('save_old.db')
    cursor = conn.cursor()
    # 创建表格用于保存每个题目的正确情况
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

def get_questions():
    """从questions.db中获取所有题目和答案。"""
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, question_text, answer FROM questions')
    questions = cursor.fetchall()
    conn.close()
    return questions

def update_save_db(conn, question_id, correct):
    """更新save_old.db中每个题目的正确情况。"""
    cursor = conn.cursor()
    if correct:
        cursor.execute('''
            INSERT INTO results (id, correct_count) VALUES (?, 1)
            ON CONFLICT(id) DO UPDATE SET correct_count = correct_count + 1
        ''', (question_id,))
    else:
        cursor.execute('''
            INSERT INTO results (id, correct_count) VALUES (?, 0)
            ON CONFLICT(id) DO UPDATE SET correct_count = 0
        ''', (question_id,))
    conn.commit()

def normalize_answer(user_input):
    """规范化用户输入，处理大小写和数字对应。"""
    # 转换为大写
    user_input = user_input.upper()
    
    # 将数字转换为对应的字母
    normalized = ""
    for char in user_input:
        if char.isdigit():
            num = int(char)
            # 转换数字为对应的字母，1 -> A, 2 -> B, ..., 26 -> Z
            if 1 <= num <= 26:
                normalized += chr(num + 64)  # ASCII 65是A
            else:
                normalized += char  # 超出范围的数字直接加入
        else:
            normalized += char
    return normalized

def main():
    save_conn = create_save_db()
    questions = get_questions()

    for question_id, question_text, answer in questions:
        clear_screen()
        # 检查该题目是否已正确过3次
        cursor = save_conn.cursor()
        cursor.execute('SELECT correct_count FROM results WHERE id = ?', (question_id,))
        result = cursor.fetchone()
        correct_count = result[0] if result else 0

        if correct_count >= 3:
            print(f"题目 {question_id} 已正确过3次，跳过该题。")
            continue

        # 显示题目并获取用户输入
        user_input = input(f"题目 {question_id}: {question_text}\n请输入答案: ")

        # 规范化用户输入
        normalized_input = normalize_answer(user_input)

        # 判断用户输入
        if normalized_input.strip() == answer.strip():
            print("正确！")
            update_save_db(save_conn, question_id, correct=True)
        else:
            print(f"错误！正确答案是: {answer}")
            update_save_db(save_conn, question_id, correct=False)
            input('按Enter继续')

    save_conn.close()

if __name__ == '__main__':
    main()
