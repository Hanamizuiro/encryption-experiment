from manim import *
from pathlib import Path
import csv


PROJECT_ROOT = Path(__file__).resolve().parent
OUT_DIR = PROJECT_ROOT / "out"


def _safe_float(value):
    try:
        return float(value)
    except Exception:
        return None


def _load_summary_rows(csv_path):
    rows = []
    dropped = 0
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sigma = _safe_float(row.get("sigma"))
            psnr = _safe_float(row.get("psnr_mean"))
            if sigma is None or psnr is None:
                dropped += 1
                continue
            rows.append(
                {
                    "matrix_type": row.get("matrix_type", ""),
                    "solver": row.get("solver", ""),
                    "sigma": sigma,
                    "psnr_mean": psnr,
                }
            )
    return rows, dropped


class EncryptionPipeline(Scene):
    def construct(self):
        title = Text("Matrix Encryption Pipeline", font_size=42).to_edge(UP)

        eq1 = MathTex(r"c = Kx", font_size=56)
        eq2 = MathTex(r"c' = c + \epsilon", font_size=56)
        eq3 = MathTex(r"K\hat{x} = c'", font_size=56)
        eq4 = MathTex(r"\hat{x} \approx x", font_size=56)

        eq_group = VGroup(eq1, eq2, eq3, eq4).arrange(DOWN, buff=0.55)
        eq_group.move_to(ORIGIN + DOWN * 0.2)

        labels = VGroup(
            MathTex(r"K\;\text{: key matrix}", font_size=34),
            MathTex(r"\epsilon\;\text{: noise}", font_size=34),
            MathTex(r"\hat{x}\;\text{: recovered signal}", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(DR)

        self.play(Write(title))
        self.wait(0.2)

        self.play(Write(eq1))
        self.play(Write(eq2))
        self.play(Write(eq3))
        self.play(Write(eq4))

        arrows = VGroup(
            Arrow(eq1.get_bottom() + DOWN * 0.05, eq2.get_top() + UP * 0.05, buff=0.0, stroke_width=3),
            Arrow(eq2.get_bottom() + DOWN * 0.05, eq3.get_top() + UP * 0.05, buff=0.0, stroke_width=3),
            Arrow(eq3.get_bottom() + DOWN * 0.05, eq4.get_top() + UP * 0.05, buff=0.0, stroke_width=3),
        )
        self.play(Create(arrows), FadeIn(labels, shift=UP * 0.2))
        self.wait(1.5)


class LinearAlgebraMatrixView(Scene):
    def construct(self):
        title = Text("Linear Algebra Behind Encryption", font_size=40).to_edge(UP)
        subtitle = Text("Vector x is transformed by matrix K into c = Kx", font_size=24)
        subtitle.next_to(title, DOWN, buff=0.2)

        eq = MathTex(
            r"x=\begin{bmatrix}x_1\\x_2\end{bmatrix},\quad "
            r"K=\begin{bmatrix}a&b\\c&d\end{bmatrix},\quad "
            r"c=Kx",
            font_size=40,
        )
        eq.next_to(subtitle, DOWN, buff=0.35)

        # 2D plane view of the linear transform x -> Kx
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.35, "stroke_width": 1},
        ).scale(0.78)
        plane.to_edge(DOWN, buff=0.35)

        vec_x = Vector([1.4, 0.8], color=BLUE)
        vec_c = Vector([2.2, 0.2], color=ORANGE)
        x_label = MathTex(r"x", color=BLUE, font_size=32).next_to(vec_x.get_end(), RIGHT, buff=0.12)
        c_label = MathTex(r"c=Kx", color=ORANGE, font_size=30).next_to(vec_c.get_end(), RIGHT, buff=0.12)

        k_note = Text("K mixes/scales/rotates vector coordinates", font_size=22)
        k_note.to_corner(DL).shift(UP * 0.2)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2))
        self.play(Write(eq))
        self.play(Create(plane))
        self.play(GrowArrow(vec_x), FadeIn(x_label))
        self.wait(0.4)
        self.play(Transform(vec_x.copy(), vec_c), FadeIn(c_label))
        self.play(FadeIn(k_note, shift=UP * 0.15))
        self.wait(1.8)


