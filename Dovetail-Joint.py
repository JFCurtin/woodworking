import math
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageDraw, ImageFont


def parse_ratio(text: str) -> float:
    """
    Parse dovetail ratio from input like:
    - "6"  -> 6.0  (meaning 1:6)
    - "1:6" -> 6.0
    """
    text = text.strip()
    if ":" in text:
        parts = text.split(":")
        try:
            left = float(parts[0])
            right = float(parts[1])
            if left == 0:
                raise ValueError("Ratio left side cannot be zero.")
            return right / left
        except Exception:
            raise ValueError("Invalid ratio format. Use e.g. 6 or 1:6")
    else:
        try:
            return float(text)
        except Exception:
            raise ValueError("Invalid ratio value. Use e.g. 6 or 1:6")


def generate_template():
    try:
        board_width_mm = float(entry_board_width.get())
        board_height_mm = float(entry_board_height.get())
        num_tails = int(entry_tails.get())
        dpi = int(entry_dpi.get())
        ratio_val = parse_ratio(entry_ratio.get())  # e.g. 6.0 for 1:6

        if board_width_mm <= 0 or board_height_mm <= 0 or num_tails <= 0 or dpi <= 0:
            messagebox.showerror("Invalid input", "All numeric values must be greater than zero.")
            return

        if num_tails < 1:
            messagebox.showerror("Invalid input", "Number of tails must be at least 1.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Save Dovetail Template",
            initialfile="DovetailTemplate.png"
        )
        if not file_path:
            return

        # --- Drawing math ---
        mm_to_px = dpi / 25.4
        margin_mm = 5
        margin_px = int(round(margin_mm * mm_to_px))

        board_width_px = int(round(board_width_mm * mm_to_px))
        board_height_px = int(round(board_height_mm * mm_to_px))

        # Image size (extra height for title/ruler text)
        img_width = board_width_px + 2 * margin_px
        img_height = board_height_px + 2 * margin_px + 100

        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)

        # Fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- Title + info ---
        title = f"Dovetail Template - Board: {board_width_mm} mm, Tails: {num_tails}, Ratio: 1:{ratio_val:g}"
        info = f"Print at {dpi} DPI, 'Actual size / 100%' with no scaling."

        draw.text((margin_px, margin_px), title, fill="black", font=font_title)
        draw.text((margin_px, margin_px + 24), info, fill="black", font=font_small)

        origin_y = margin_px + 50  # top of board end
        left_x = margin_px
        top_y = origin_y
        right_x = left_x + board_width_px
        bottom_y = top_y + board_height_px

        # Draw board outline
        draw.rectangle([left_x, top_y, right_x, bottom_y], outline="black", width=1)

        # --- Layout for tails and pins ---
        # We treat each tail as "1 unit" and each pin as "pin_fraction units".
        pin_fraction = 0.5  # pin width relative to tail width (adjust as desired)
        tail_units = 1.0
        pin_units = pin_fraction

        total_units = num_tails * tail_units + (num_tails + 1) * pin_units
        unit_px = board_width_px / total_units

        tail_top_width_px = tail_units * unit_px
        pin_width_px = pin_units * unit_px

        # Dovetail slope: for ratio 1:R, horizontal offset = height / R
        offset_px = board_height_px / ratio_val

        # Starting X for first tail top (after first pin)
        tail_start_x = left_x + pin_width_px

        for i in range(num_tails):
            tail_left_top_x = tail_start_x + i * (tail_top_width_px + pin_width_px)
            tail_right_top_x = tail_left_top_x + tail_top_width_px

            # Bottom (baseline) positions, pulled inward by offset on each side
            tail_left_bottom_x = tail_left_top_x + offset_px
            tail_right_bottom_x = tail_right_top_x - offset_px

            # Prevent inverted tails if offset is too large
            if tail_right_bottom_x <= tail_left_bottom_x:
                # If that happens, clamp and just make a triangle
                tail_left_bottom_x = (tail_left_bottom_x + tail_right_bottom_x) / 2.0
                tail_right_bottom_x = tail_left_bottom_x

            polygon = [
                (tail_left_top_x, top_y),
                (tail_right_top_x, top_y),
                (tail_right_bottom_x, bottom_y),
                (tail_left_bottom_x, bottom_y),
            ]

            draw.polygon(polygon, fill="black", outline=None)

        # --- Simple mm ruler under board ---
        ruler_top_y = bottom_y + 10
        ruler_length_mm = min(board_width_mm, 200)
        ruler_length_px = int(round(ruler_length_mm * mm_to_px))

        draw.line(
            [left_x, ruler_top_y, left_x + ruler_length_px, ruler_top_y],
            fill="black",
            width=1
        )

        tick_step_mm = 10
        mm_val = 0
        while mm_val <= ruler_length_mm + 0.01:
            px = left_x + int(round(mm_val * mm_to_px))
            draw.line(
                [px, ruler_top_y, px, ruler_top_y + 6],
                fill="black",
                width=1
            )
            label = f"{int(mm_val)} mm"
            draw.text((px - 10, ruler_top_y + 8), label, fill="black", font=font_small)
            mm_val += tick_step_mm

        img.save(file_path, "PNG")

        messagebox.showinfo("Done", f"Template saved to:\n{file_path}")

        try:
            if os.name == "nt":
                os.startfile(file_path)
        except Exception:
            pass

    except ValueError as ve:
        messagebox.showerror("Invalid input", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")


# ---------------------------
#   Build the GUI
# ---------------------------

root = tk.Tk()
root.title("Dovetail Template Generator")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Board width
ttk.Label(mainframe, text="Board width (mm):").grid(row=0, column=0, sticky="w", pady=2)
entry_board_width = ttk.Entry(mainframe, width=10)
entry_board_width.grid(row=0, column=1, sticky="w", pady=2)
entry_board_width.insert(0, "100")

# Template height (dovetail depth)
ttk.Label(mainframe, text="Dovetail depth (mm):").grid(row=1, column=0, sticky="w", pady=2)
entry_board_height = ttk.Entry(mainframe, width=10)
entry_board_height.grid(row=1, column=1, sticky="w", pady=2)
entry_board_height.insert(0, "40")

# Number of tails
ttk.Label(mainframe, text="Number of tails:").grid(row=2, column=0, sticky="w", pady=2)
entry_tails = ttk.Entry(mainframe, width=10)
entry_tails.grid(row=2, column=1, sticky="w", pady=2)
entry_tails.insert(0, "3")

# Dovetail ratio
ttk.Label(mainframe, text="Dovetail ratio (1:x):").grid(row=3, column=0, sticky="w", pady=2)
entry_ratio = ttk.Entry(mainframe, width=10)
entry_ratio.grid(row=3, column=1, sticky="w", pady=2)
entry_ratio.insert(0, "6")  # 1:6 default

# DPI
ttk.Label(mainframe, text="Output DPI:").grid(row=4, column=0, sticky="w", pady=2)
entry_dpi = ttk.Entry(mainframe, width=10)
entry_dpi.grid(row=4, column=1, sticky="w", pady=2)
entry_dpi.insert(0, "300")

# Buttons
btn_generate = ttk.Button(mainframe, text="Generate Template", command=generate_template)
btn_generate.grid(row=5, column=0, sticky="w", pady=8)

btn_close = ttk.Button(mainframe, text="Close", command=root.destroy)
btn_close.grid(row=5, column=1, sticky="e", pady=8)

root.mainloop()
