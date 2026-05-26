import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# 데이터 저장 파일 경로
DATA_FILE = "tasks.json"

class AssignmentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("수행평가 일정 관리자")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        
        # 데이터 로드
        self.tasks = self.load_data()
        
        # UI 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 입력 프레임
        input_frame = ttk.LabelFrame(root, text=" 새로운 수행평가 추가 ", padding=10)
        input_frame.pack(fill="x", padx=15, pady=10)
        
        # 과목명 입력
        ttk.Label(input_frame, text="과목명:").grid(row=0, column=0, sticky="w", padx=5)
        self.subject_entry = ttk.Entry(input_frame, width=15)
        self.subject_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 과제 내용 입력
        ttk.Label(input_frame, text="수행 내용:").grid(row=0, column=2, sticky="w", padx=5)
        self.content_entry = ttk.Entry(input_frame, width=25)
        self.content_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 마감일 입력
        ttk.Label(input_frame, text="마감일 (MM-DD):").grid(row=1, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 추가 버튼
        add_btn = ttk.Button(input_frame, text="추가하기", command=self.add_task)
        add_btn.grid(row=1, column=2, columnspan=2, sticky="e", padx=5, pady=5)
        
        # 리스트 출력 프레임
        list_frame = ttk.Frame(root, padding=10)
        list_frame.pack(fill="both", expand=True, padx=15)
        
        # 표(Treeview) 생성
        columns = ("subject", "content", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True)
        
        # 각 컬럼 헤더 및 너비 설정
        self.tree.heading("subject", text="과목")
        self.tree.heading("content", text="수행평가 내용")
        self.tree.heading("date", text="마감일")
        
        self.tree.column("subject", width=100, anchor="center")
        self.tree.column("content", width=250, anchor="w")
        self.tree.column("date", width=100, anchor="center")
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # 하단 컨트롤 버튼
        btn_frame = ttk.Frame(root, padding=10)
        btn_frame.pack(fill="x", padx=15)
        
        del_btn = ttk.Button(btn_frame, text="선택 항목 삭제", command=self.delete_task)
        del_btn.pack(side="right", padx=5)
        
        # 초기 데이터 표에 뿌리기
        self.update_treeview()

    # 데이터 불러오기 (에러 방지 예외처리 포함)
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return [] # 파일이 깨져있으면 빈 리스트 반환
        return []

    # 데이터 저장하기
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 중 에러가 발생했습니다: {e}")

    # 표 갱신
    def update_treeview(self):
        # 기존 내용 싹 비우기
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 마감일 순으로 정렬해서 출력
        sorted_tasks = sorted(self.tasks, key=lambda x: x['date'])
        for idx, task in enumerate(sorted_tasks):
            self.tree.insert("", "end", iid=idx, values=(task["subject"], task["content"], task["date"]))

    # 일정 추가 기능
    def add_task(self):
        subject = self.subject_entry.get().strip()
        content = self.content_entry.get().strip()
        date = self.date_entry.get().strip()
        
        # 빈칸 입력 에러 방지 방어 코드
        if not subject or not content or not date:
            messagebox.showwarning("입력 확인", "모든 칸을 채워주세요!")
            return
            
        # 데이터 추가 및 저장
        new_task = {"subject": subject, "content": content, "date": date}
        self.tasks.append(new_task)
        self.save_data()
        self.update_treeview()
        
        # 입력창 초기화
        self.subject_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        messagebox.showinfo("성공", "수행평가 일정이 추가되었습니다.")

    # 일정 삭제 기능
    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("선택 확인", "삭제할 항목을 리스트에서 선택해주세요!")
            return
            
        # 선택된 행의 데이터 가져오기
        item_values = self.tree.item(selected_item[0])["values"]
        
        # 원래 리스트에서 찾아 삭제 (동일 데이터가 있을 수 있으니 조건 매칭)
        for task in self.tasks:
            if task["subject"] == item_values[0] and task["content"] == item_values[1] and task["date"] == str(item_values[2]):
                self.tasks.remove(task)
                break
                
        self.save_data()
        self.update_treeview()
        messagebox.showinfo("성공", "선택한 일정이 삭제되었습니다.")

# 프로그램 시작
if __name__ == "__main__":
    root = tk.Tk()
    app = AssignmentManager(root)
    root.mainloop()