class SolverConvergence(Scene):
    def construct(self):
        title = Text("Solver Convergence (Illustrative)", font_size=40).to_edge(UP)

        axes = Axes(
            x_range=[0, 25, 5],
            y_range=[-6, 0, 1],
            x_length=10,
            y_length=4.5,
            axis_config={"include_numbers": True, "font_size": 24},
            tips=False,
        ).to_edge(DOWN, buff=0.9)

        x_label = axes.get_x_axis_label(MathTex(r"\text{iteration }k", font_size=34), edge=DOWN, direction=DOWN)
        y_label = axes.get_y_axis_label(MathTex(r"\log_{10}(\|r_k\|/\|b\|)", font_size=30), edge=LEFT, direction=LEFT)

        gs = axes.plot(lambda x: -0.14 * x - 0.2, x_range=[0, 25], color=GREEN)
        lu = axes.plot(lambda x: -2.8, x_range=[0, 25], color=ORANGE)
        ge = axes.plot(lambda x: -2.7, x_range=[0, 25], color=BLUE)

        legend = VGroup(
            VGroup(Line(LEFT * 0.4, RIGHT * 0.4, color=GREEN), Text("Gauss-Seidel", font_size=24)).arrange(RIGHT, buff=0.2),
            VGroup(Line(LEFT * 0.4, RIGHT * 0.4, color=ORANGE), Text("LU", font_size=24)).arrange(RIGHT, buff=0.2),
            VGroup(Line(LEFT * 0.4, RIGHT * 0.4, color=BLUE), Text("Gaussian", font_size=24)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR).shift(DOWN * 0.8)

        note = Text("Direct methods: one-shot solve; GS: iterative residual drop", font_size=24).to_corner(DL)

        self.play(Write(title))
        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Create(gs), run_time=1.2)
        self.play(Create(lu), Create(ge), run_time=1.0)
        self.play(FadeIn(legend), FadeIn(note, shift=UP * 0.2))
        self.wait(2)


class ResultsFromCSV(Scene):
    # Change this to "sparse" if needed.
    matrix_type = "dense"

    def construct(self):
        csv_path = OUT_DIR / "results_summary.csv"

        if not csv_path.exists():
            msg = VGroup(
                Text("results_summary.csv not found", font_size=40),
                Text(f"Expected: {csv_path}", font_size=24),
                Text("Run code.ipynb first", font_size=28),
            ).arrange(DOWN, buff=0.3)
            self.play(Write(msg))
            self.wait(2)
            return

        rows, dropped = _load_summary_rows(csv_path)
        rows = [r for r in rows if r["matrix_type"] == self.matrix_type]

        if len(rows) == 0:
            msg = VGroup(
                Text(f"No {self.matrix_type} rows in results_summary.csv", font_size=36),
                Text("Check notebook outputs and rerun experiments", font_size=26),
            ).arrange(DOWN, buff=0.35)
            self.play(Write(msg))
            self.wait(2)
            return

        solver_order = ["np_solve", "gaussian", "lu", "gauss_seidel"]
        color_map = {
            "np_solve": RED,
            "gaussian": BLUE,
            "lu": ORANGE,
            "gauss_seidel": GREEN,
        }

        sigmas = sorted({r["sigma"] for r in rows})
        psnr_vals = [r["psnr_mean"] for r in rows]
        y_min = min(psnr_vals)
        y_max = max(psnr_vals)
        y_pad = max(0.5, (y_max - y_min) * 0.15)

        x_min, x_max = min(sigmas), max(sigmas)
        if abs(x_max - x_min) < 1e-12:
            x_min -= 0.05
            x_max += 0.05
        x_step = max(0.01, (x_max - x_min) / 4)

        y_low, y_high = y_min - y_pad, y_max + y_pad
        if abs(y_high - y_low) < 1e-9:
            y_low -= 0.5
            y_high += 0.5
        y_step = max(0.5, (y_high - y_low) / 5)

        axes = Axes(
            x_range=[x_min, x_max, x_step],
            y_range=[y_low, y_high, y_step],
            x_length=10,
            y_length=5,
            axis_config={"include_numbers": True, "font_size": 22},
            tips=False,
        ).to_edge(DOWN, buff=0.8)

        title = Text(f"Real Results: PSNR vs Noise ({self.matrix_type.title()})", font_size=36).to_edge(UP)
        subtitle_text = f"Loaded from out/results_summary.csv"
        if dropped > 0:
            subtitle_text += f" | dropped rows: {dropped}"
        subtitle = Text(subtitle_text, font_size=22).next_to(title, DOWN, buff=0.2)

        x_label = axes.get_x_axis_label(MathTex(r"\sigma", font_size=34), edge=DOWN, direction=DOWN)
        y_label = axes.get_y_axis_label(MathTex(r"\mathrm{PSNR\ (dB)}", font_size=30), edge=LEFT, direction=LEFT)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2))
        self.play(Create(axes), Write(x_label), Write(y_label))

        legend_items = []
        for solver in solver_order:
            pts = sorted([(r["sigma"], r["psnr_mean"]) for r in rows if r["solver"] == solver], key=lambda t: t[0])
            if len(pts) == 0:
                continue

            graph = axes.plot_line_graph(
                x_values=[p[0] for p in pts],
                y_values=[p[1] for p in pts],
                line_color=color_map[solver],
                vertex_dot_style={"fill_color": color_map[solver]},
                vertex_dot_radius=0.04,
                add_vertex_dots=True,
            )
            self.play(Create(graph), run_time=0.9)

            # endpoint label to improve paper readability
            end_x, end_y = pts[-1]
            end_label = MathTex(f"{end_y:.2f}", font_size=24, color=color_map[solver])
            end_label.next_to(axes.c2p(end_x, end_y), RIGHT, buff=0.08)
            self.play(FadeIn(end_label, shift=RIGHT * 0.05), run_time=0.3)

            legend_items.append(
                VGroup(Line(LEFT * 0.35, RIGHT * 0.35, color=color_map[solver]), Text(solver.replace("_", " "), font_size=22)).arrange(RIGHT, buff=0.2)
            )

        if len(legend_items) > 0:
            legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            legend.to_corner(UR).shift(DOWN * 0.8)
            self.play(FadeIn(legend, shift=LEFT * 0.1))

        self.wait(2)


