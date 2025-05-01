import tkinter as tk
from tkinter import scrolledtext
import json
import os
from openai import OpenAI
import threading
import time

# Настройка клиента OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Переменные для памяти
memory_enabled = True  # Память всегда включена
chat_memory = []  # ОЗУ память
memory_file = "memory.json"

# Инициализация файла памяти при запуске
if not os.path.exists(memory_file):
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4, ensure_ascii=False)

# Функция отправки сообщения
def send_message(event=None):
    user_message = user_input.get()
    if user_message.strip() == "":
        return

    chat_history.configure(state='normal')
    chat_history.insert(tk.END, f"Вы: {user_message}\n", "user")
    chat_history.configure(state='disabled')
    chat_history.yview(tk.END)

    user_input.delete(0, tk.END)

    # Поток для обработки запроса
    threading.Thread(target=get_ai_response, args=(user_message,)).start()

# Функция получения ответа от OpenRouter
def get_ai_response(user_message):
    chat_history.configure(state='normal')
    chat_history.insert(tk.END, "NOUS думает...\n", "nous_thinking")
    chat_history.configure(state='disabled')
    chat_history.yview(tk.END)

    try:
        # Собираем сообщения для памяти
        messages = []
        with open(memory_file, "r", encoding="utf-8") as f:
            saved_dialogues = json.load(f)
            for dialogue in saved_dialogues[-5:]:  # Последние 5 диалогов
                messages.append({"role": "user", "content": dialogue["user"]})
                messages.append({"role": "assistant", "content": dialogue["nous"]})
        
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            extra_body={},
            model="microsoft/mai-ds-r1:free",
            messages=messages
        )
        ai_response = response.choices[0].message.content

        # Удалить "думает..."
        chat_history.configure(state='normal')
        chat_history.delete("end-2l", "end-1l")

        # Плавный вывод ответа
        chat_history.insert(tk.END, "NOUS: ", "nous_name")
        for char in ai_response:
            chat_history.insert(tk.END, char, "nous_text")
            chat_history.yview(tk.END)
            chat_history.update()
            time.sleep(0.02)
        chat_history.insert(tk.END, "\n")
        chat_history.configure(state='disabled')
        chat_history.yview(tk.END)

        # Сохраняем в память
        chat_memory.append({"user": user_message, "nous": ai_response})
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(chat_memory, f, indent=4, ensure_ascii=False)

    except Exception as e:
        chat_history.configure(state='normal')
        chat_history.insert(tk.END, f"\nОшибка: {e}\n", "error")
        chat_history.configure(state='disabled')

# Создание GUI
root = tk.Tk()
root.title("NOUS - ИИ Чат")

root.configure(bg="#1e1e1e")

# Верхняя панель
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=10)

# Заголовок
title = tk.Label(top_frame, text="NOUS", fg="#00aaff", bg="#1e1e1e", font=("Helvetica", 24, "bold"))
title.pack(side=tk.LEFT, padx=10)

# Окно чата
chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25, bg="#2d2d2d", fg="white", font=("Helvetica", 12))
chat_history.pack(padx=10, pady=10)
chat_history.tag_config("user", foreground="#cccccc")
chat_history.tag_config("nous_thinking", foreground="#8888ff")
chat_history.tag_config("nous_name", foreground="#00aaff", font=("Helvetica", 12, "bold"))
chat_history.tag_config("nous_text", foreground="#ffffff")
chat_history.tag_config("error", foreground="red")
chat_history.configure(state='disabled')

# Поле ввода
user_input = tk.Entry(root, width=50, bg="#2d2d2d", fg="white", insertbackground="white", font=("Helvetica", 12))
user_input.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))
user_input.bind("<Return>", send_message)  # Enter для отправки

# Кнопка отправить
send_button = tk.Button(root, text="Отправить", command=send_message, bg="#00aaff", fg="white", font=("Helvetica", 12, "bold"))
send_button.pack(side=tk.LEFT, padx=(5, 10), pady=(0, 10))

root.mainloop()
