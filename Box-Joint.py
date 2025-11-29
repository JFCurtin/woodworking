import math
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageDraw, ImageFont


def generate_template():
    try:
        board_width_mm = float(entry_board_width.get())
        finger_width_mm = float(entry_finger_width.get())
        board_height_mm = float(entry_board_height.get())
        dpi = int(entry_dpi.get())
        start_with_finger = var_start_with_finger.get() == 1

        if board_width_mm <= 0 or finger_width_mm <= 0 or board_height_mm <= 0 or dpi <= 0:
            messagebox.showerror("Invalid input", "All numeric values must be greater than zero.")
            return

        if finger_width_mm > board_width_mm:
            messagebox.showerror("Invalid input", "Finger width cannot be greater than board width.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Save Box Joint Template",
            initialfile="BoxJointTemplate.png"
        )
        if not file_path:
            return

        # --- Drawing math ---
        mm_to_px = dpi / 25.4
        margin_mm = 5
        margin_px = int(round(margin_mm * mm_to_px))

        board_width_px = int(round(board_width_mm * mm_to_px))
        board_height_px = int(round(board_height_mm * mm_to_px))
        finger_width_px = int(round(finger_width_mm * mm_to_px))

        # Image size (extra height for title/ruler text)
        img_width = board_width_px + 2 * margin_px
        img_height = board_height_px + 2 * margin_px + 80

        # --- Create image ---
        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)

        # Try to load a nicer font, fall back to default
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- Title / info text ---
        title = f"Box Joint Template - Board: {board_width_mm} mm, Finger: {finger_width_mm} mm"
        info = f"Print at {dpi} DPI, 'Actual size / 100%' with no scaling."

        draw.text((margin_px, margin_px), title, fill="black", font=font_title)
        draw.text((margin_px, margin_px + 24), info, fill="black", font=font_small)

        origin_y = margin_px + 50  # space for title

        # --- Board outline ---
        left_x = margin_px
        top_y = origin_y
        right_x = left_x + board_width_px
        bottom_y = top_y + board_height_px

        draw.rectangle([left_x, top_y, right_x, bottom_y], outline="black", width=1)

        # --- Fingers ---
        x = left_x
        end_x = right_x
        draw_finger = start_with_finger

        while x < end_x:
            seg_width = min(finger_width_px, end_x - x)
            if draw_finger and seg_width > 0:
                # Filled finger down full board height
                draw.rectangle([x, top_y, x + seg_width, bottom_y], fill="black", outline=None)
            x += seg_width
            draw_finger = not draw_finger

        # --- Simple scale ruler below the board ---
        ruler_top_y = bottom_y + 10
        ruler_length_mm = min(board_width_mm, 200)  # cap length for readability
        ruler_length_px = int(round(ruler_length_mm * mm_to_px))

        # main ruler line
        draw.line(
            [left_x, ruler_top_y, left_x + ruler_length_px, ruler_top_y],
            fill="black",
            width=1
        )

        # Tick marks every 10 mm
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

        # Save image
        img.save(file_path, "PNG")

        messagebox.showinfo("Done", f"Template saved to:\n{file_path}")

        # Optionally open the file on Windows
        try:
            if os.name == "nt":
                os.startfile(file_path)
        except Exception:
            pass

    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")


# ---------------------------
#   Build the GUI
# ---------------------------

root = tk.Tk()
root.title("Box Joint Template Generator")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Board width
ttk.Label(mainframe, text="Board width (mm):").grid(row=0, column=0, sticky="w", pady=2)
entry_board_width = ttk.Entry(mainframe, width=10)
entry_board_width.grid(row=0, column=1, sticky="w", pady=2)
entry_board_width.insert(0, "100")

# Finger width
ttk.Label(mainframe, text="Finger width (mm):").grid(row=1, column=0, sticky="w", pady=2)
entry_finger_width = ttk.Entry(mainframe, width=10)
entry_finger_width.grid(row=1, column=1, sticky="w", pady=2)
entry_finger_width.insert(0, "10")

# Template height
ttk.Label(mainframe, text="Template height (mm):").grid(row=2, column=0, sticky="w", pady=2)
entry_board_height = ttk.Entry(mainframe, width=10)
entry_board_height.grid(row=2, column=1, sticky="w", pady=2)
entry_board_height.insert(0, "40")

# DPI
ttk.Label(mainframe, text="Output DPI:").grid(row=3, column=0, sticky="w", pady=2)
entry_dpi = ttk.Entry(mainframe, width=10)
entry_dpi.grid(row=3, column=1, sticky="w", pady=2)
entry_dpi.insert(0, "300")

# Start with finger checkbox
var_start_with_finger = tk.IntVar(value=1)
chk_start_with_finger = ttk.Checkbutton(
    mainframe,
    text="Start with finger (else gap)",
    variable=var_start_with_finger
)
chk_start_with_finger.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)

# Buttons
btn_generate = ttk.Button(mainframe, text="Generate Template", command=generate_template)
btn_generate.grid(row=5, column=0, sticky="w", pady=8)

btn_close = ttk.Button(mainframe, text="Close", command=root.destroy)
btn_close.grid(row=5, column=1, sticky="e", pady=8)

root.mainloop()