class ErrorMapsShowcase(Scene):
    def construct(self):
        err_files = sorted((OUT_DIR / "figures").glob("wall_err_*.png"))

        if len(err_files) == 0:
            msg = VGroup(
                Text("No wall_err_*.png found", font_size=40),
                Text("Run code.ipynb to generate error maps first", font_size=28),
            ).arrange(DOWN, buff=0.35)
            self.play(Write(msg))
            self.wait(2)
            return

        title = Text("Error Map Showcase", font_size=42).to_edge(UP)
        note = Text("Higher intensity = larger reconstruction error", font_size=24).next_to(title, DOWN, buff=0.2)
        self.play(Write(title), FadeIn(note, shift=UP * 0.2))

        # Show up to 6 maps for clarity
        show_files = err_files[:6]
        n = len(show_files)
        cols = 3
        rows = (n + cols - 1) // cols

        imgs = []
        for i, fp in enumerate(show_files):
            im = ImageMobject(str(fp)).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            im.scale_to_fit_width(3.9)
            cap = Text(fp.stem.replace("_", " "), font_size=18)
            group = VGroup(im, cap).arrange(DOWN, buff=0.12)
            imgs.append(group)

        grid = VGroup(*imgs).arrange_in_grid(rows=rows, cols=cols, buff=0.35)
        grid.move_to(DOWN * 0.35)

        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in imgs], lag_ratio=0.12, run_time=2.2))
        self.wait(2)


