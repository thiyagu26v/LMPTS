"""Main Tkinter application window with MVC architecture."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from lmpts.gui.controllers import (
    AdminController,
    AnalyticsController,
    LearnerController,
    PathController,
)
from lmpts.services.container import ServiceContainer

# Professional color scheme
COLORS = {
    "bg": "#f5f6fa",
    "header": "#2c3e50",
    "accent": "#3498db",
    "success": "#27ae60",
    "error": "#e74c3c",
    "card": "#ffffff",
    "text": "#2c3e50",
}


class LMPTSApplication:
    """Main application window (FR7)."""

    def __init__(self, container: ServiceContainer) -> None:
        self.container = container
        self.root = tk.Tk()
        self.root.title("LMPTS - Learning Management & Prerequisite Tracking System")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])

        self.admin_ctrl = AdminController(container)
        self.learner_ctrl = LearnerController(container, self._refresh_all)
        self.analytics_ctrl = AnalyticsController(container)
        self.path_ctrl = PathController(container)

        self._status_var = tk.StringVar(value="Ready")
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLORS["header"])
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TButton", padding=6, font=("Segoe UI", 9))
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("TEntry", font=("Segoe UI", 9))

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=COLORS["header"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="Learning Management & Prerequisite Tracking System",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=COLORS["header"],
        ).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(
            header,
            text="Capstone Project | Suganthan S",
            font=("Segoe UI", 10),
            fg="#bdc3c7",
            bg=COLORS["header"],
        ).pack(side=tk.RIGHT, padx=20)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_admin_tab()
        self._build_learner_tab()
        self._build_path_tab()
        self._build_analytics_tab()

        status_bar = tk.Frame(self.root, bg=COLORS["header"], height=28)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        tk.Label(
            status_bar,
            textvariable=self._status_var,
            font=("Segoe UI", 9),
            fg="white",
            bg=COLORS["header"],
            anchor=tk.W,
        ).pack(fill=tk.X, padx=10, pady=4)

    def _set_status(self, message: str, is_error: bool = False) -> None:
        self._status_var.set(message)
        if is_error:
            messagebox.showerror("Error", message)

    def _refresh_all(self) -> None:
        self._refresh_courses_table()
        self._refresh_learners()
        self._refresh_analytics()

    # ---- Admin Tab ----
    def _build_admin_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Admin Panel")

        left = ttk.LabelFrame(frame, text="Course Management", padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        fields = [
            ("Code", "course_code"),
            ("Name", "course_name"),
            ("Description", "course_desc"),
            ("Difficulty", "course_diff"),
            ("Duration (hrs)", "course_duration"),
            ("Instructor", "course_instructor"),
        ]
        self.admin_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(left, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            if key == "course_diff":
                var = tk.StringVar(value="beginner")
                cb = ttk.Combobox(
                    left,
                    textvariable=var,
                    values=["beginner", "intermediate", "advanced", "expert"],
                    width=28,
                )
                cb.grid(row=i, column=1, pady=2, sticky=tk.EW)
            else:
                var = tk.StringVar()
                ttk.Entry(left, textvariable=var, width=30).grid(
                    row=i, column=1, pady=2, sticky=tk.EW
                )
            self.admin_vars[key] = var

        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Create Course", command=self._admin_create).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Publish", command=self._admin_publish).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self._admin_delete).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_courses_table).pack(
            side=tk.LEFT, padx=2
        )

        prereq_frame = ttk.LabelFrame(left, text="Prerequisites", padding=5)
        prereq_frame.grid(row=len(fields) + 1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        ttk.Label(prereq_frame, text="Prerequisite:").grid(row=0, column=0)
        self.prereq_var = tk.StringVar()
        ttk.Entry(prereq_frame, textvariable=self.prereq_var, width=12).grid(row=0, column=1)
        ttk.Label(prereq_frame, text="Dependent:").grid(row=0, column=2, padx=(10, 0))
        self.dependent_var = tk.StringVar()
        ttk.Entry(prereq_frame, textvariable=self.dependent_var, width=12).grid(row=0, column=3)
        ttk.Button(prereq_frame, text="Add", command=self._admin_add_prereq).grid(
            row=0, column=4, padx=5
        )
        ttk.Button(prereq_frame, text="Remove", command=self._admin_remove_prereq).grid(
            row=0, column=5
        )

        self.prereq_info = tk.StringVar(value="Select a course to view prerequisites")
        ttk.Label(left, textvariable=self.prereq_info, wraplength=350).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky=tk.W
        )

        right = ttk.LabelFrame(frame, text="Course Catalog", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        search_frame = ttk.Frame(right)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_courses_table())
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(
            side=tk.LEFT, padx=5
        )

        cols = ("code", "name", "difficulty", "duration", "status", "instructor")
        self.courses_tree = ttk.Treeview(right, columns=cols, show="headings", height=20)
        headings = {
            "code": "Code",
            "name": "Name",
            "difficulty": "Difficulty",
            "duration": "Hours",
            "status": "Status",
            "instructor": "Instructor",
        }
        for col, heading in headings.items():
            self.courses_tree.heading(col, text=heading)
            self.courses_tree.column(col, width=100 if col != "name" else 180)
        self.courses_tree.pack(fill=tk.BOTH, expand=True)
        self.courses_tree.bind("<<TreeviewSelect>>", self._on_course_select)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=scrollbar.set)

        self._refresh_courses_table()

    def _admin_create(self) -> None:
        try:
            duration = float(self.admin_vars["course_duration"].get() or "0")
        except ValueError:
            self._set_status("Invalid duration", is_error=True)
            return
        data = {
            "code": self.admin_vars["course_code"].get(),
            "name": self.admin_vars["course_name"].get(),
            "description": self.admin_vars["course_desc"].get(),
            "difficulty": self.admin_vars["course_diff"].get(),
            "duration_hours": duration,
            "instructor": self.admin_vars["course_instructor"].get(),
        }
        ok, msg = self.admin_ctrl.create_course(data)
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_courses_table()

    def _admin_publish(self) -> None:
        code = self._selected_course_code()
        if not code:
            self._set_status("Select a course first", is_error=True)
            return
        ok, msg = self.admin_ctrl.publish_course(code)
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_courses_table()

    def _admin_delete(self) -> None:
        code = self._selected_course_code()
        if not code:
            self._set_status("Select a course first", is_error=True)
            return
        ok, msg = self.admin_ctrl.delete_course(code)
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_courses_table()

    def _admin_add_prereq(self) -> None:
        ok, msg = self.admin_ctrl.add_prerequisite(
            self.prereq_var.get(), self.dependent_var.get()
        )
        self._set_status(msg, is_error=not ok)
        if ok:
            self._on_course_select(None)

    def _admin_remove_prereq(self) -> None:
        ok, msg = self.admin_ctrl.remove_prerequisite(
            self.prereq_var.get(), self.dependent_var.get()
        )
        self._set_status(msg, is_error=not ok)

    def _selected_course_code(self) -> Optional[str]:
        sel = self.courses_tree.selection()
        if not sel:
            return None
        return self.courses_tree.item(sel[0])["values"][0]

    def _on_course_select(self, _event) -> None:
        code = self._selected_course_code()
        if not code:
            return
        direct, transitive = self.admin_ctrl.get_prerequisites(code)
        self.prereq_info.set(
            f"{code}: Direct prereqs: {sorted(direct) or 'None'} | "
            f"Transitive: {sorted(transitive) or 'None'}"
        )

    def _refresh_courses_table(self) -> None:
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        query = self.search_var.get() if hasattr(self, "search_var") else ""
        courses = (
            self.admin_ctrl.list_courses()
            if not query
            else self.container.course_service.search_courses(query)
        )
        for c in courses:
            self.courses_tree.insert(
                "",
                tk.END,
                values=(
                    c.code,
                    c.name,
                    c.difficulty.value,
                    c.duration_hours,
                    c.status.value,
                    c.instructor,
                ),
            )

    # ---- Learner Tab ----
    def _build_learner_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Learner Portal")

        top = ttk.LabelFrame(frame, text="Learner Profile", padding=10)
        top.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top, text="Learner ID:").grid(row=0, column=0, sticky=tk.W)
        self.learner_id_var = tk.StringVar(value="L001")
        learner_cb = ttk.Combobox(top, textvariable=self.learner_id_var, width=15)
        learner_cb.grid(row=0, column=1, padx=5)
        learner_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_learner_data())
        self._learner_cb = learner_cb

        ttk.Label(top, text="Name:").grid(row=0, column=2, padx=(20, 0))
        self.learner_name_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.learner_name_var, width=20).grid(row=0, column=3)

        ttk.Label(top, text="Email:").grid(row=0, column=4, padx=(20, 0))
        self.learner_email_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.learner_email_var, width=25).grid(row=0, column=5)

        ttk.Button(top, text="Register", command=self._learner_register).grid(
            row=0, column=6, padx=10
        )
        ttk.Button(top, text="Load Progress", command=self._refresh_learner_data).grid(
            row=0, column=7
        )

        mid = ttk.Frame(frame)
        mid.pack(fill=tk.BOTH, expand=True)

        enroll_frame = ttk.LabelFrame(mid, text="Enrollment", padding=10)
        enroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(enroll_frame, text="Course Code:").grid(row=0, column=0)
        self.enroll_course_var = tk.StringVar()
        ttk.Entry(enroll_frame, textvariable=self.enroll_course_var, width=15).grid(
            row=0, column=1
        )
        ttk.Button(enroll_frame, text="Validate", command=self._learner_validate).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(enroll_frame, text="Enroll", command=self._learner_enroll).grid(
            row=0, column=3
        )

        ttk.Label(enroll_frame, text="Score:").grid(row=1, column=0, pady=5)
        self.complete_score_var = tk.StringVar()
        ttk.Entry(enroll_frame, textvariable=self.complete_score_var, width=10).grid(
            row=1, column=1
        )
        ttk.Button(enroll_frame, text="Mark Complete", command=self._learner_complete).grid(
            row=1, column=2, columnspan=2, pady=5
        )

        self.validation_label = tk.StringVar(value="Real-time validation feedback appears here")
        ttk.Label(
            enroll_frame, textvariable=self.validation_label, foreground=COLORS["accent"]
        ).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)

        self.suggested_var = tk.StringVar(value="Suggested courses: (load progress first)")
        ttk.Label(enroll_frame, textvariable=self.suggested_var, wraplength=400).grid(
            row=3, column=0, columnspan=4, sticky=tk.W
        )

        progress_frame = ttk.LabelFrame(mid, text="Progress & Enrollments", padding=10)
        progress_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.progress_var = tk.StringVar(value="Completion: --")
        ttk.Label(progress_frame, textvariable=self.progress_var, font=("Segoe UI", 11, "bold")).pack(
            anchor=tk.W
        )

        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)

        cols = ("course", "status", "score")
        self.enroll_tree = ttk.Treeview(progress_frame, columns=cols, show="headings", height=15)
        for col, heading in zip(cols, ["Course", "Status", "Score"]):
            self.enroll_tree.heading(col, text=heading)
            self.enroll_tree.column(col, width=120)
        self.enroll_tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_learners()
        self._refresh_learner_data()

    def _learner_register(self) -> None:
        ok, msg = self.learner_ctrl.register_learner(
            self.learner_id_var.get(),
            self.learner_name_var.get(),
            self.learner_email_var.get(),
        )
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_learners()

    def _learner_validate(self) -> None:
        ok, msg = self.learner_ctrl.validate_enrollment(
            self.learner_id_var.get(), self.enroll_course_var.get()
        )
        color = COLORS["success"] if ok else COLORS["error"]
        self.validation_label.set(msg)
        for widget in self.root.winfo_children():
            pass

    def _learner_enroll(self) -> None:
        ok, msg = self.learner_ctrl.enroll(
            self.learner_id_var.get(), self.enroll_course_var.get()
        )
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_learner_data()

    def _learner_complete(self) -> None:
        score_str = self.complete_score_var.get()
        score = float(score_str) if score_str else None
        ok, msg = self.learner_ctrl.complete_course(
            self.learner_id_var.get(),
            self.enroll_course_var.get(),
            score,
        )
        self._set_status(msg, is_error=not ok)
        if ok:
            self._refresh_learner_data()

    def _refresh_learners(self) -> None:
        learners = self.learner_ctrl.list_learners()
        self._learner_cb["values"] = [l.learner_id for l in learners]

    def _refresh_learner_data(self) -> None:
        learner_id = self.learner_id_var.get()
        progress = self.learner_ctrl.get_progress(learner_id)
        if progress:
            self.progress_var.set(
                f"Completed: {progress.completed_count}/{progress.total_enrollments} "
                f"({progress.completion_rate:.1f}%)"
            )
            self.progress_bar["value"] = progress.completion_rate
            suggested = self.learner_ctrl.suggest_courses(learner_id)
            self.suggested_var.set(
                f"Suggested courses: {', '.join(sorted(suggested)) or 'None available'}"
            )

        for item in self.enroll_tree.get_children():
            self.enroll_tree.delete(item)
        for e in self.learner_ctrl.get_enrollments(learner_id):
            self.enroll_tree.insert(
                "",
                tk.END,
                values=(e.course_code, e.status.value, e.score or "N/A"),
            )

    # ---- Learning Path Tab ----
    def _build_path_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Learning Paths")

        input_frame = ttk.LabelFrame(frame, text="Path Finder", padding=10)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Start:").grid(row=0, column=0)
        self.path_start_var = tk.StringVar(value="CS101")
        ttk.Entry(input_frame, textvariable=self.path_start_var, width=12).grid(row=0, column=1)

        ttk.Label(input_frame, text="Target:").grid(row=0, column=2, padx=(15, 0))
        self.path_target_var = tk.StringVar(value="CS301")
        ttk.Entry(input_frame, textvariable=self.path_target_var, width=12).grid(row=0, column=3)

        ttk.Label(input_frame, text="Strategy:").grid(row=0, column=4, padx=(15, 0))
        self.path_strategy_var = tk.StringVar(value="shortest")
        ttk.Combobox(
            input_frame,
            textvariable=self.path_strategy_var,
            values=self.path_ctrl.get_strategies(),
            width=18,
        ).grid(row=0, column=5)

        ttk.Button(input_frame, text="Find Path", command=self._find_path).grid(
            row=0, column=6, padx=10
        )
        ttk.Button(input_frame, text="Find All Paths", command=self._find_all_paths).grid(
            row=0, column=7
        )

        self.path_result = tk.Text(frame, height=20, font=("Consolas", 10), wrap=tk.WORD)
        self.path_result.pack(fill=tk.BOTH, expand=True, pady=10)

    def _find_path(self) -> None:
        path, stats = self.path_ctrl.find_path(
            self.path_start_var.get(),
            self.path_target_var.get(),
            self.path_strategy_var.get(),
        )
        self.path_result.delete("1.0", tk.END)
        if not path:
            self.path_result.insert(tk.END, "No path found.")
            return
        valid, msg = self.path_ctrl.validate_path(path)
        text = f"Path ({self.path_strategy_var.get()}): {' -> '.join(path)}\n"
        text += f"Valid: {msg}\n"
        if stats:
            text += f"Total hours: {stats.total_hours}\n"
            text += f"Course count: {stats.course_count}\n"
            text += f"Avg difficulty: {stats.average_difficulty:.2f}\n"
            text += f"Difficulty progression: {stats.difficulty_progression}\n"
        self.path_result.insert(tk.END, text)

    def _find_all_paths(self) -> None:
        paths = self.path_ctrl.find_multiple_paths(
            self.path_start_var.get(), self.path_target_var.get()
        )
        self.path_result.delete("1.0", tk.END)
        if not paths:
            self.path_result.insert(tk.END, "No paths found.")
            return
        for i, (path, stats) in enumerate(paths, 1):
            self.path_result.insert(
                tk.END,
                f"\n--- Path {i}: {' -> '.join(path)} ---\n"
                f"Hours: {stats.total_hours}, Courses: {stats.course_count}, "
                f"Avg Difficulty: {stats.average_difficulty:.2f}\n",
            )

    # ---- Analytics Tab ----
    def _build_analytics_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Analytics Dashboard")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Refresh Analytics", command=self._refresh_analytics).pack(
            side=tk.LEFT
        )

        self.metrics_text = tk.Text(frame, height=8, font=("Consolas", 10), wrap=tk.WORD)
        self.metrics_text.pack(fill=tk.X, pady=5)

        cols = ("code", "name", "enrolled", "completed", "rate", "avg_score")
        self.analytics_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for col, heading in zip(
            cols, ["Code", "Name", "Enrolled", "Completed", "Rate %", "Avg Score"]
        ):
            self.analytics_tree.heading(col, text=heading)
            self.analytics_tree.column(col, width=120)
        self.analytics_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.bottleneck_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.bottleneck_var, wraplength=900).pack(anchor=tk.W)

        self._refresh_analytics()

    def _refresh_analytics(self) -> None:
        report = self.analytics_ctrl.get_report()
        m = report.system_metrics
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(
            tk.END,
            f"System Metrics\n"
            f"{'='*40}\n"
            f"Total Courses: {m.total_courses} (Published: {m.published_courses})\n"
            f"Total Learners: {m.total_learners}\n"
            f"Total Enrollments: {m.total_enrollments}\n"
            f"Completed: {m.completed_enrollments} ({m.completion_rate:.1f}%)\n"
            f"Graph Depth: {m.graph_depth} | Edges: {m.graph_edges}\n"
            f"Avg Prerequisites: {m.average_prerequisites:.2f}\n",
        )

        for item in self.analytics_tree.get_children():
            self.analytics_tree.delete(item)
        for stat in report.course_stats:
            self.analytics_tree.insert(
                "",
                tk.END,
                values=(
                    stat.course_code,
                    stat.course_name,
                    stat.total_enrollments,
                    stat.completed_count,
                    f"{stat.completion_rate:.1f}",
                    f"{stat.average_score:.1f}" if stat.average_score else "N/A",
                ),
            )

        if report.bottlenecks:
            bn = ", ".join(
                f"{c} (prereqs={p}, rate={r:.0%})" for c, p, r in report.bottlenecks[:5]
            )
            self.bottleneck_var.set(f"Bottleneck courses: {bn}")
        else:
            self.bottleneck_var.set("No significant bottleneck courses detected.")

    def run(self) -> None:
        self.root.mainloop()
