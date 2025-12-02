from tkinter import ttk, messagebox
import tkinter as tk
import requests

API_BASE = "http://127.0.0.1:5000"

class Session4UsersFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        reg = ttk.Frame(notebook)
        login = ttk.Frame(notebook)
        profile = ttk.Frame(notebook)

        notebook.add(reg, text="Register")
        notebook.add(login, text="Login")
        notebook.add(profile, text="Profile")

        # Register
        self.reg_email = tk.StringVar()
        self.reg_pwd = tk.StringVar()
        self.reg_fname = tk.StringVar()
        self.reg_lname = tk.StringVar()
        self.reg_sub = tk.BooleanVar()

        for text, var in [("First name", self.reg_fname),
                          ("Last name", self.reg_lname),
                          ("Email", self.reg_email),
                          ("Password", self.reg_pwd)]:
            row = ttk.Frame(reg); row.pack(fill="x", pady=2)
            ttk.Label(row, text=text+":").pack(side="left", padx=5)
            ttk.Entry(row, textvariable=var, show="*" if text=="Password" else "").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Checkbutton(reg, text="Subscribe to mailing list", variable=self.reg_sub).pack(anchor="w", padx=10, pady=5)
        ttk.Button(reg, text="Register", command=self.do_register).pack(padx=10, pady=5)

        # Login
        self.login_email = tk.StringVar()
        self.login_pwd = tk.StringVar()
        for text, var in [("Email", self.login_email), ("Password", self.login_pwd)]:
            row = ttk.Frame(login); row.pack(fill="x", pady=2)
            ttk.Label(row, text=text+":").pack(side="left", padx=5)
            ttk.Entry(row, textvariable=var, show="*" if text=="Password" else "").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(login, text="Login", command=self.do_login).pack(padx=10, pady=5)

        # Profile
        self.current_user_id = tk.StringVar()
        self.prof_email = tk.StringVar()
        self.prof_fname = tk.StringVar()
        self.prof_lname = tk.StringVar()
        self.prof_phone = tk.StringVar()

        row = ttk.Frame(profile); row.pack(fill="x", pady=2)
        ttk.Label(row, text="User ID:").pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.current_user_id).pack(side="left", padx=5)
        ttk.Button(row, text="Load", command=self.load_profile).pack(side="left", padx=5)

        for text, var in [("Email", self.prof_email),
                          ("First name", self.prof_fname),
                          ("Last name", self.prof_lname),
                          ("Phone", self.prof_phone)]:
            r = ttk.Frame(profile); r.pack(fill="x", pady=2)
            ttk.Label(r, text=text+":").pack(side="left", padx=5)
            ttk.Entry(r, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(profile, text="Save", command=self.save_profile).pack(padx=10, pady=5)

    def do_register(self):
        data = {
            "email": self.reg_email.get(),
            "password": self.reg_pwd.get(),
            "first_name": self.reg_fname.get(),
            "last_name": self.reg_lname.get(),
            "mailing_list": self.reg_sub.get(),
        }
        try:
            r = requests.post(f"{API_BASE}/api/register", json=data)
            if r.ok:
                uid = r.json()["id"]
                messagebox.showinfo("OK", f"Registered user id={uid}")
                self.current_user_id.set(str(uid))
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_login(self):
        try:
            r = requests.post(f"{API_BASE}/api/login", json={
                "email": self.login_email.get(),
                "password": self.login_pwd.get()
            })
            if r.ok:
                uid = r.json()["user_id"]
                self.current_user_id.set(str(uid))
                messagebox.showinfo("OK", f"Logged in as id={uid}")
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_profile(self):
        uid = self.current_user_id.get()
        try:
            r = requests.get(f"{API_BASE}/api/profile", params={"user_id": uid})
            if r.ok:
                data = r.json()
                self.prof_email.set(data["email"])
                self.prof_fname.set(data["first_name"])
                self.prof_lname.set(data["last_name"])
                self.prof_phone.set(data.get("phone",""))
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_profile(self):
        uid = self.current_user_id.get()
        data = {
            "id": uid,
            "email": self.prof_email.get(),
            "first_name": self.prof_fname.get(),
            "last_name": self.prof_lname.get(),
            "phone": self.prof_phone.get(),
        }
        try:
            r = requests.put(f"{API_BASE}/api/profile", json=data)
            if r.ok:
                messagebox.showinfo("OK", "Profile updated")
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))