class DenseVsSparseComparison(Scene):
    def construct(self):
        csv_path = OUT_DIR / "results_summary.csv"

        if not csv_path.exists():
            msg = VGroup(
                Text("results_summary.csv not found", font_size=38),
                Text("Run code.ipynb first", font_size=26),
            ).arrange(DOWN, buff=0.3)
            self.play(Write(msg))
            self.wait(2)
            return

        rows, dropped = _load_summary_rows(csv_path)
        dense_rows = [r for r in rows if r["matrix_type"] == "dense"]
        sparse_rows = [r for r in rows if r["matrix_type"] == "sparse"]

        if len(dense_rows) == 0 or len(sparse_rows) == 0:
            msg = VGroup(
                Text("Need both dense and sparse rows", font_size=36),
                Text("Check results_summary.csv", font_size=24),
            ).arrange(DOWN, buff=0.3)
            self.play(Write(msg))
            self.wait(2)
            return

        solver_order = ["np_solve", "gaussian", "lu", "gauss_seidel"]
        color_map = {
            "np_solve": RED,
            "gaussian": BLUE,
            "lu": ORANGE,
            "gauss_seidel": GREEN,
        }

        all_rows = dense_rows + sparse_rows
        sigmas = sorted({r["sigma"] for r in all_rows})
        psnr_vals = [r["psnr_mean"] for r in all_rows]

        x_min, x_max = min(sigmas), max(sigmas)
        if abs(x_max - x_min) < 1e-12:
            x_min -= 0.05
            x_max += 0.05
        x_step = max(0.01, (x_max - x_min) / 4)

        y_min, y_max = min(psnr_vals), max(psnr_vals)
        y_pad = max(0.5, (y_max - y_min) * 0.15)
        y_low, y_high = y_min - y_pad, y_max + y_pad
        if abs(y_high - y_low) < 1e-9:
            y_low -= 0.5
            y_high += 0.5
        y_step = max(0.5, (y_high - y_low) / 5)

        title = Text("Dense vs Sparse: PSNR vs Noise", font_size=40).to_edge(UP)
        subtitle_text = "Same scale on both sides"
        if dropped > 0:
            subtitle_text += f" | dropped rows: {dropped}"
        subtitle = Text(subtitle_text, font_size=22).next_to(title, DOWN, buff=0.2)

        dense_axes = Axes(
            x_range=[x_min, x_max, x_step],
            y_range=[y_low, y_high, y_step],
            x_length=5.5,
            y_length=4.2,
            axis_config={"include_numbers": True, "font_size": 18},
            tips=False,
        )
        sparse_axes = Axes(
            x_range=[x_min, x_max, x_step],
            y_range=[y_low, y_high, y_step],
            x_length=5.5,
            y_length=4.2,
            axis_config={"include_numbers": True, "font_size": 18},
            tips=False,
        )

        panels = VGroup(dense_axes, sparse_axes).arrange(RIGHT, buff=0.9).to_edge(DOWN, buff=0.7)

        dense_label = Text("Dense", font_size=28).next_to(dense_axes, UP, buff=0.15)
        sparse_label = Text("Sparse", font_size=28).next_to(sparse_axes, UP, buff=0.15)

        x_label_dense = dense_axes.get_x_axis_label(MathTex(r"\sigma", font_size=28), edge=DOWN, direction=DOWN)
        y_label_dense = dense_axes.get_y_axis_label(MathTex(r"\mathrm{PSNR}", font_size=26), edge=LEFT, direction=LEFT)
        x_label_sparse = sparse_axes.get_x_axis_label(MathTex(r"\sigma", font_size=28), edge=DOWN, direction=DOWN)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2))
        self.play(
            Create(dense_axes), Create(sparse_axes),
            Write(dense_label), Write(sparse_label),
            Write(x_label_dense), Write(y_label_dense), Write(x_label_sparse),
        )

        legend_items = []

        for solver in solver_order:
            dense_pts = sorted(
                [(r["sigma"], r["psnr_mean"]) for r in dense_rows if r["solver"] == solver],
                key=lambda t: t[0],
            )
            sparse_pts = sorted(
                [(r["sigma"], r["psnr_mean"]) for r in sparse_rows if r["solver"] == solver],
                key=lambda t: t[0],
            )

            anims = []
            if len(dense_pts) > 0:
                dense_graph = dense_axes.plot_line_graph(
                    x_values=[p[0] for p in dense_pts],
                    y_values=[p[1] for p in dense_pts],
                    line_color=color_map[solver],
                    vertex_dot_style={"fill_color": color_map[solver]},
                    vertex_dot_radius=0.035,
                    add_vertex_dots=True,
                )
                anims.append(Create(dense_graph))

            if len(sparse_pts) > 0:
                sparse_graph = sparse_axes.plot_line_graph(
                    x_values=[p[0] for p in sparse_pts],
                    y_values=[p[1] for p in sparse_pts],
                    line_color=color_map[solver],
                    vertex_dot_style={"fill_color": color_map[solver]},
                    vertex_dot_radius=0.035,
                    add_vertex_dots=True,
                )
                anims.append(Create(sparse_graph))

            if len(anims) > 0:
                self.play(*anims, run_time=0.8)
                legend_items.append(
                    VGroup(
                        Line(LEFT * 0.28, RIGHT * 0.28, color=color_map[solver]),
                        Text(solver.replace("_", " "), font_size=20),
                    ).arrange(RIGHT, buff=0.15)
                )

        if len(legend_items) > 0:
            legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            legend.to_corner(UR).shift(DOWN * 1.0)
            self.play(FadeIn(legend, shift=LEFT * 0.1))

        self.wait(2)


# Render examples:
# manim -pqh manim_math_visualization.py EncryptionPipeline
# manim -pqh manim_math_visualization.py LinearAlgebraMatrixView
# manim -pqh manim_math_visualization.py SolverConvergence
# manim -pqh manim_math_visualization.py ResultsFromCSV
# manim -pqh manim_math_visualization.py ErrorMapsShowcase
# manim -pqh manim_math_visualization.py DenseVsSparseComparison
