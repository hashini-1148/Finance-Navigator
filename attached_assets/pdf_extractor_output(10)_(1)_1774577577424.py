"""
PDF Data Extraction Tool — Enterprise Edition
============================================================
Professional-grade PDF extraction with a clean, dark enterprise GUI.
All extraction modes fully functional: Invoice, Form, Table, Custom, Auto.

Requirements:
    pip install PyMuPDF pdfplumber Pillow openpyxl pytesseract
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
import re
import io
import csv
import time
import math
import random
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.request
import urllib.error
import base64

# ── Gemini free models (Google AI Studio) ────────────────────
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


# ─────────────────────────────────────────────────────────────
#  THEME — Deep Navy / Purple Gradient
# ─────────────────────────────────────────────────────────────
T = {
    # Backgrounds — deep navy blue tones
    "bg0":      "#010101",   # deepest background (near black)
    "bg1":      "#031a2e",   # panel background (deep navy)
    "bg2":      "#042540",   # card / sidebar (navy blue)
    "bg3":      "#063356",   # input / hover (slightly lighter navy)

    # Borders
    "border":   "#0d4a7a",
    "border2":  "#1a6baa",

    # Accent — purple gradient spectrum (FA93FA → C967E8 → 983AD6)
    "accent":   "#c967e8",   # mid-gradient purple
    "accent2":  "#fa93fa",   # light pinkish-purple
    "accent_dk":"#7b2abf",   # dark purple

    # Gradient colors
    "grad_start": "#fa93fa", # from
    "grad_mid":   "#c967e8", # via
    "grad_end":   "#983ad6", # to

    # Status
    "green":    "#4ade80",
    "yellow":   "#fbbf24",
    "red":      "#f87171",
    "orange":   "#fb923c",
    "purple":   "#c084fc",

    # Text
    "text1":    "#ffffff",   # primary white
    "text2":    "#a8b4c0",   # secondary (muted gray)
    "text3":    "#6b7a8a",   # dim/placeholder

    # Special
    "white":    "#ffffff",
    "tag_bg":   "#1a2a5e",
    "sel_bg":   "#7b2abf",
}

# Gradient accent string for canvas gradient simulation
GRAD_ACCENT = "#c967e8"

FONT_MONO  = ("Consolas", 10)
FONT_MONO_S= ("Consolas", 9)
FONT_UI    = ("Segoe UI", 10)
FONT_UI_B  = ("Segoe UI", 10, "bold")
FONT_UI_S  = ("Segoe UI", 9)
FONT_UI_L  = ("Segoe UI", 12, "bold")
FONT_UI_XL = ("Segoe UI", 16, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")


# ─────────────────────────────────────────────────────────────
#  SPARK / PARTICLE ANIMATION ENGINE
# ─────────────────────────────────────────────────────────────

class SparkOverlay(tk.Canvas):
    """Spark canvas scoped to the title bar."""
    COLORS = ["#fa93fa", "#e070e0", "#c967e8", "#983ad6", "#ffffff",
              "#e0b0ff", "#f0a0f0", "#b040d0", "#d080f8"]
    MAX_SPARKS = 80

    def __init__(self, root, **kw):
        super().__init__(root, bg=T["bg1"], highlightthickness=0, bd=0, **kw)
        self._sparks = []
        self._trail_counter = 0
        self._running = False
        self.bind("<Motion>", self._on_motion)

    def _on_motion(self, e):
        self._trail_counter += 1
        if self._trail_counter % 2 == 0:
            self._emit(e.x, e.y, count=random.randint(2, 4))
            if not self._running:
                self._running = True
                self._tick()

    def _emit(self, x, y, count=3):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.8, 4.0)
            size  = random.uniform(1.5, 5.0)
            life  = random.randint(20, 45)
            color = random.choice(self.COLORS)
            glow  = random.random() < 0.35
            self._sparks.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - random.uniform(0.3, 2.5),
                "size": size, "life": life, "max_life": life,
                "color": color, "glow": glow,
            })
        if len(self._sparks) > self.MAX_SPARKS:
            self._sparks = self._sparks[-self.MAX_SPARKS:]

    def _tick(self):
        self.delete("spark")
        alive = []
        for sp in self._sparks:
            sp["x"]  += sp["vx"]
            sp["y"]  += sp["vy"]
            sp["vy"] += 0.10
            sp["vx"] *= 0.97
            sp["life"] -= 1
            if sp["life"] <= 0:
                continue
            alive.append(sp)
            ratio = sp["life"] / sp["max_life"]
            r = max(1, int(sp["size"] * ratio))
            faded = self._fade(sp["color"], ratio)
            if sp["glow"]:
                gr = r + 5
                self.create_oval(
                    sp["x"]-gr, sp["y"]-gr, sp["x"]+gr, sp["y"]+gr,
                    fill="", outline=self._fade(sp["color"], ratio * 0.25),
                    width=1, tags="spark"
                )
            self.create_oval(
                sp["x"]-r, sp["y"]-r, sp["x"]+r, sp["y"]+r,
                fill=faded, outline="", tags="spark"
            )
        self._sparks = alive
        if self._sparks:
            self.after(33, self._tick)
        else:
            self._running = False

    @staticmethod
    def _fade(hex_color, ratio):
        h = hex_color.lstrip("#")
        r = int(int(h[0:2], 16) * ratio)
        g = int(int(h[2:4], 16) * ratio)
        b = int(int(h[4:6], 16) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"


class GlobalCursorSpark:
    """Full-window cursor spark — attaches to the SparkOverlay titlebar canvas
    AND tracks motion app-wide, drawing sparks scoped to that canvas.
    No full-window overlay needed — avoids all stacking/transparency issues."""
    COLORS = ["#fa93fa", "#e070e0", "#c967e8", "#983ad6", "#ffffff",
              "#e0b0ff", "#f0a0f0", "#b040d0", "#d080f8", "#ff80ff"]
    MAX_SPARKS = 120

    def __init__(self, root):
        self._root    = root
        self._sparks  = []
        self._running = False
        self._counter = 0
        self._canvas  = None   # set later via set_canvas()
        # Capture motion from every widget in the app
        root.bind_all("<Motion>", self._on_motion, add=True)

    def set_canvas(self, canvas):
        """Attach to an existing canvas (e.g. the SparkOverlay on the titlebar)."""
        self._canvas = canvas

    def _on_motion(self, e):
        if self._canvas is None:
            return
        self._counter += 1
        if self._counter % 2 == 0:
            try:
                # Map root-window coords → canvas coords
                cx = e.x_root - self._canvas.winfo_rootx()
                cy = e.y_root - self._canvas.winfo_rooty()
            except Exception:
                return
            self._emit(cx, cy)
            if not self._running:
                self._running = True
                self._tick()

    def _emit(self, x, y):
        count = random.randint(2, 5)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 3.5)
            size  = random.uniform(1.5, 5.5)
            life  = random.randint(18, 40)
            color = random.choice(self.COLORS)
            glow  = random.random() < 0.4
            self._sparks.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - random.uniform(0.2, 2.0),
                "size": size, "life": life, "max_life": life,
                "color": color, "glow": glow,
            })
        if len(self._sparks) > self.MAX_SPARKS:
            self._sparks = self._sparks[-self.MAX_SPARKS:]

    def _tick(self):
        c = self._canvas
        if c is None:
            self._running = False
            return
        c.delete("gspark")
        alive = []
        for sp in self._sparks:
            sp["x"]  += sp["vx"]
            sp["y"]  += sp["vy"]
            sp["vy"] += 0.12
            sp["vx"] *= 0.96
            sp["life"] -= 1
            if sp["life"] <= 0:
                continue
            alive.append(sp)
            ratio = sp["life"] / sp["max_life"]
            r = max(1, int(sp["size"] * ratio))
            faded = self._fade(sp["color"], ratio)
            if sp["glow"]:
                gr = r + 4
                c.create_oval(
                    sp["x"]-gr, sp["y"]-gr, sp["x"]+gr, sp["y"]+gr,
                    fill="", outline=self._fade(sp["color"], ratio * 0.3),
                    width=1, tags="gspark"
                )
            c.create_oval(
                sp["x"]-r, sp["y"]-r, sp["x"]+r, sp["y"]+r,
                fill=faded, outline="", tags="gspark"
            )
        self._sparks = alive
        if self._sparks:
            c.after(33, self._tick)
        else:
            self._running = False

    @staticmethod
    def _fade(hex_color, ratio):
        h = hex_color.lstrip("#")
        r = int(int(h[0:2], 16) * ratio)
        g = int(int(h[2:4], 16) * ratio)
        b = int(int(h[4:6], 16) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

def blend_color(hex_color, alpha, bg_hex="#042540"):
    """
    Simulate RGBA by blending hex_color at given alpha (0.0-1.0) over bg_hex.
    Tkinter does not support 8-char hex colors — this produces a valid 6-char result.
    alpha can also be a 2-char hex string like '22' or '10'.
    """
    if isinstance(alpha, str):
        alpha = int(alpha, 16) / 255.0
    def parse(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    fr, fg, fb = parse(hex_color)
    br, bg_r, bb = parse(bg_hex)
    r = int(fr * alpha + br * (1 - alpha))
    g = int(fg * alpha + bg_r * (1 - alpha))
    b = int(fb * alpha + bb * (1 - alpha))
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────
#  EXTRACTION ENGINE
# ─────────────────────────────────────────────────────────────

def pdf_get_text(path):
    """Extract raw text from all pages using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(path)
        pages = []
        for i, page in enumerate(doc):
            pages.append(f"[PAGE {i+1}]\n{page.get_text('text')}")
        doc.close()
        return "\n\n".join(pages)
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install PyMuPDF")
    except Exception as e:
        raise RuntimeError(f"Cannot open PDF: {e}")


def pdf_page_count(path):
    """Return number of pages."""
    try:
        import fitz
        doc = fitz.open(path)
        n = len(doc)
        doc.close()
        return n
    except Exception:
        return 0


def pdf_render_page(path, page_num=0, zoom=1.5):
    """Render a PDF page to a PIL Image."""
    import fitz
    from PIL import Image
    doc = fitz.open(path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def pdf_get_text_blocks(path, page_num=0):
    """Return text block bounding boxes for a page."""
    try:
        import fitz
        doc = fitz.open(path)
        page = doc[page_num]
        blocks = page.get_text("blocks")
        doc.close()
        return [(b[0], b[1], b[2], b[3], b[4]) for b in blocks if b[4].strip()]
    except Exception:
        return []


# ── Invoice Parser ────────────────────────────────────────────

INV_PATTERNS = {
    "Invoice Number": [
        r"(?:invoice|inv)[\s#.:]*([A-Z0-9][\w\-/]{2,20})",
        r"(?:invoice|inv)\s+no\.?\s*[:\-]?\s*([A-Z0-9][\w\-]{2,20})",
    ],
    "Invoice Date": [
        r"(?:invoice\s+)?date\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?:invoice\s+)?date\s*[:\-]\s*(\w+\s+\d{1,2},?\s*\d{4})",
        r"(?:date\s+of\s+invoice)\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    ],
    "Due Date": [
        r"due\s+(?:date|by|on)\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"payment\s+due\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"pay\s+by\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    ],
    "Vendor / From": [
        r"(?:from|vendor|billed?\s+by|seller|company)\s*[:\-]\s*([A-Za-z0-9][\w\s&.,'\-]{2,50}?)(?:\n|$)",
    ],
    "Bill To": [
        r"bill(?:ed)?\s+to\s*[:\-]?\s*([A-Za-z][\w\s.,'\-]{2,60})(?:\n|$)",
        r"customer\s*[:\-]\s*([A-Za-z][\w\s.,'\-]{2,60})(?:\n|$)",
    ],
    "PO Number": [
        r"p\.?o\.?\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9\-]{3,20})",
        r"purchase\s+order\s*[:\-]?\s*([A-Z0-9\-]{3,20})",
    ],
    "Subtotal": [
        r"sub[\s\-]?total\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
    ],
    "Tax / VAT": [
        r"(?:tax|vat|gst)\s*(?:\([\d.]+%\))?\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
    ],
    "Tax Rate": [
        r"(?:tax|vat|gst)\s+rate\s*[:\-]?\s*([\d.]+\s*%)",
        r"(?:tax|vat|gst)\s*\(([\d.]+%)\)",
    ],
    "Discount": [
        r"discount\s*(?:\([\d.]+%\))?\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
    ],
    "Shipping": [
        r"(?:shipping|freight|delivery)\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
    ],
    "Total Amount": [
        r"(?:grand\s+total|total\s+amount\s+due|total\s+due|amount\s+due|total)\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
        r"(?:balance\s+due)\s*[:\-]?\s*\$?\s*([\d,]+\.?\d{0,2})",
    ],
    "Currency": [
        r"\b(USD|EUR|GBP|INR|AUD|CAD|JPY|CHF|SGD|AED)\b",
        r"(\$|€|£|₹|¥)",
    ],
    "Payment Terms": [
        r"(?:payment\s+terms?|terms?)\s*[:\-]\s*(.{3,40})(?:\n|$)",
        r"(net\s+\d+|due\s+on\s+receipt|COD|net30|net60)",
    ],
    "Bank / Account": [
        r"(?:bank|account|iban|swift|routing)\s*[:\-]\s*([\w\s\-]{5,30})(?:\n|$)",
    ],
}

CURRENCY_MAP = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR", "¥": "JPY"}

def extract_line_items(text):
    """Heuristically extract line items from invoice text."""
    items = []
    # Pattern: description (spaces) qty (space) unit_price (space) total
    pat = re.compile(
        r"^(.{4,60}?)\s{2,}(\d+(?:\.\d+)?)\s+\$?([\d,]+\.?\d{0,2})\s+\$?([\d,]+\.?\d{0,2})\s*$",
        re.MULTILINE
    )
    skip = {"subtotal","total","tax","vat","gst","discount","shipping","freight"}
    for m in pat.finditer(text):
        desc = m.group(1).strip()
        if any(s in desc.lower() for s in skip):
            continue
        try:
            items.append({
                "Description": desc,
                "Qty": float(m.group(2)),
                "Unit Price": float(m.group(3).replace(",","")),
                "Total": float(m.group(4).replace(",","")),
            })
        except ValueError:
            pass
    # Fallback: two-column (description + price)
    if not items:
        pat2 = re.compile(
            r"^(.{4,60}?)\s{2,}\$?([\d,]+\.?\d{0,2})\s*$",
            re.MULTILINE
        )
        for m in pat2.finditer(text):
            desc = m.group(1).strip()
            if any(s in desc.lower() for s in skip) or len(desc) < 4:
                continue
            try:
                items.append({
                    "Description": desc,
                    "Qty": 1,
                    "Unit Price": float(m.group(2).replace(",","")),
                    "Total": float(m.group(2).replace(",","")),
                })
            except ValueError:
                pass
    return items[:30]


def extract_invoice(text):
    """Extract all invoice fields from text."""
    result = {"_type": "Invoice", "_fields": {}, "_line_items": [], "_confidence": 0}
    found = 0
    for field, patterns in INV_PATTERNS.items():
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            if m:
                val = m.group(1).strip()
                if field == "Currency" and val in CURRENCY_MAP:
                    val = CURRENCY_MAP[val]
                result["_fields"][field] = val
                found += 1
                break
    result["_line_items"] = extract_line_items(text)
    total = len(INV_PATTERNS)
    result["_confidence"] = round(min(found / total, 1.0), 2)
    return result


# ── Form Parser ───────────────────────────────────────────────

def extract_form(text):
    """Extract key:value pairs from form-style PDFs."""
    result = {"_type": "Form", "_fields": {}, "_confidence": 0}
    patterns = [
        # Label: Value
        re.compile(r"^([A-Za-z][A-Za-z0-9 _/().-]{1,50}?)\s*:\s*(.{1,150}?)$", re.MULTILINE),
        # Label ............. Value
        re.compile(r"^([A-Za-z][A-Za-z0-9 _/().-]{1,50}?)\s*[_.]{4,}\s*(.{1,150}?)$", re.MULTILINE),
        # Label — Value  (em dash)
        re.compile(r"^([A-Za-z][A-Za-z0-9 _/().-]{1,50}?)\s*[\u2014\u2013]\s*(.{1,150}?)$", re.MULTILINE),
    ]
    for pat in patterns:
        for m in pat.finditer(text):
            label = m.group(1).strip()
            value = m.group(2).strip()
            # Filter noise
            if len(label) < 2 or len(value) == 0:
                continue
            if label.lower() in ("page", "of", "the", "and", "or", "for", "to", "a"):
                continue
            if value not in result["_fields"]:
                result["_fields"][label] = value

    n = len(result["_fields"])
    result["_confidence"] = round(min(n / 8, 1.0), 2)
    return result


# ── Table Parser ──────────────────────────────────────────────

def extract_tables(path):
    """Extract all tables from PDF using pdfplumber."""
    result = {"_type": "Tables", "_tables": [], "_confidence": 0}
    try:
        import pdfplumber
    except ImportError:
        result["_error"] = "pdfplumber not installed. Run: pip install pdfplumber"
        return result
    try:
        with pdfplumber.open(path) as pdf:
            for pg_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for t_idx, table in enumerate(tables):
                    if not table:
                        continue
                    cleaned = []
                    for row in table:
                        cleaned.append([str(c).strip() if c else "" for c in row])
                    # Remove empty rows
                    cleaned = [r for r in cleaned if any(c for c in r)]
                    if cleaned:
                        result["_tables"].append({
                            "page": pg_num,
                            "index": t_idx + 1,
                            "rows": len(cleaned),
                            "cols": max(len(r) for r in cleaned),
                            "data": cleaned,
                        })
        n = len(result["_tables"])
        result["_confidence"] = round(min(0.4 + n * 0.2, 1.0), 2) if n > 0 else 0.1
    except Exception as e:
        result["_error"] = str(e)
    return result


# ── Custom Pattern Parser ─────────────────────────────────────

def extract_custom(text, patterns_str):
    """Extract fields using user-defined regex patterns (one per line: Name: pattern)."""
    result = {"_type": "Custom", "_fields": {}, "_confidence": 0}
    patterns = {}
    for line in patterns_str.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            name, _, pat = line.partition(":")
            patterns[name.strip()] = pat.strip()

    if not patterns:
        result["_error"] = "No valid patterns defined."
        return result

    found = 0
    for name, pat in patterns.items():
        try:
            m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
            if m:
                val = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else m.group(0).strip()
                result["_fields"][name] = val
                found += 1
            else:
                result["_fields"][name] = "(not found)"
        except re.error as e:
            result["_fields"][name] = f"[regex error: {e}]"

    result["_confidence"] = round(found / len(patterns), 2)
    return result


# ── Auto Detect ───────────────────────────────────────────────

def detect_type(text):
    """Heuristic document type detection."""
    tl = text.lower()
    scores = {
        "invoice": sum(1 for w in ["invoice","bill to","total due","line item",
                                    "subtotal","payment terms","amount due",
                                    "purchase order","quantity","unit price"] if w in tl),
        "form":    sum(1 for w in ["please complete","applicant","signature",
                                    "date of birth","full name","checkbox",
                                    "fill in","please print"] if w in tl),
        "table":   sum(1 for w in ["table","column","row","header"] if w in tl),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "invoice"


def run_extraction(path, mode, custom_patterns="", use_ocr=False, ocr_lang="eng", tess_cmd=""):
    """Main extraction orchestrator. Returns result dict."""
    result = {
        "path": path,
        "filename": os.path.basename(path),
        "pages": pdf_page_count(path),
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_text": "",
        "data": {},
        "error": None,
    }

    # Step 1: Extract text
    try:
        raw = pdf_get_text(path)
    except Exception as e:
        result["error"] = str(e)
        return result

    # Step 2: OCR fallback
    if use_ocr or len(raw.strip()) < 100:
        try:
            import pytesseract
            from PIL import Image
            import fitz
            if tess_cmd:
                pytesseract.pytesseract.tesseract_cmd = tess_cmd
            doc = fitz.open(path)
            ocr_parts = []
            for i, page in enumerate(doc):
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_parts.append(f"[PAGE {i+1}]\n{pytesseract.image_to_string(img, lang=ocr_lang)}")
            doc.close()
            ocr_text = "\n\n".join(ocr_parts)
            if len(ocr_text.strip()) > len(raw.strip()):
                raw = ocr_text
        except Exception as e:
            pass  # OCR failed, use whatever text we have

    result["raw_text"] = raw

    # Step 3: Auto-detect
    effective = mode
    if mode == "auto":
        effective = detect_type(raw)
        result["detected"] = effective

    # Step 4: Parse
    try:
        if effective == "invoice":
            result["data"] = extract_invoice(raw)
        elif effective == "form":
            result["data"] = extract_form(raw)
        elif effective == "table":
            result["data"] = extract_tables(path)
        elif effective == "custom":
            result["data"] = extract_custom(raw, custom_patterns)
        else:
            result["data"] = extract_invoice(raw)
    except Exception as e:
        result["error"] = str(e)

    return result


# ─────────────────────────────────────────────────────────────
#  EXPORT ENGINE
# ─────────────────────────────────────────────────────────────

def flatten_result(data):
    """Flatten extraction result into simple key-value pairs."""
    flat = {}
    if "_fields" in data:
        flat.update(data["_fields"])
    if "_type" in data:
        flat["Document Type"] = data["_type"]
    if "_confidence" in data:
        flat["Confidence"] = f"{int(data['_confidence']*100)}%"
    return flat


def do_export_json(result, path):
    """Export to JSON."""
    out = {
        "meta": {
            "filename": result.get("filename"),
            "pages": result.get("pages"),
            "mode": result.get("mode"),
            "detected": result.get("detected", result.get("mode")),
            "timestamp": result.get("timestamp"),
        },
        "fields": result["data"].get("_fields", {}),
        "line_items": result["data"].get("_line_items", []),
        "tables": result["data"].get("_tables", []),
        "confidence": result["data"].get("_confidence", 0),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)


def do_export_csv(result, path):
    """Export fields + line items to CSV."""
    data = result["data"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # Fields section
        w.writerow(["=== EXTRACTED FIELDS ==="])
        w.writerow(["Field", "Value"])
        for k, v in data.get("_fields", {}).items():
            w.writerow([k, v])
        # Line items
        items = data.get("_line_items", [])
        if items:
            w.writerow([])
            w.writerow(["=== LINE ITEMS ==="])
            w.writerow(list(items[0].keys()))
            for item in items:
                w.writerow(list(item.values()))
        # Tables
        for i, tbl in enumerate(data.get("_tables", []), 1):
            w.writerow([])
            w.writerow([f"=== TABLE {i} (Page {tbl['page']}) ==="])
            for row in tbl["data"]:
                w.writerow(row)


def do_export_excel(result, path):
    """Export to styled Excel workbook."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        raise ImportError("openpyxl not installed. Run: pip install openpyxl")

    wb = openpyxl.Workbook()
    data = result["data"]

    # ── Fields Sheet ──
    ws = wb.active
    ws.title = "Extracted Fields"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 50

    hdr_fill = PatternFill("solid", fgColor="1c2333")
    hdr_font = Font(name="Segoe UI", bold=True, color="2f81f7", size=10)
    val_font  = Font(name="Segoe UI", color="e6edf3", size=10)
    alt_fill  = PatternFill("solid", fgColor="161b22")
    alt2_fill = PatternFill("solid", fgColor="0e1117")
    thin = Border(bottom=Side(style="thin", color="30363d"))

    # Header
    ws.append(["Field", "Value"])
    for cell in ws[1]:
        cell.font = hdr_font
        cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 22

    # Metadata rows
    ws.append(["Document Type", data.get("_type", "Unknown")])
    ws.append(["Confidence", f"{int(data.get('_confidence', 0)*100)}%"])
    ws.append(["Filename", result.get("filename", "")])
    ws.append(["Pages", str(result.get("pages", ""))])
    ws.append(["Extracted At", result.get("timestamp", "")])

    # Fields
    for k, v in data.get("_fields", {}).items():
        ws.append([k, str(v)])

    for i, row in enumerate(ws.iter_rows(min_row=2), 2):
        fill = alt_fill if i % 2 == 0 else alt2_fill
        for cell in row:
            cell.font = val_font
            cell.fill = fill
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[i].height = 18

    # ── Line Items Sheet ──
    items = data.get("_line_items", [])
    if items:
        ws2 = wb.create_sheet("Line Items")
        ws2.sheet_view.showGridLines = False
        headers = list(items[0].keys())
        ws2.append(headers)
        for cell in ws2[1]:
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="left")
        for ci, h in enumerate(headers, 1):
            ws2.column_dimensions[openpyxl.utils.get_column_letter(ci)].width = 20
        for ri, item in enumerate(items, 2):
            ws2.append([item.get(h, "") for h in headers])
            fill = alt_fill if ri % 2 == 0 else alt2_fill
            for cell in ws2[ri]:
                cell.font = val_font
                cell.fill = fill

    # ── Tables Sheet ──
    for ti, tbl in enumerate(data.get("_tables", []), 1):
        ws3 = wb.create_sheet(f"Table {ti} (P{tbl['page']})")
        ws3.sheet_view.showGridLines = False
        for ri, row in enumerate(tbl["data"], 1):
            ws3.append(row)
            is_hdr = ri == 1
            fill = hdr_fill if is_hdr else (alt_fill if ri % 2 == 0 else alt2_fill)
            font = hdr_font if is_hdr else val_font
            for cell in ws3[ri]:
                cell.font = font
                cell.fill = fill
                cell.alignment = Alignment(horizontal="left")
        for ci in range(1, tbl["cols"] + 2):
            ws3.column_dimensions[openpyxl.utils.get_column_letter(ci)].width = 18

    wb.save(path)


def do_export_xml(result, path):
    """Export to structured XML."""
    root = ET.Element("PDFExtraction")
    root.set("timestamp", result.get("timestamp", ""))
    root.set("file", result.get("filename", ""))

    meta = ET.SubElement(root, "Meta")
    ET.SubElement(meta, "Pages").text = str(result.get("pages", ""))
    ET.SubElement(meta, "Mode").text = result.get("mode", "")
    ET.SubElement(meta, "Confidence").text = str(result["data"].get("_confidence", 0))

    fields_el = ET.SubElement(root, "Fields")
    for k, v in result["data"].get("_fields", {}).items():
        tag = re.sub(r"[^A-Za-z0-9_]", "_", k)
        ET.SubElement(fields_el, tag).text = str(v)

    items_el = ET.SubElement(root, "LineItems")
    for item in result["data"].get("_line_items", []):
        item_el = ET.SubElement(items_el, "Item")
        for k, v in item.items():
            tag = re.sub(r"[^A-Za-z0-9_]", "_", k)
            ET.SubElement(item_el, tag).text = str(v)

    tables_el = ET.SubElement(root, "Tables")
    for tbl in result["data"].get("_tables", []):
        tbl_el = ET.SubElement(tables_el, "Table")
        tbl_el.set("page", str(tbl["page"]))
        for row in tbl["data"]:
            row_el = ET.SubElement(tbl_el, "Row")
            for cell in row:
                ET.SubElement(row_el, "Cell").text = str(cell)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=True)


# ─────────────────────────────────────────────────────────────
#  GEMINI AI ENGINE  (Google AI Studio — no SDK, pure urllib)
# ─────────────────────────────────────────────────────────────
#
#  Provider / model catalogue — mirrors ResumeIQ pattern
#  Free tier:  2.5 Flash (10 RPM), 2.5 Flash-Lite (15 RPM), 2.5 Pro (5 RPM)
#  Preview:    3.1 Flash, 3.1 Pro  (may require billing)
#  Get free key: https://aistudio.google.com/app/apikey
# ─────────────────────────────────────────────────────────────

AI_PROVIDERS = [
    {
        "id": "gemini-free",
        "name": "Gemini Free Tier",
        "color": "#4285f4",
        "icon": "🆓",
        "models": [
            {"id": "gemini-2.5-flash",      "name": "Gemini 2.5 Flash",      "badge": "🆓 Free · 10 RPM", "tier": "free"},
            {"id": "gemini-2.5-flash-lite",  "name": "Gemini 2.5 Flash-Lite", "badge": "🆓 Free · 15 RPM", "tier": "free"},
            {"id": "gemini-2.5-pro",         "name": "Gemini 2.5 Pro",        "badge": "🆓 Free · 5 RPM",  "tier": "free"},
        ],
    },
    {
        "id": "gemini-3",
        "name": "Gemini 3 (Preview)",
        "color": "#0f9d58",
        "icon": "✦",
        "models": [
            {"id": "gemini-3.1-flash",       "name": "Gemini 3.1 Flash",      "badge": "🆕 Latest",    "tier": "premium"},
            {"id": "gemini-3.1-flash-lite",  "name": "Gemini 3.1 Flash-Lite", "badge": "⚡ Fast",       "tier": "premium"},
            {"id": "gemini-3-flash-preview",  "name": "Gemini 3 Flash",        "badge": "🔬 Preview",   "tier": "premium"},
            {"id": "gemini-3.1-pro-preview",  "name": "Gemini 3.1 Pro",        "badge": "💎 Power",     "tier": "premium"},
        ],
    },
]

ALL_AI_MODELS = {m["id"]: {**m, "provider": p["name"], "provider_color": p["color"], "provider_icon": p["icon"]}
                 for p in AI_PROVIDERS for m in p["models"]}

DEFAULT_AI_MODEL = "gemini-2.5-flash"

TIER_COLORS = {"free": ("#166534", "#dcfce7"), "premium": ("#5b21b6", "#ede9fe")}

# AI task catalogue — same pattern as ResumeIQ AIPanel.tasks
AI_TASKS = [
    {"id": "arrange",   "label": "Arrange & Structure", "icon": "⊞",  "desc": "Organise into clean sections",     "color": "#6366f1"},
    {"id": "summarise", "label": "Summarise",            "icon": "≡",  "desc": "Executive summary",               "color": "#8b5cf6"},
    {"id": "tables",    "label": "Extract Tables",       "icon": "⊟",  "desc": "All tables as neat Markdown",      "color": "#ec4899"},
    {"id": "invoice",   "label": "Invoice Analysis",     "icon": "◎",  "desc": "Fields, line items, totals",       "color": "#f59e0b"},
    {"id": "keywords",  "label": "Key Insights",         "icon": "⌖",  "desc": "Important facts & figures",        "color": "#10b981"},
    {"id": "qa",        "label": "Ask a Question",       "icon": "⊕",  "desc": "Custom Q&A about the document",    "color": "#0ea5e9"},
]


def gemini_call(api_key, model, prompt, pdf_path=None):
    """
    Call Gemini generateContent REST endpoint.
    Optionally attaches PDF as inline base64 (vision-capable models).
    Returns full response text, or raises RuntimeError with friendly message.
    Get your free key: https://aistudio.google.com/app/apikey
    """
    parts = []

    # Attach PDF inline — Gemini 2.5+ supports native PDF vision
    if pdf_path and os.path.isfile(pdf_path):
        try:
            with open(pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})
        except Exception as e:
            raise RuntimeError(f"Cannot read PDF for upload: {e}")

    parts.append({"text": prompt})

    payload = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
    }).encode("utf-8")

    url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            body = json.loads(e.read().decode("utf-8", errors="replace"))
            msg  = body.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        # Mirror ResumeIQ friendly error messages
        if code == 400: msg = "Bad request — the model name may be invalid. Try Gemini 2.5 Flash."
        if code == 403: msg = "Invalid API key — check your Google AI Studio key in Settings."
        if code == 429: msg = "Rate limit hit — free tier: 10 req/min. Wait a moment or switch to Flash-Lite (15 RPM)."
        if code == 404: msg = "Model not found — this preview model may require billing. Switch to Gemini 2.5 Flash (free)."
        if code == 500: msg = "Gemini server error — try again in a moment."
        raise RuntimeError(f"Gemini API error ({code}): {msg}")
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Network error: {e.reason}\n\n"
            "Troubleshooting:\n"
            "• Check your internet connection\n"
            "• Make sure generativelanguage.googleapis.com is reachable\n"
            "• Try Gemini 2.5 Flash-Lite in Settings"
        )

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:300]}")


def gemini_test_key(api_key):
    """Quick key test — returns (ok: bool, message: str)."""
    try:
        url = f"{GEMINI_API_BASE}/gemini-2.5-flash:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Say OK"}]}],
            "generationConfig": {"maxOutputTokens": 5},
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read().decode("utf-8"))
        reply = d["candidates"][0]["content"]["parts"][0]["text"]
        return True, f"✓ API key valid! Gemini replied: \"{reply[:40]}\""
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, "Invalid API key — check your Google AI Studio key."
        return False, f"Error {e.code} — {e.reason}"
    except Exception as e:
        return False, f"Network error: {e}"


def build_gemini_prompt(task_id, extraction_result, custom_prompt=""):
    """Build task-specific prompt from extraction data — mirrors ResumeIQ prompts dict."""
    data      = extraction_result.get("data",     {}) if extraction_result else {}
    raw_text  = extraction_result.get("raw_text", "") if extraction_result else ""
    filename  = extraction_result.get("filename", "document") if extraction_result else "document"
    fields    = data.get("_fields",     {})
    tables    = data.get("_tables",     [])
    items     = data.get("_line_items", [])

    # Build context block from extracted data
    ctx_parts = []
    if fields:
        ctx_parts.append("=== EXTRACTED FIELDS ===\n" + "\n".join(f"{k}: {v}" for k, v in fields.items()))
    if items:
        ctx_parts.append("=== LINE ITEMS ===\n" + json.dumps(items, indent=2))
    if tables:
        for i, tbl in enumerate(tables, 1):
            rows = "\n".join("\t".join(str(c) for c in r) for r in tbl["data"])
            ctx_parts.append(f"=== TABLE {i} (Page {tbl['page']}) ===\n{rows}")
    if raw_text:
        ctx_parts.append(f"=== RAW TEXT ===\n{raw_text[:6000]}")
    ctx = "\n\n".join(ctx_parts) if ctx_parts else "(No extracted data — upload and extract a PDF first.)"

    doc_ref = f"Document: {filename}\n\n"

    prompts = {
        "arrange": (
            "You are a document intelligence assistant.\n"
            "Re-organise the content of this document into a clean, well-structured format.\n"
            "Use Markdown: # headers, ## sub-headers, bullet lists, and | tables | where appropriate.\n"
            "Preserve all data — do not omit anything.\n\n"
            + doc_ref + ctx
        ),
        "summarise": (
            "You are a professional document analyst.\n"
            "Write a concise executive summary of this document in 3–5 paragraphs.\n"
            "Include: purpose, key data points, totals/figures, important dates, and any action items.\n"
            "Format clearly with Markdown headers.\n\n"
            + doc_ref + ctx
        ),
        "tables": (
            "You are a data extraction specialist.\n"
            "Find every table in this document and reproduce it as a clean Markdown table.\n"
            "Label each table with a heading (## Table N — description).\n"
            "Include all rows and columns. Do not truncate or omit data.\n\n"
            + doc_ref + ctx
        ),
        "invoice": (
            "You are an invoice processing expert.\n"
            "Extract and neatly present ALL invoice information:\n"
            "  • Header fields: invoice number, date, due date, vendor, bill-to\n"
            "  • Line items table: description, qty, unit price, total\n"
            "  • Totals: subtotal, tax/VAT, discount, shipping, grand total\n"
            "  • Payment: terms, bank details, reference\n"
            "Format as structured Markdown with tables.\n\n"
            + doc_ref + ctx
        ),
        "keywords": (
            "You are a document analysis expert.\n"
            "Identify the most important facts, figures, entities, and insights in this document.\n"
            "Provide three sections:\n"
            "1. 🔑 Key Facts & Figures — the most critical numbers and dates\n"
            "2. 📌 Important Entities — people, companies, products, locations mentioned\n"
            "3. 💡 Actionable Insights — what someone should know or do based on this document\n\n"
            + doc_ref + ctx
        ),
        "qa": (
            f"You are a helpful document assistant.\n"
            f"Answer the following question based strictly on the document content.\n"
            f"If the answer is not in the document, say so clearly.\n\n"
            f"Question: {custom_prompt or 'What are the key points of this document?'}\n\n"
            + doc_ref + ctx
        ),
        "custom": (custom_prompt or "Analyse this document and provide key insights.\n\n") + doc_ref + ctx,
    }
    return prompts.get(task_id, prompts["arrange"])


# ─────────────────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────────────────

def styled_btn(parent, text, cmd, style="primary", width=None, pady=6, padx=14):
    """Create a styled flat button."""
    styles = {
        "primary": (T["accent"],   T["white"],  T["accent2"]),
        "success": (T["green"],    T["white"],  "#2ea043"),
        "danger":  (T["red"],      T["white"],  "#da3633"),
        "ghost":   (T["bg3"],      T["text2"],  T["border2"]),
        "outline": (T["bg1"],      T["accent"], T["bg3"]),
    }
    bg, fg, hover = styles.get(style, styles["primary"])
    kw = dict(text=text, command=cmd, font=FONT_UI_S, fg=fg, bg=bg,
              activeforeground=fg, activebackground=hover,
              relief="flat", bd=0, cursor="hand2", pady=pady, padx=padx)
    if width:
        kw["width"] = width
    btn = tk.Button(parent, **kw)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def label(parent, text, style="normal", **kw):
    """Create a themed label."""
    styles = {
        "normal":  (FONT_UI,    T["text2"]),
        "primary": (FONT_UI,    T["text1"]),
        "bold":    (FONT_UI_B,  T["text1"]),
        "title":   (FONT_TITLE, T["text1"]),
        "large":   (FONT_UI_L,  T["text1"]),
        "accent":  (FONT_UI_B,  T["accent"]),
        "small":   (FONT_UI_S,  T["text3"]),
        "green":   (FONT_UI_S,  T["green"]),
        "red":     (FONT_UI_S,  T["red"]),
        "mono":    (FONT_MONO,  T["text2"]),
    }
    font, fg = styles.get(style, styles["normal"])
    return tk.Label(parent, text=text, font=font, fg=fg,
                    bg=kw.pop("bg", T["bg1"]), **kw)


def divider(parent, bg=None, pady=(8, 8)):
    """Horizontal divider."""
    f = tk.Frame(parent, bg=bg or T["border"], height=1)
    f.pack(fill="x", pady=pady)
    return f


def card(parent, **kw):
    """A card-style frame."""
    f = tk.Frame(parent, bg=T["bg2"],
                 highlightthickness=1,
                 highlightbackground=T["border"])
    return f


def scrollable_frame(parent, bg=None):
    """Return (outer_frame, inner_frame) with vertical scroll."""
    bg = bg or T["bg1"]
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                       bg=bg, troughcolor=T["bg0"])
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=bg)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win_id, width=canvas.winfo_width())

    inner.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_configure)
    inner.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return outer, inner


def animate_int(widget, attr, start, end, steps=20, delay=16):
    """Animate an integer counter on a label."""
    if steps <= 0:
        widget.configure(**{attr: str(end)})
        return
    val = int(start + (end - start) * (1 - (1 - 1/steps) ** (21 - steps)))
    widget.configure(**{attr: str(val)})
    widget.after(delay, animate_int, widget, attr, val, end, steps-1, delay)


# ─────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────

class PDFExtractorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("PDF Data Extraction Tool — Enterprise Edition")
        self.configure(bg=T["bg0"])
        self.geometry("1380x840")
        self.minsize(1100, 700)

        # State
        self._pdf_path = None
        self._result = None
        self._page_num = 0
        self._total_pages = 0
        self._zoom = 1.4
        self._photo = None
        self._gemini_pdf_path = None
        self._settings = {
            "ocr_lang": "eng",
            "tesseract_cmd": "",
        }

        # Configure ttk styles
        self._style_ttk()

        # Global cursor spark — must exist before _build_titlebar assigns the canvas
        self._cursor_spark = GlobalCursorSpark(self)

        # Build UI
        self._build_titlebar()
        self._build_main()

        # Keyboard bindings
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._quick_save())
        self.bind("<F5>",        lambda e: self._run_extraction())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _style_ttk(self):
        s = ttk.Style(self)
        s.theme_use("default")
        # Notebook
        s.configure("App.TNotebook",
                    background=T["bg1"], borderwidth=0, tabmargins=0)
        s.configure("App.TNotebook.Tab",
                    background=T["bg2"], foreground=T["text2"],
                    padding=[18, 8], font=FONT_UI_S, borderwidth=0)
        s.map("App.TNotebook.Tab",
              background=[("selected", T["bg1"]), ("active", T["bg3"])],
              foreground=[("selected", T["accent"]), ("active", T["text1"])])
        # Treeview
        s.configure("App.Treeview",
                    background=T["bg0"], foreground=T["text1"],
                    fieldbackground=T["bg0"], font=FONT_MONO_S,
                    rowheight=22, borderwidth=0)
        s.configure("App.Treeview.Heading",
                    background=T["bg2"], foreground=T["accent"],
                    font=FONT_UI_S, relief="flat", borderwidth=0)
        s.map("App.Treeview",
              background=[("selected", T["sel_bg"])],
              foreground=[("selected", T["white"])])
        # Scrollbar
        s.configure("Thin.Vertical.TScrollbar",
                    background=T["bg3"], troughcolor=T["bg1"],
                    borderwidth=0, arrowsize=12)
        s.configure("Thin.Horizontal.TScrollbar",
                    background=T["bg3"], troughcolor=T["bg1"],
                    borderwidth=0, arrowsize=12)
        # Progressbar
        s.configure("App.Horizontal.TProgressbar",
                    background=T["accent"], troughcolor=T["bg3"],
                    borderwidth=0, thickness=3)
        # Separator
        s.configure("App.TSeparator", background=T["border"])
        # Combobox
        s.configure("App.TCombobox",
                    background=T["bg3"], foreground=T["text1"],
                    fieldbackground=T["bg3"], selectbackground=T["sel_bg"],
                    font=FONT_UI_S)

    # ── Title Bar ─────────────────────────────────────────────

    def _build_titlebar(self):
        tb = tk.Frame(self, bg=T["bg1"], height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Gradient accent line at very top
        accent_line = tk.Canvas(tb, height=3, bg=T["bg1"], highlightthickness=0)
        accent_line.pack(fill="x", side="top")
        self._titlebar_accent = accent_line
        self._gradient_job = None
        self.after(300, self._do_draw_title_gradient)
        self.bind("<Configure>", self._draw_title_gradient, add=True)

        # Logo / title
        left = tk.Frame(tb, bg=T["bg1"])
        left.pack(side="left", padx=16, fill="y")
        self._logo_lbl = tk.Label(left, text="✦", font=("Segoe UI", 20, "bold"),
                                  fg=T["accent"], bg=T["bg1"])
        self._logo_lbl.pack(side="left", padx=(0, 10))
        self._animate_logo()

        tk.Label(left, text="PDF Extraction Suite", font=FONT_UI_L,
                 fg=T["text1"], bg=T["bg1"]).pack(side="left")
        tk.Label(left, text="  ·  Enterprise Edition", font=FONT_UI_S,
                 fg=T["accent"], bg=T["bg1"]).pack(side="left", padx=(4, 0))

        # Right controls
        right = tk.Frame(tb, bg=T["bg1"])
        right.pack(side="right", padx=12, fill="y")

        styled_btn(right, "⚙  Settings", self._open_settings,
                   style="ghost", pady=4, padx=12).pack(side="right", padx=2)
        styled_btn(right, "?  Help",    self._show_help,
                   style="ghost", pady=4, padx=12).pack(side="right", padx=2)

        # Keyboard shortcut hints
        hints = tk.Frame(tb, bg=T["bg1"])
        hints.pack(side="right", padx=20, fill="y")
        for txt in ["Ctrl+O  Open", "F5  Extract", "Ctrl+S  Save"]:
            tk.Label(hints, text=txt, font=FONT_UI_S, fg=T["text3"],
                     bg=T["bg1"]).pack(side="left", padx=8)

        # Divider — gradient colored
        tk.Frame(self, bg=T["accent_dk"], height=1).pack(fill="x")

        # Spark overlay scoped to title bar
        self._spark_overlay = SparkOverlay(tb)
        self._spark_overlay.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        # Give the global cursor spark a canvas to draw on
        if hasattr(self, "_cursor_spark"):
            self._cursor_spark.set_canvas(self._spark_overlay)

    def _draw_title_gradient(self, e=None):
        # Debounce: cancel any pending redraw and schedule one after 200ms
        try:
            self.after_cancel(self._gradient_job)
        except Exception:
            pass
        self._gradient_job = self.after(200, self._do_draw_title_gradient)

    def _do_draw_title_gradient(self):
        try:
            c = self._titlebar_accent
            w = c.winfo_width()
            if w < 2:
                return
            c.delete("all")
            steps = min(w, 120)
            for i in range(steps):
                ratio = i / steps
                r = int(0xfa + (0x98 - 0xfa) * ratio)
                g = int(0x93 + (0x3a - 0x93) * ratio)
                b = int(0xfa + (0xd6 - 0xfa) * ratio)
                x = int(i * w / steps)
                x2 = int((i+1) * w / steps)
                c.create_rectangle(x, 0, x2, 3, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
        except Exception:
            pass

    def _animate_logo(self, phase=0):
        colors = [T["grad_start"], T["grad_mid"], T["grad_end"],
                  T["grad_mid"], T["grad_start"]]
        try:
            self._logo_lbl.configure(fg=colors[phase % len(colors)])
        except Exception:
            return
        self.after(1200, self._animate_logo, phase + 1)

    # ── Main Layout ───────────────────────────────────────────

    def _build_main(self):
        main = tk.Frame(self, bg=T["bg0"])
        main.pack(fill="both", expand=True)

        # Left sidebar  (240px)
        self._left = tk.Frame(main, bg=T["bg1"], width=240)
        self._left.pack(side="left", fill="y")
        self._left.pack_propagate(False)
        tk.Frame(main, bg=T["border"], width=1).pack(side="left", fill="y")

        # Center pane (preview + results)
        center = tk.Frame(main, bg=T["bg0"])
        center.pack(side="left", fill="both", expand=True)

        # Right sidebar (260px)
        tk.Frame(main, bg=T["border"], width=1).pack(side="left", fill="y")
        self._right = tk.Frame(main, bg=T["bg1"], width=260)
        self._right.pack(side="right", fill="y")
        self._right.pack_propagate(False)

        self._build_left_sidebar()
        self._build_center(center)
        self._build_right_sidebar()
        self._build_statusbar()

    # ── Left Sidebar ──────────────────────────────────────────

    def _build_left_sidebar(self):
        p = self._left

        # Section: File
        self._section_header(p, "FILE")

        # Drop zone
        drop = tk.Frame(p, bg=T["bg2"], cursor="hand2",
                        highlightthickness=1, highlightbackground=T["border"])
        drop.pack(fill="x", padx=12, pady=(0, 8))
        dz_inner = tk.Frame(drop, bg=T["bg2"])
        dz_inner.pack(fill="both", padx=16, pady=20)
        tk.Label(dz_inner, text="↑", font=("Segoe UI", 28), fg=T["text3"],
                 bg=T["bg2"]).pack()
        tk.Label(dz_inner, text="Drop PDF here", font=FONT_UI_S, fg=T["text3"],
                 bg=T["bg2"]).pack()
        tk.Label(dz_inner, text="or click Open", font=FONT_UI_S, fg=T["text3"],
                 bg=T["bg2"]).pack()

        for w in (drop, dz_inner) + tuple(dz_inner.winfo_children()):
            w.bind("<Button-1>", lambda e: self._open_file())
            w.bind("<Enter>", lambda e: drop.configure(highlightbackground=T["accent"]))
            w.bind("<Leave>", lambda e: drop.configure(highlightbackground=T["border"]))

        # Open button
        styled_btn(p, "  Open PDF File", self._open_file,
                   style="primary").pack(fill="x", padx=12, pady=(0, 6))
        styled_btn(p, "  Open Multiple", self._open_multiple,
                   style="ghost").pack(fill="x", padx=12, pady=(0, 8))

        divider(p, pady=(4, 8))

        # File info panel
        self._section_header(p, "FILE INFO")
        info_frame = tk.Frame(p, bg=T["bg1"])
        info_frame.pack(fill="x", padx=12)

        self._info_vars = {}
        for key in ("Name", "Size", "Pages", "Type"):
            row = tk.Frame(info_frame, bg=T["bg1"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{key}", font=FONT_UI_S, fg=T["text3"],
                     bg=T["bg1"], width=6, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            self._info_vars[key] = var
            tk.Label(row, textvariable=var, font=FONT_UI_S, fg=T["text2"],
                     bg=T["bg1"], anchor="w").pack(side="left", padx=4)

        divider(p, pady=(8, 8))

        # File list (recently opened)
        self._section_header(p, "LOADED FILES")
        list_frame = tk.Frame(p, bg=T["bg1"])
        list_frame.pack(fill="both", expand=True, padx=12)

        sb = tk.Scrollbar(list_frame, bg=T["bg1"], troughcolor=T["bg0"])
        sb.pack(side="right", fill="y")
        self._filelist = tk.Listbox(
            list_frame,
            bg=T["bg0"], fg=T["text2"],
            selectbackground=T["sel_bg"], selectforeground=T["white"],
            font=FONT_UI_S, relief="flat", bd=0,
            highlightthickness=0, activestyle="none",
            yscrollcommand=sb.set, cursor="hand2"
        )
        self._filelist.pack(fill="both", expand=True)
        sb.config(command=self._filelist.yview)
        self._filelist.bind("<Double-Button-1>", self._on_filelist_select)

        self._file_paths = []

        divider(p, pady=(8, 4))
        styled_btn(p, "Clear All", self._clear_files,
                   style="ghost", pady=4).pack(fill="x", padx=12, pady=(0, 8))

    # ── Center Panel ──────────────────────────────────────────

    def _build_center(self, parent):
        # Top toolbar
        toolbar = tk.Frame(parent, bg=T["bg1"], height=40)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        # Page nav
        nav = tk.Frame(toolbar, bg=T["bg1"])
        nav.pack(side="left", padx=12, fill="y")
        styled_btn(nav, "◀", self._prev_page, style="ghost", pady=2, padx=8).pack(side="left")
        self._page_label = tk.Label(nav, text="— / —", font=FONT_UI_S,
                                    fg=T["text2"], bg=T["bg1"])
        self._page_label.pack(side="left", padx=6)
        styled_btn(nav, "▶", self._next_page, style="ghost", pady=2, padx=8).pack(side="left")

        # Zoom
        zoom_frame = tk.Frame(toolbar, bg=T["bg1"])
        zoom_frame.pack(side="left", padx=8, fill="y")
        styled_btn(zoom_frame, "−", self._zoom_out, style="ghost", pady=2, padx=8).pack(side="left")
        self._zoom_label = tk.Label(zoom_frame, text="140%", font=FONT_UI_S,
                                    fg=T["text2"], bg=T["bg1"], width=5)
        self._zoom_label.pack(side="left")
        styled_btn(zoom_frame, "+", self._zoom_in, style="ghost", pady=2, padx=8).pack(side="left")

        # Quick extract
        styled_btn(toolbar, "⚡  Quick Extract (F5)", self._run_extraction,
                   style="primary", pady=4).pack(side="right", padx=12)

        tk.Frame(parent, bg=T["border"], height=1).pack(fill="x")

        # Paned window — preview top, results bottom
        paned = tk.PanedWindow(parent, orient="vertical",
                                bg=T["border"], sashwidth=4,
                                sashrelief="flat", handlesize=0)
        paned.pack(fill="both", expand=True)

        # Preview pane
        preview_outer = tk.Frame(paned, bg=T["bg0"])
        paned.add(preview_outer, minsize=180, stretch="always")

        # Canvas + scrollbars for PDF preview
        preview_inner = tk.Frame(preview_outer, bg=T["bg0"])
        preview_inner.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(preview_inner, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(preview_inner, orient="horizontal",
                             style="Thin.Horizontal.TScrollbar")
        hsb.pack(side="bottom", fill="x")

        self._preview_canvas = tk.Canvas(
            preview_inner, bg=T["bg0"],
            highlightthickness=0,
            xscrollcommand=hsb.set,
            yscrollcommand=vsb.set
        )
        self._preview_canvas.pack(fill="both", expand=True)
        vsb.config(command=self._preview_canvas.yview)
        hsb.config(command=self._preview_canvas.xview)
        self._preview_canvas.bind("<MouseWheel>", self._scroll_preview)
        self._preview_canvas.bind("<Control-MouseWheel>", self._ctrl_scroll)

        # Placeholder
        self._preview_canvas.create_text(
            400, 250, text="Open a PDF file to preview it here",
            font=FONT_UI, fill=T["text3"], tags="placeholder"
        )

        # Results pane (notebook)
        results_outer = tk.Frame(paned, bg=T["bg1"])
        paned.add(results_outer, minsize=200, stretch="always")
        self._build_results_panel(results_outer)

        paned.after(100, lambda: paned.sash_place(0, 0, 380))

    # ── Results Panel ─────────────────────────────────────────

    def _build_results_panel(self, parent):
        # Stats bar
        stats = tk.Frame(parent, bg=T["bg2"])
        stats.pack(fill="x")

        self._stat_vars = {}
        for key, label_text, color in [
            ("fields",     "FIELDS",     T["accent"]),
            ("items",      "LINE ITEMS", T["green"]),
            ("tables",     "TABLES",     T["purple"]),
            ("confidence", "CONFIDENCE", T["yellow"]),
            ("pages",      "PAGES",      T["text2"]),
        ]:
            box = tk.Frame(stats, bg=T["bg2"])
            box.pack(side="left", padx=16, pady=6)
            var = tk.StringVar(value="0")
            self._stat_vars[key] = var
            tk.Label(box, textvariable=var, font=FONT_UI_L,
                     fg=color, bg=T["bg2"]).pack()
            tk.Label(box, text=label_text, font=FONT_UI_S,
                     fg=T["text3"], bg=T["bg2"]).pack()

        # Progress bar (hidden by default)
        self._progress = ttk.Progressbar(parent, style="App.Horizontal.TProgressbar",
                                          mode="indeterminate")

        tk.Frame(parent, bg=T["border"], height=1).pack(fill="x")

        # Notebook tabs
        nb = ttk.Notebook(parent, style="App.TNotebook")
        nb.pack(fill="both", expand=True)
        self._results_nb = nb

        # Tab 1: Fields
        t1 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t1, text="  Fields  ")
        self._build_fields_tab(t1)

        # Tab 2: Line Items
        t2 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t2, text="  Line Items  ")
        self._build_items_tab(t2)

        # Tab 3: Tables
        t3 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t3, text="  Tables  ")
        self._build_tables_tab(t3)

        # Tab 4: JSON
        t4 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t4, text="  JSON  ")
        self._build_json_tab(t4)

        # Tab 5: Raw Text
        t5 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t5, text="  Raw Text  ")
        self._build_raw_tab(t5)

        # Tab 6: Export
        t6 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t6, text="  Export  ")
        self._build_export_tab(t6)

        # Tab 7: Gemini AI
        t7 = tk.Frame(nb, bg=T["bg0"])
        nb.add(t7, text="  ✦ Gemini AI  ")
        self._build_gemini_tab(t7)

    def _build_fields_tab(self, parent):
        """Key-value fields table."""
        frame = tk.Frame(parent, bg=T["bg0"])
        frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(frame, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")

        cols = ("field", "value")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style="App.Treeview", yscrollcommand=vsb.set)
        tree.heading("field", text="Field", anchor="w")
        tree.heading("value", text="Value", anchor="w")
        tree.column("field", width=220, anchor="w", stretch=False)
        tree.column("value", width=500, anchor="w")
        tree.pack(fill="both", expand=True)
        vsb.config(command=tree.yview)
        tree.tag_configure("alt", background=T["bg2"])
        tree.tag_configure("meta", foreground=T["text3"])
        tree.tag_configure("val",  foreground=T["text1"])
        tree.bind("<Double-Button-1>", self._copy_field_value)
        self._fields_tree = tree

    def _build_items_tab(self, parent):
        """Line items table."""
        frame = tk.Frame(parent, bg=T["bg0"])
        frame.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(frame, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(frame, orient="horizontal",
                             style="Thin.Horizontal.TScrollbar")
        hsb.pack(side="bottom", fill="x")

        self._items_tree = ttk.Treeview(frame, show="headings",
                                         style="App.Treeview",
                                         yscrollcommand=vsb.set,
                                         xscrollcommand=hsb.set)
        self._items_tree.pack(fill="both", expand=True)
        vsb.config(command=self._items_tree.yview)
        hsb.config(command=self._items_tree.xview)
        self._items_tree.tag_configure("alt", background=T["bg2"])

        # Placeholder
        self._items_placeholder = tk.Label(
            parent, text="No line items extracted.\nRun Invoice extraction to detect line items.",
            font=FONT_UI, fg=T["text3"], bg=T["bg0"], justify="center"
        )
        self._items_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _build_tables_tab(self, parent):
        """Tables from pdfplumber."""
        self._tables_container, self._tables_inner = scrollable_frame(parent, bg=T["bg0"])
        self._tables_container.pack(fill="both", expand=True)
        self._tables_placeholder = tk.Label(
            self._tables_inner,
            text="No tables extracted.\nRun Table or Auto extraction to detect tables.",
            font=FONT_UI, fg=T["text3"], bg=T["bg0"], justify="center", pady=40
        )
        self._tables_placeholder.pack()

    def _build_json_tab(self, parent):
        """JSON view with syntax-like coloring."""
        frame = tk.Frame(parent, bg=T["bg0"])
        frame.pack(fill="both", expand=True)

        toolbar = tk.Frame(frame, bg=T["bg1"])
        toolbar.pack(fill="x")
        styled_btn(toolbar, "Copy JSON", self._copy_json,
                   style="ghost", pady=3, padx=10).pack(side="left", padx=6, pady=4)
        styled_btn(toolbar, "Format / Collapse", lambda: None,
                   style="ghost", pady=3, padx=10).pack(side="left", pady=4)

        vsb = ttk.Scrollbar(frame, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(frame, orient="horizontal",
                             style="Thin.Horizontal.TScrollbar")
        hsb.pack(side="bottom", fill="x")

        self._json_text = tk.Text(
            frame, bg=T["bg0"], fg=T["text1"],
            font=FONT_MONO, insertbackground=T["accent"],
            relief="flat", bd=0, wrap="none",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
            state="disabled", padx=12, pady=8
        )
        self._json_text.pack(fill="both", expand=True)
        vsb.config(command=self._json_text.yview)
        hsb.config(command=self._json_text.xview)

        # Tags for highlighting
        self._json_text.tag_configure("key",    foreground="#79c0ff")
        self._json_text.tag_configure("string", foreground="#a5d6ff")
        self._json_text.tag_configure("number", foreground="#ffa657")
        self._json_text.tag_configure("bool",   foreground="#ff7b72")
        self._json_text.tag_configure("null",   foreground="#6e7681")
        self._json_text.tag_configure("punct",  foreground="#8b949e")

    def _build_raw_tab(self, parent):
        """Raw extracted text."""
        frame = tk.Frame(parent, bg=T["bg0"])
        frame.pack(fill="both", expand=True)

        toolbar = tk.Frame(frame, bg=T["bg1"])
        toolbar.pack(fill="x")
        styled_btn(toolbar, "Copy Text", self._copy_raw,
                   style="ghost", pady=3, padx=10).pack(side="left", padx=6, pady=4)
        self._raw_stats = tk.Label(toolbar, text="", font=FONT_UI_S,
                                    fg=T["text3"], bg=T["bg1"])
        self._raw_stats.pack(side="right", padx=12)

        vsb = ttk.Scrollbar(frame, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")

        self._raw_text = tk.Text(
            frame, bg=T["bg0"], fg=T["text2"],
            font=FONT_MONO, insertbackground=T["accent"],
            relief="flat", bd=0, wrap="word",
            yscrollcommand=vsb.set,
            state="disabled", padx=12, pady=8
        )
        self._raw_text.pack(fill="both", expand=True)
        vsb.config(command=self._raw_text.yview)

    def _build_export_tab(self, parent):
        """Export panel."""
        outer, inner = scrollable_frame(parent, bg=T["bg0"])
        outer.pack(fill="both", expand=True)

        pad = tk.Frame(inner, bg=T["bg0"])
        pad.pack(padx=32, pady=24, fill="x")

        tk.Label(pad, text="Export Extracted Data", font=FONT_UI_XL,
                 fg=T["text1"], bg=T["bg0"]).pack(anchor="w")
        tk.Label(pad, text="Choose a format to download your extraction results.",
                 font=FONT_UI, fg=T["text3"], bg=T["bg0"]).pack(anchor="w", pady=(2, 20))

        # Export format cards
        formats = [
            ("JSON", "Structured JSON format — great for APIs and developers",
             T["accent"], self._export_json),
            ("CSV", "Comma-separated — opens in Excel, Google Sheets",
             T["green"], self._export_csv),
            ("Excel (.xlsx)", "Styled Excel workbook with multiple sheets",
             T["yellow"], self._export_excel),
            ("XML", "Structured XML — ideal for enterprise integration",
             T["purple"], self._export_xml),
        ]
        for fmt, desc, color, cmd in formats:
            row = tk.Frame(pad, bg=T["bg2"],
                           highlightthickness=1, highlightbackground=T["border"])
            row.pack(fill="x", pady=4)
            left = tk.Frame(row, bg=T["bg2"])
            left.pack(side="left", fill="both", expand=True, padx=16, pady=12)
            tk.Label(left, text=fmt, font=FONT_UI_B, fg=color,
                     bg=T["bg2"]).pack(anchor="w")
            tk.Label(left, text=desc, font=FONT_UI_S, fg=T["text3"],
                     bg=T["bg2"]).pack(anchor="w")
            styled_btn(row, f"Export {fmt}", cmd,
                       style="ghost", pady=6, padx=14).pack(side="right", padx=12, pady=12)

        # Divider
        tk.Frame(pad, bg=T["border"], height=1).pack(fill="x", pady=(20, 16))

        # Clipboard
        tk.Label(pad, text="Clipboard", font=FONT_UI_B,
                 fg=T["text1"], bg=T["bg0"]).pack(anchor="w", pady=(0, 8))
        clip_row = tk.Frame(pad, bg=T["bg0"])
        clip_row.pack(anchor="w")
        styled_btn(clip_row, "Copy JSON to Clipboard", self._copy_json,
                   style="outline").pack(side="left", padx=(0, 8))
        styled_btn(clip_row, "Copy Raw Text", self._copy_raw,
                   style="outline").pack(side="left")

        # Export log
        tk.Frame(pad, bg=T["border"], height=1).pack(fill="x", pady=(20, 16))
        tk.Label(pad, text="Export History", font=FONT_UI_B,
                 fg=T["text1"], bg=T["bg0"]).pack(anchor="w", pady=(0, 8))
        self._export_log = tk.Text(
            pad, height=6, bg=T["bg2"], fg=T["text3"],
            font=FONT_MONO_S, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=T["border"],
            state="disabled", padx=8, pady=6
        )
        self._export_log.pack(fill="x")

    def _build_gemini_tab(self, parent):
        """
        Gemini AI tab — mirrors ResumeIQ's SettingsModal + AIPanel quality:
          • Provider cards with colour coding
          • Model badges with tier labels (Free / Premium)
          • Test API key button with live feedback
          • PDF source selector + upload
          • Task buttons (Arrange, Summarise, Tables, Invoice, Key Insights, Q&A)
          • Streaming-style animated output with syntax colouring
          • Copy / Save result
        """
        self._gemini_pdf_path    = None
        self._gemini_result_full = ""   # full result text for copy/save
        self._gemini_active_task = None
        self._gemini_streaming   = False

        # ── Outer scrollable container ──────────────────────
        outer, inner = scrollable_frame(parent, bg=T["bg0"])
        outer.pack(fill="both", expand=True)

        pad = tk.Frame(inner, bg=T["bg0"])
        pad.pack(padx=20, pady=14, fill="x")

        # ── Title row ──────────────────────────────────────
        title_row = tk.Frame(pad, bg=T["bg0"])
        title_row.pack(fill="x", pady=(0, 12))
        tk.Label(title_row, text="✦  Gemini AI Assistant",
                 font=("Segoe UI", 15, "bold"), fg=T["accent"], bg=T["bg0"]).pack(side="left")
        # "AI Ready" pill — shown when key is set
        self._gemini_ready_pill = tk.Label(
            title_row,
            text="● AI Ready",
            font=FONT_UI_S, fg="#166534",
            bg="#dcfce7",
            padx=8, pady=2,
            relief="flat"
        )
        self._gemini_ready_pill.pack(side="right")
        self._gemini_ready_pill.pack_forget()  # hidden until key is valid

        tk.Label(pad,
                 text="Powered by Google AI Studio — switch models, test your key, and analyse PDFs with Gemini.",
                 font=FONT_UI_S, fg=T["text3"], bg=T["bg0"]).pack(anchor="w", pady=(0, 14))

        # ═══════════════════════════════════════════════════
        # CARD 1 — API KEY
        # ═══════════════════════════════════════════════════
        key_card = tk.Frame(pad, bg=T["bg2"],
                            highlightthickness=1, highlightbackground=T["border"])
        key_card.pack(fill="x", pady=(0, 10))
        ki = tk.Frame(key_card, bg=T["bg2"])
        ki.pack(fill="x", padx=14, pady=12)

        tk.Label(ki, text="GOOGLE AI STUDIO API KEY",
                 font=("Segoe UI", 8, "bold"), fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(0, 6))

        key_row = tk.Frame(ki, bg=T["bg2"])
        key_row.pack(fill="x")

        self._gemini_key_var  = tk.StringVar()
        self._gemini_show_var = tk.BooleanVar(value=False)

        self._gemini_key_entry = tk.Entry(
            key_row, textvariable=self._gemini_key_var,
            show="•", font=FONT_MONO_S,
            bg=T["bg3"], fg=T["text1"], insertbackground=T["accent"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=T["border"],
            highlightcolor=T["accent"]
        )
        self._gemini_key_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))
        self._gemini_key_var.trace_add("write", self._on_gemini_key_change)

        def _toggle_show():
            self._gemini_key_entry.configure(
                show="" if self._gemini_show_var.get() else "•"
            )
        tk.Checkbutton(
            key_row, text="Show", variable=self._gemini_show_var,
            command=_toggle_show,
            font=FONT_UI_S, fg=T["text3"], bg=T["bg2"],
            selectcolor=T["bg3"], activebackground=T["bg2"],
            activeforeground=T["text2"]
        ).pack(side="left", padx=(0, 6))

        self._gemini_test_btn = styled_btn(
            key_row, "Test Key", self._gemini_test_key,
            style="ghost", pady=4, padx=10
        )
        self._gemini_test_btn.pack(side="left")

        # Test result banner
        self._gemini_key_result = tk.Label(
            ki, text="", font=FONT_UI_S, bg=T["bg2"],
            wraplength=520, justify="left", anchor="w"
        )
        self._gemini_key_result.pack(fill="x", pady=(5, 0))

        tk.Label(ki,
                 text="Get a free key at  aistudio.google.com/app/apikey  — free tier: Flash, Pro & Flash-Lite",
                 font=("Segoe UI", 8), fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(4, 0))

        # ═══════════════════════════════════════════════════
        # CARD 2 — MODEL SELECTOR  (provider tabs + model grid)
        # ═══════════════════════════════════════════════════
        model_card = tk.Frame(pad, bg=T["bg2"],
                              highlightthickness=1, highlightbackground=T["border"])
        model_card.pack(fill="x", pady=(0, 10))
        mi = tk.Frame(model_card, bg=T["bg2"])
        mi.pack(fill="x", padx=14, pady=12)

        tk.Label(mi, text="SELECT AI MODEL",
                 font=("Segoe UI", 8, "bold"), fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(0, 8))

        # Provider toggle buttons
        self._gemini_provider_var = tk.StringVar(value=AI_PROVIDERS[0]["id"])
        provider_row = tk.Frame(mi, bg=T["bg2"])
        provider_row.pack(fill="x", pady=(0, 10))

        self._gemini_model_var = tk.StringVar(value=DEFAULT_AI_MODEL)

        def _build_provider_btn(p):
            def _select():
                self._gemini_provider_var.set(p["id"])
                _refresh_model_grid()
            btn = tk.Button(
                provider_row,
                text=f"{p['icon']}  {p['name']}",
                command=_select,
                font=FONT_UI_S, relief="flat", bd=0, cursor="hand2",
                padx=10, pady=4
            )
            btn.pack(side="left", padx=(0, 6))
            def _upd(*_):
                active = self._gemini_provider_var.get() == p["id"]
                btn.configure(
                    bg=blend_color(p["color"], "22", T["bg3"]) if active else T["bg3"],
                    fg=p["color"] if active else T["text2"],
                    highlightthickness=2 if active else 1,
                    highlightbackground=p["color"] if active else T["border"],
                )
            self._gemini_provider_var.trace_add("write", _upd)
            _upd()

        for p in AI_PROVIDERS:
            _build_provider_btn(p)

        # Model grid (2 columns)
        self._gemini_model_grid = tk.Frame(mi, bg=T["bg2"])
        self._gemini_model_grid.pack(fill="x")

        def _refresh_model_grid():
            for w in self._gemini_model_grid.winfo_children():
                w.destroy()
            pid    = self._gemini_provider_var.get()
            prov   = next((p for p in AI_PROVIDERS if p["id"] == pid), AI_PROVIDERS[0])
            models = prov["models"]
            for i, m in enumerate(models):
                col = i % 2
                row = i // 2
                self._build_model_badge(self._gemini_model_grid, m, prov, row, col)

        def _build_model_badge_ref():
            pass
        self._refresh_model_grid = _refresh_model_grid

        def _build_mb(parent, m, prov, row, col):
            frame = tk.Frame(parent, bg=T["bg2"], cursor="hand2",
                             highlightthickness=2)
            frame.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            parent.grid_columnconfigure(col, weight=1)

            inner_f = tk.Frame(frame, bg=T["bg2"])
            inner_f.pack(fill="both", padx=10, pady=8)

            rb = tk.Radiobutton(
                inner_f, text=m["name"],
                value=m["id"], variable=self._gemini_model_var,
                font=FONT_UI_S, fg=T["text1"], bg=T["bg2"],
                selectcolor=T["bg2"], activebackground=T["bg2"],
                cursor="hand2"
            )
            rb.pack(side="left")

            tc, tbg = TIER_COLORS.get(m["tier"], (T["text2"], T["bg3"]))
            tk.Label(inner_f, text=m["badge"],
                     font=("Segoe UI", 8, "bold"),
                     fg=tc, bg=tbg,
                     padx=5, pady=1).pack(side="right")

            def _upd(*_):
                active = self._gemini_model_var.get() == m["id"]
                frame.configure(
                    highlightbackground=prov["color"] if active else T["border"],
                    bg=blend_color(prov["color"], "10", T["bg2"]) if active else T["bg2"]
                )
                inner_f.configure(bg=blend_color(prov["color"], "10", T["bg2"]) if active else T["bg2"])
                rb.configure(bg=blend_color(prov["color"], "10", T["bg2"]) if active else T["bg2"])

            self._gemini_model_var.trace_add("write", _upd)
            frame.bind("<Button-1>", lambda e, v=m["id"]: self._gemini_model_var.set(v))
            _upd()

        self._build_model_badge = _build_mb
        _refresh_model_grid()

        # Active model summary pill
        self._gemini_active_model_lbl = tk.Label(
            mi, text="", font=FONT_UI_S,
            fg=T["accent"], bg=T["bg2"], anchor="w"
        )
        self._gemini_active_model_lbl.pack(anchor="w", pady=(8, 0))
        self._gemini_model_var.trace_add("write", self._update_active_model_label)
        self._update_active_model_label()

        # ═══════════════════════════════════════════════════
        # CARD 3 — PDF SOURCE
        # ═══════════════════════════════════════════════════
        pdf_card = tk.Frame(pad, bg=T["bg2"],
                            highlightthickness=1, highlightbackground=T["border"])
        pdf_card.pack(fill="x", pady=(0, 10))
        pi = tk.Frame(pdf_card, bg=T["bg2"])
        pi.pack(fill="x", padx=14, pady=12)

        tk.Label(pi, text="PDF SOURCE",
                 font=("Segoe UI", 8, "bold"), fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(0, 6))

        self._gemini_use_pdf_var = tk.BooleanVar(value=True)
        opt_row = tk.Frame(pi, bg=T["bg2"])
        opt_row.pack(fill="x")
        tk.Radiobutton(opt_row, text="Send PDF directly to Gemini (native vision)",
                       variable=self._gemini_use_pdf_var, value=True,
                       font=FONT_UI_S, fg=T["text2"], bg=T["bg2"],
                       selectcolor=T["bg3"], activebackground=T["bg2"], cursor="hand2"
                       ).pack(side="left")
        tk.Radiobutton(opt_row, text="Use extracted text only",
                       variable=self._gemini_use_pdf_var, value=False,
                       font=FONT_UI_S, fg=T["text2"], bg=T["bg2"],
                       selectcolor=T["bg3"], activebackground=T["bg2"], cursor="hand2"
                       ).pack(side="left", padx=(16, 0))

        upload_row = tk.Frame(pi, bg=T["bg2"])
        upload_row.pack(fill="x", pady=(8, 0))
        self._gemini_pdf_label = tk.Label(
            upload_row, text="Using currently loaded PDF",
            font=FONT_UI_S, fg=T["text3"], bg=T["bg2"]
        )
        self._gemini_pdf_label.pack(side="left")
        styled_btn(upload_row, "Upload different PDF", self._gemini_browse_pdf,
                   style="ghost", pady=3, padx=10).pack(side="left", padx=8)
        styled_btn(upload_row, "✕ Clear", self._gemini_clear_pdf,
                   style="ghost", pady=3, padx=6).pack(side="left")

        # ═══════════════════════════════════════════════════
        # CARD 4 — AI TASKS  (mirrors AIPanel task buttons)
        # ═══════════════════════════════════════════════════
        task_card = tk.Frame(pad, bg=T["bg2"],
                             highlightthickness=1, highlightbackground=T["border"])
        task_card.pack(fill="x", pady=(0, 10))
        ti = tk.Frame(task_card, bg=T["bg2"])
        ti.pack(fill="x", padx=14, pady=12)

        tk.Label(ti, text="AI TASK",
                 font=("Segoe UI", 8, "bold"), fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(0, 8))

        # Task button grid (3 cols)
        task_grid = tk.Frame(ti, bg=T["bg2"])
        task_grid.pack(fill="x")
        self._gemini_task_btns = {}

        for i, t in enumerate(AI_TASKS):
            col = i % 3
            row = i // 3
            self._build_task_btn(task_grid, t, row, col)
        task_grid.grid_columnconfigure(0, weight=1)
        task_grid.grid_columnconfigure(1, weight=1)
        task_grid.grid_columnconfigure(2, weight=1)

        # Custom prompt / Q&A input
        tk.Label(ti, text="Custom prompt / question:",
                 font=FONT_UI_S, fg=T["text3"], bg=T["bg2"]).pack(anchor="w", pady=(10, 2))
        self._gemini_prompt_text = tk.Text(
            ti, height=3,
            bg=T["bg3"], fg=T["text1"],
            font=FONT_MONO_S, insertbackground=T["accent"],
            relief="flat", bd=0, padx=8, pady=5,
            highlightthickness=1, highlightbackground=T["border"],
            highlightcolor=T["accent"]
        )
        self._gemini_prompt_text.pack(fill="x", pady=(0, 4))
        self._gemini_prompt_text.insert("1.0", "What are the key financial figures in this document?")

        # ═══════════════════════════════════════════════════
        # RUN BUTTON + PROGRESS
        # ═══════════════════════════════════════════════════
        run_row = tk.Frame(pad, bg=T["bg0"])
        run_row.pack(fill="x", pady=(4, 8))

        self._gemini_run_btn = styled_btn(
            run_row, "  ✦  Run Gemini AI", self._gemini_run_last_task,
            style="primary", pady=10
        )
        self._gemini_run_btn.pack(side="left", padx=(0, 12))

        self._gemini_status_lbl = tk.Label(
            run_row, text="Select a task above, then click Run",
            font=FONT_UI_S, fg=T["text3"], bg=T["bg0"],
            wraplength=460, justify="left"
        )
        self._gemini_status_lbl.pack(side="left", fill="x")

        self._gemini_progress = ttk.Progressbar(
            pad, style="App.Horizontal.TProgressbar", mode="indeterminate"
        )

        # ═══════════════════════════════════════════════════
        # OUTPUT PANEL  (mirrors AIPanel output section)
        # ═══════════════════════════════════════════════════
        tk.Frame(pad, bg=T["border"], height=1).pack(fill="x", pady=(2, 10))

        result_hdr = tk.Frame(pad, bg=T["bg0"])
        result_hdr.pack(fill="x", pady=(0, 4))

        self._gemini_result_title = tk.Label(
            result_hdr, text="AI Response",
            font=FONT_UI_B, fg=T["text1"], bg=T["bg0"]
        )
        self._gemini_result_title.pack(side="left")

        # Spinner label (shown while streaming)
        self._gemini_spin_lbl = tk.Label(
            result_hdr, text="", font=FONT_UI_S, fg=T["accent"], bg=T["bg0"]
        )
        self._gemini_spin_lbl.pack(side="left", padx=8)

        btn_r = tk.Frame(result_hdr, bg=T["bg0"])
        btn_r.pack(side="right")
        styled_btn(btn_r, "📋 Copy", self._gemini_copy_result,
                   style="ghost", pady=2, padx=8).pack(side="left", padx=2)
        styled_btn(btn_r, "💾 Save .txt", self._gemini_save_result,
                   style="ghost", pady=2, padx=8).pack(side="left", padx=2)

        # Dashed placeholder (shown before first run)
        self._gemini_placeholder = tk.Frame(
            pad, bg=T["bg0"],
            highlightthickness=2, highlightbackground=T["border2"]
        )
        self._gemini_placeholder.pack(fill="x", pady=(0, 8))
        ph_inner = tk.Frame(self._gemini_placeholder, bg=T["bg0"])
        ph_inner.pack(padx=20, pady=32)
        tk.Label(ph_inner, text="✦", font=("Segoe UI", 28), fg=T["text3"], bg=T["bg0"]).pack()
        tk.Label(ph_inner, text="Select an AI task to get started",
                 font=FONT_UI_B, fg=T["text3"], bg=T["bg0"]).pack(pady=(4, 0))
        self._gemini_ph_key_lbl = tk.Label(
            ph_inner,
            text="🔑  Add your Google AI Studio key above",
            font=FONT_UI_S, fg="#d97706", bg="#fef3c7",
            padx=10, pady=3
        )
        self._gemini_ph_key_lbl.pack(pady=(6, 0))

        # Result text box (hidden until first run)
        result_frame = tk.Frame(pad, bg=T["bg2"],
                                highlightthickness=1, highlightbackground=T["border"])
        result_frame.pack(fill="x", pady=(0, 8))
        result_frame.pack_forget()
        self._gemini_result_frame = result_frame

        vsb = ttk.Scrollbar(result_frame, style="Thin.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")

        self._gemini_result_text = tk.Text(
            result_frame, height=24,
            bg=T["bg0"], fg=T["text1"],
            font=FONT_MONO_S, insertbackground=T["accent"],
            relief="flat", bd=0, padx=12, pady=10, wrap="word",
            yscrollcommand=vsb.set,
            state="disabled"
        )
        self._gemini_result_text.pack(fill="x")
        vsb.config(command=self._gemini_result_text.yview)

        # Syntax-highlight tags — same as ResumeIQ output panel
        self._gemini_result_text.tag_configure("h1",   font=("Segoe UI", 13, "bold"), foreground=T["accent"])
        self._gemini_result_text.tag_configure("h2",   font=("Segoe UI", 11, "bold"), foreground=T["accent2"])
        self._gemini_result_text.tag_configure("h3",   font=("Segoe UI", 10, "bold"), foreground=T["text1"])
        self._gemini_result_text.tag_configure("bold", font=("Consolas",  9, "bold"),  foreground=T["text1"])
        self._gemini_result_text.tag_configure("code", font=FONT_MONO_S,               foreground=T["green"], background=T["bg2"])
        self._gemini_result_text.tag_configure("tbl",  font=FONT_MONO_S,               foreground=T["yellow"])
        self._gemini_result_text.tag_configure("dim",  foreground=T["text3"])
        self._gemini_result_text.tag_configure("err",  foreground=T["red"])
        self._gemini_result_text.tag_configure("cursor", foreground=T["accent"])

        # Streaming cursor animation state
        self._gemini_cursor_on  = False
        self._gemini_cursor_job = None

    # ── Model badge builder ───────────────────────────────────

    def _build_task_btn(self, parent, t, row, col):
        """Build a single task button — mirrors AIPanel task buttons in ResumeIQ."""
        frame = tk.Frame(parent, bg=T["bg2"], cursor="hand2",
                         highlightthickness=1, highlightbackground=T["border"])
        frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        inner = tk.Frame(frame, bg=T["bg2"])
        inner.pack(fill="both", padx=10, pady=10)

        icon_lbl = tk.Label(inner, text=t["icon"],
                            font=("Segoe UI", 16), fg=T["text3"], bg=T["bg2"])
        icon_lbl.pack()
        name_lbl = tk.Label(inner, text=t["label"],
                            font=("Segoe UI", 9, "bold"), fg=T["text1"], bg=T["bg2"])
        name_lbl.pack()
        desc_lbl = tk.Label(inner, text=t["desc"],
                            font=("Segoe UI", 8), fg=T["text3"], bg=T["bg2"],
                            wraplength=110)
        desc_lbl.pack()

        self._gemini_task_btns[t["id"]] = {
            "frame": frame, "inner": inner,
            "icon": icon_lbl, "name": name_lbl, "desc": desc_lbl,
            "color": t["color"],
        }

        def _click(tid=t["id"]):
            self._gemini_active_task = tid
            self._update_task_btn_styles()
            self._run_gemini(tid)

        for w in (frame, inner, icon_lbl, name_lbl, desc_lbl):
            w.bind("<Button-1>", lambda e, f=_click: f())

        def _hover_enter(e, tid=t["id"]):
            info = self._gemini_task_btns[tid]
            frame.configure(highlightbackground=info["color"])
        def _hover_leave(e, tid=t["id"]):
            self._update_task_btn_styles()

        frame.bind("<Enter>", _hover_enter)
        frame.bind("<Leave>", _hover_leave)

    def _update_task_btn_styles(self):
        """Highlight the active task button — mirrors AIPanel isActive styling."""
        for tid, info in self._gemini_task_btns.items():
            active = tid == self._gemini_active_task
            color  = info["color"]
            bg     = blend_color(color, "20", T["bg2"]) if active else T["bg2"]
            info["frame"].configure(
                highlightbackground=color if active else T["border"],
                highlightthickness=2 if active else 1,
            )
            for w in (info["inner"], info["icon"], info["name"], info["desc"]):
                w.configure(bg=bg)
            info["icon"].configure(fg=color if active else T["text3"])
            info["name"].configure(fg=color if active else T["text1"])

    def _update_active_model_label(self, *_):
        mid  = self._gemini_model_var.get()
        info = ALL_AI_MODELS.get(mid)
        if info:
            self._gemini_active_model_lbl.configure(
                text=f"✦  Active model: {info['provider']}  —  {info['name']}  ·  {info['badge']}"
            )

    # ── Key helpers ───────────────────────────────────────────

    def _on_gemini_key_change(self, *_):
        """Hide test result and ready pill when key is edited."""
        self._gemini_key_result.configure(text="")
        self._gemini_ready_pill.pack_forget()
        self._gemini_ph_key_lbl.pack(pady=(6, 0))

    def _gemini_test_key(self):
        key = self._gemini_key_var.get().strip()
        if not key:
            self._gemini_key_result.configure(
                text="Enter an API key first.",
                fg=T["red"], bg="#fee2e2"
            )
            return
        self._gemini_test_btn.configure(text="Testing…", state="disabled", bg=T["bg3"])
        self._gemini_key_result.configure(text="", bg=T["bg2"])

        def worker():
            ok, msg = gemini_test_key(key)
            self.after(0, _done, ok, msg)

        def _done(ok, msg):
            self._gemini_test_btn.configure(text="Test Key", state="normal", bg=T["bg3"])
            self._gemini_key_result.configure(
                text=msg,
                fg="#166534" if ok else T["red"],
                bg="#dcfce7" if ok else "#fee2e2"
            )
            if ok:
                self._gemini_ready_pill.pack(side="right")
                self._gemini_ph_key_lbl.pack_forget()

        threading.Thread(target=worker, daemon=True).start()

    # ── PDF helpers ───────────────────────────────────────────

    def _gemini_browse_pdf(self):
        path = filedialog.askopenfilename(
            title="Choose PDF for Gemini",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if path:
            self._gemini_pdf_path = path
            name = os.path.basename(path)
            self._gemini_pdf_label.configure(
                text=f"Using: {name[:50]}", fg=T["green"]
            )

    def _gemini_clear_pdf(self):
        self._gemini_pdf_path = None
        self._gemini_pdf_label.configure(
            text="Using currently loaded PDF", fg=T["text3"]
        )

    # ── Run logic ─────────────────────────────────────────────

    def _gemini_run_last_task(self):
        """Run button click — uses the last selected task, or defaults to 'arrange'."""
        task = self._gemini_active_task or "arrange"
        self._gemini_active_task = task
        self._update_task_btn_styles()
        self._run_gemini(task)

    def _run_gemini(self, task_id):
        api_key = self._gemini_key_var.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your Google AI Studio API key.\n\n"
                "Get a free key at: https://aistudio.google.com/app/apikey"
            )
            return

        model        = self._gemini_model_var.get()
        use_pdf      = self._gemini_use_pdf_var.get()
        pdf_for_send = self._gemini_pdf_path or (self._pdf_path if use_pdf else None)
        custom       = self._gemini_prompt_text.get("1.0", "end").strip()

        if use_pdf and not pdf_for_send:
            messagebox.showwarning(
                "No PDF",
                "No PDF is loaded. Open a PDF first, "
                "or switch to 'Use extracted text only'."
            )
            return

        if not use_pdf and not self._result:
            ans = messagebox.askyesno(
                "No Extraction Data",
                "No extraction has been run yet.\n\n"
                "Send the loaded PDF to Gemini instead?"
            )
            if ans and self._pdf_path:
                use_pdf      = True
                pdf_for_send = self._pdf_path
            else:
                return

        # Build prompt (text-only path)
        prompt = build_gemini_prompt(task_id, self._result if not use_pdf else None, custom)

        # ── UI: busy state ────────────────────────────────
        self._gemini_run_btn.configure(
            text="  ⏳  Generating…", state="disabled", bg=T["accent_dk"]
        )
        self._gemini_progress.pack(fill="x", pady=(2, 6))
        self._gemini_progress.start(12)
        task_label = next((t["label"] for t in AI_TASKS if t["id"] == task_id), task_id)
        self._gemini_status_lbl.configure(
            text=f"Calling {model} — {task_label}…", fg=T["text3"]
        )
        self._gemini_streaming = True
        self._gemini_result_full = ""

        # Show result panel, hide placeholder
        self._gemini_placeholder.pack_forget()
        self._gemini_result_frame.pack(fill="x", pady=(0, 8))
        self._set_gemini_result("⏳  Waiting for Gemini response…", streaming=True)
        self._start_gemini_cursor()

        def worker():
            try:
                text = gemini_call(
                    api_key=api_key,
                    model=model,
                    prompt=prompt,
                    pdf_path=pdf_for_send if use_pdf else None,
                )
                self.after(0, self._on_gemini_done, text, None, task_label, model)
            except Exception as e:
                self.after(0, self._on_gemini_done, None, str(e), task_label, model)

        threading.Thread(target=worker, daemon=True).start()

    def _on_gemini_done(self, response, error, task_label, model):
        # Stop animation
        self._gemini_streaming = False
        self._stop_gemini_cursor()
        self._gemini_progress.stop()
        self._gemini_progress.pack_forget()
        self._gemini_run_btn.configure(
            text="  ✦  Run Gemini AI", state="normal", bg=T["accent"]
        )
        if error:
            self._gemini_status_lbl.configure(
                text=f"Error — {error[:100]}", fg=T["red"]
            )
            self._set_gemini_result(f"⚠  AI Error\n\n{error}", error=True)
        else:
            self._gemini_result_full = response
            self._gemini_status_lbl.configure(
                text=f"✓  Done  —  {model}  ·  {task_label}", fg=T["green"]
            )
            self._set_gemini_result(response)

    # ── Streaming cursor animation ─────────────────────────────

    def _start_gemini_cursor(self):
        self._gemini_cursor_on = True
        self._animate_gemini_cursor()

    def _stop_gemini_cursor(self):
        self._gemini_cursor_on = False
        if self._gemini_cursor_job:
            self.after_cancel(self._gemini_cursor_job)
            self._gemini_cursor_job = None
        # Remove cursor mark from text
        try:
            w = self._gemini_result_text
            w.configure(state="normal")
            w.delete("cursor_start", "cursor_end")
        except Exception:
            pass
        try:
            w.configure(state="disabled")
        except Exception:
            pass

    def _animate_gemini_cursor(self):
        if not self._gemini_cursor_on:
            return
        # Toggle ▍ at the end of text
        try:
            w = self._gemini_result_text
            w.configure(state="normal")
            try:
                w.delete("cursor_start", "cursor_end")
            except Exception:
                pass
            w.mark_set("cursor_start", "end-1c")
            w.insert("end", "▍", "cursor")
            w.mark_set("cursor_end", "end-1c")
            w.configure(state="disabled")
        except Exception:
            pass
        self._gemini_cursor_job = self.after(500, self._animate_gemini_cursor)

    # ── Markdown-aware result renderer ────────────────────────

    def _set_gemini_result(self, text, streaming=False, error=False):
        """
        Write text into the result box with Markdown-style highlighting.
        Mirrors ResumeIQ's streamed output panel rendering.
        """
        w = self._gemini_result_text
        w.configure(state="normal")
        w.delete("1.0", "end")

        if error:
            # Split error nicely
            lines = text.split("\n")
            for line in lines:
                if line.startswith("⚠"):
                    w.insert("end", line + "\n", "err")
                elif line.startswith("•"):
                    w.insert("end", line + "\n", "dim")
                else:
                    w.insert("end", line + "\n", "err" if line.strip() else "dim")
            w.configure(state="disabled")
            return

        in_code = False
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                w.insert("end", line + "\n", "dim")
                continue
            if in_code:
                w.insert("end", line + "\n", "code")
                continue
            if stripped.startswith("### "):
                w.insert("end", line + "\n", "h3")
            elif stripped.startswith("## "):
                w.insert("end", line + "\n", "h2")
            elif stripped.startswith("# "):
                w.insert("end", line + "\n", "h1")
            elif "|" in stripped and stripped.startswith("|"):
                w.insert("end", line + "\n", "tbl")
            elif stripped.startswith(("- ", "* ", "• ")):
                w.insert("end", "  " + line.lstrip() + "\n")
            elif stripped.startswith("⏳"):
                w.insert("end", line + "\n", "dim")
            else:
                # Inline **bold** splitting
                parts = re.split(r"(\*\*[^*]+\*\*)", line)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        w.insert("end", part[2:-2], "bold")
                    else:
                        w.insert("end", part)
                w.insert("end", "\n")

        w.configure(state="disabled")
        w.see("end")

    # ── Copy / Save ───────────────────────────────────────────

    def _gemini_copy_result(self):
        content = self._gemini_result_full.strip()
        if not content:
            # Fall back to whatever is in the text widget
            content = self._gemini_result_text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self._gemini_status_lbl.configure(
                text="📋  Copied to clipboard", fg=T["green"]
            )

    def _gemini_save_result(self):
        content = self._gemini_result_full.strip()
        if not content:
            messagebox.showwarning("No Result", "Nothing to save yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="gemini_result.txt",
            filetypes=[
                ("Text File", "*.txt"),
                ("Markdown",  "*.md"),
                ("All Files", "*.*"),
            ]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._gemini_status_lbl.configure(
                text=f"💾  Saved → {os.path.basename(path)}", fg=T["green"]
            )

    # ── Right Sidebar ─────────────────────────────────────────

    def _build_right_sidebar(self):
        p = self._right

        self._section_header(p, "EXTRACTION MODE")

        self._mode_var = tk.StringVar(value="auto")
        modes = [
            ("auto",    "⬡  Auto Detect",      "Automatically identify document type"),
            ("invoice", "⬡  Invoice / Receipt", "Vendors, dates, totals, line items"),
            ("form",    "⬡  Form Fields",       "Labels and field values"),
            ("table",   "⬡  Tables Only",       "Extract all tabular data"),
            ("custom",  "⬡  Custom Patterns",   "User-defined regex fields"),
        ]
        for val, txt, desc in modes:
            self._build_mode_row(p, val, txt, desc)

        divider(p, pady=(8, 8))

        # Custom patterns
        self._section_header(p, "CUSTOM PATTERNS")
        tk.Label(p, text="Format: FieldName: regex_pattern",
                 font=FONT_UI_S, fg=T["text3"], bg=T["bg1"]).pack(anchor="w", padx=12)
        tk.Label(p, text="Use group () to capture value",
                 font=FONT_UI_S, fg=T["text3"], bg=T["bg1"]).pack(anchor="w", padx=12, pady=(0, 4))

        self._custom_text = tk.Text(
            p, height=7, bg=T["bg0"], fg=T["text2"],
            font=FONT_MONO_S, insertbackground=T["accent"],
            relief="flat", bd=0, padx=8, pady=6,
            highlightthickness=1, highlightbackground=T["border"],
            highlightcolor=T["accent"]
        )
        self._custom_text.pack(fill="x", padx=12, pady=(0, 4))
        self._custom_text.insert("1.0",
            "# Examples:\nEmail: ([\\w.+%-]+@[\\w.-]+\\.[a-z]{2,})\n"
            "Phone: ((?:\\+?\\d[\\d\\s-]{8,15}))\n"
            "Amount: \\$([\\d,]+\\.?\\d{0,2})\n"
            "Date: (\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4})"
        )

        divider(p, pady=(8, 8))

        # Options
        self._section_header(p, "OPTIONS")

        self._ocr_var = tk.BooleanVar(value=False)
        ocr_row = tk.Frame(p, bg=T["bg1"])
        ocr_row.pack(fill="x", padx=12, pady=4)
        tk.Checkbutton(
            ocr_row, text="Enable OCR (scanned PDFs)",
            variable=self._ocr_var,
            font=FONT_UI_S, fg=T["text2"], bg=T["bg1"],
            selectcolor=T["bg3"], activebackground=T["bg1"],
            activeforeground=T["text1"]
        ).pack(side="left")

        self._bbox_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            p, text="Show bounding boxes",
            variable=self._bbox_var,
            font=FONT_UI_S, fg=T["text2"], bg=T["bg1"],
            selectcolor=T["bg3"], activebackground=T["bg1"],
            activeforeground=T["text1"]
        ).pack(anchor="w", padx=12, pady=4)

        divider(p, pady=(8, 12))

        # Extract button
        self._extract_btn = styled_btn(
            p, "  Extract Data  (F5)", self._run_extraction,
            style="primary", pady=10
        )
        self._extract_btn.pack(fill="x", padx=12)

        # Status
        self._extract_status = tk.Label(p, text="", font=FONT_UI_S,
                                         fg=T["text3"], bg=T["bg1"],
                                         wraplength=220, justify="left")
        self._extract_status.pack(fill="x", padx=12, pady=4)

        divider(p, pady=(8, 8))

        # Legend
        self._section_header(p, "BBOX LEGEND")
        legend_frame = tk.Frame(p, bg=T["bg1"])
        legend_frame.pack(fill="x", padx=12, pady=(0, 8))
        for color, lbl in [(T["green"], "Text blocks"),
                            (T["accent"], "Tables"),
                            (T["yellow"], "Form fields")]:
            row = tk.Frame(legend_frame, bg=T["bg1"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="■", fg=color, bg=T["bg1"], font=FONT_UI_S).pack(side="left")
            tk.Label(row, text=f"  {lbl}", fg=T["text3"], bg=T["bg1"],
                     font=FONT_UI_S).pack(side="left")

    def _build_mode_row(self, parent, value, text, desc):
        frame = tk.Frame(parent, bg=T["bg1"], cursor="hand2")
        frame.pack(fill="x", padx=8, pady=1)

        rb = tk.Radiobutton(
            frame, text=text, value=value,
            variable=self._mode_var,
            font=FONT_UI_S, fg=T["text2"], bg=T["bg1"],
            selectcolor=T["bg1"],
            activebackground=T["bg1"], activeforeground=T["text1"],
            indicatoron=True, cursor="hand2",
            command=self._on_mode_change
        )
        rb.pack(side="left", padx=4)

        def on_hover_enter(e):
            frame.configure(bg=T["bg3"])
            rb.configure(bg=T["bg3"])
        def on_hover_leave(e):
            frame.configure(bg=T["bg1"])
            rb.configure(bg=T["bg1"])
        frame.bind("<Enter>", on_hover_enter)
        frame.bind("<Leave>", on_hover_leave)
        rb.bind("<Enter>", on_hover_enter)
        rb.bind("<Leave>", on_hover_leave)
        frame.bind("<Button-1>", lambda e: self._mode_var.set(value))

        # Update colors when selected
        def update_color(*args):
            selected = self._mode_var.get() == value
            rb.configure(fg=T["accent"] if selected else T["text2"])
        self._mode_var.trace_add("write", update_color)

    def _on_mode_change(self):
        pass  # Could show/hide custom text area

    # ── Status Bar ────────────────────────────────────────────

    def _build_statusbar(self):
        # ── Top divider ───────────────────────────────────────
        tk.Frame(self, bg=T["border"], height=1).pack(fill="x", side="bottom")

        # ── Footer bar ───────────────────────────────────────
        footer = tk.Frame(self, bg=T["bg1"], height=42)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        # Status label (left)
        self._status_var = tk.StringVar(value="Ready — open a PDF to get started")
        tk.Label(footer, textvariable=self._status_var, font=FONT_UI_S,
                 fg=T["text3"], bg=T["bg1"]).pack(side="left", padx=12)

        # ── Creator + social (right side) ────────────────────
        right = tk.Frame(footer, bg=T["bg1"])
        right.pack(side="right", padx=10, fill="y")

        # Creator label
        creator = tk.Label(right, text="✦  Created by",
                           font=("Segoe UI", 8), fg=T["text3"], bg=T["bg1"])
        creator.pack(side="left", padx=(0, 4))

        name_lbl = tk.Label(right, text="D4RK TIG3R",
                            font=("Segoe UI", 9, "bold"), fg=T["accent2"], bg=T["bg1"],
                            cursor="hand2")
        name_lbl.pack(side="left", padx=(0, 10))
        self._animate_creator_label(name_lbl)

        # Divider pip
        tk.Label(right, text="·", font=FONT_UI_S, fg=T["text3"],
                 bg=T["bg1"]).pack(side="left", padx=(0, 8))

        # Social links: (icon, label, url)
        socials = [
            ("⌥", "GitHub",    "https://github.com/d4rktig3r"),
            ("◈", "Instagram", "https://instagram.com/d4rktig3r"),
            ("✕", "X / Twitter","https://x.com/d4rktig3r"),
            ("▶", "YouTube",   "https://youtube.com/@d4rktig3r"),
        ]
        social_colors = {
            "GitHub":     "#a8b4c0",
            "Instagram":  "#fa93fa",
            "X / Twitter":"#a8b4c0",
            "YouTube":    "#f87171",
        }
        for icon, name, url in socials:
            col = social_colors.get(name, T["text2"])
            btn = tk.Label(right,
                           text=f"{icon} {name}",
                           font=("Segoe UI", 8, "bold"),
                           fg=col, bg=T["bg1"],
                           cursor="hand2", padx=6, pady=2)
            btn.pack(side="left", padx=2)
            btn.bind("<Enter>", lambda e, b=btn, c=col: b.configure(
                fg=T["accent2"], bg=T["bg3"]))
            btn.bind("<Leave>", lambda e, b=btn, c=col: b.configure(
                fg=c, bg=T["bg1"]))
            btn.bind("<Button-1>", lambda e, u=url: self._open_url(u))

        # Accent line above footer
        tk.Frame(self, bg=T["accent_dk"], height=1).pack(fill="x", side="bottom")

    def _animate_creator_label(self, lbl, phase=0):
        colors = [T["grad_start"], T["accent"], T["grad_end"],
                  T["accent"], T["grad_start"]]
        try:
            lbl.configure(fg=colors[phase % len(colors)])
        except Exception:
            return
        self.after(600, self._animate_creator_label, lbl, phase + 1)

    def _open_url(self, url):
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # ── UI Helpers ────────────────────────────────────────────

    def _section_header(self, parent, text):
        row = tk.Frame(parent, bg=T["bg1"])
        row.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(row, text=text, font=("Segoe UI", 8, "bold"),
                 fg=T["text3"], bg=T["bg1"]).pack(side="left")

    def _set_status(self, text, color=None):
        self._status_var.set(text)
        if color:
            self._extract_status.configure(text=text, fg=color)

    # ── File Operations ───────────────────────────────────────

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if path:
            self._load_pdf(path)

    def _open_multiple(self):
        paths = filedialog.askopenfilenames(
            title="Open PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        for p in paths:
            self._add_to_filelist(p)
        if paths:
            self._load_pdf(paths[0])

    def _add_to_filelist(self, path):
        if path not in self._file_paths:
            self._file_paths.append(path)
            name = os.path.basename(path)
            disp = name if len(name) <= 26 else name[:23] + "..."
            self._filelist.insert("end", f"  {disp}")

    def _on_filelist_select(self, event):
        sel = self._filelist.curselection()
        if sel and sel[0] < len(self._file_paths):
            self._load_pdf(self._file_paths[sel[0]])

    def _clear_files(self):
        self._file_paths.clear()
        self._filelist.delete(0, "end")

    def _load_pdf(self, path):
        if not os.path.isfile(path):
            messagebox.showerror("Error", f"File not found:\n{path}")
            return
        self._pdf_path = path
        self._page_num = 0
        self._total_pages = pdf_page_count(path)

        # File info
        stat = os.stat(path)
        size = stat.st_size
        size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
        name = os.path.basename(path)
        self._info_vars["Name"].set(name[:22] + ("..." if len(name) > 22 else ""))
        self._info_vars["Size"].set(size_str)
        self._info_vars["Pages"].set(str(self._total_pages))
        self._info_vars["Type"].set("PDF")

        self._add_to_filelist(path)
        self._render_preview()
        self._set_status(f"Loaded: {name}  ({self._total_pages} pages)")

    def _quick_save(self):
        if self._result:
            self._export_json()

    # ── PDF Preview ───────────────────────────────────────────

    def _render_preview(self):
        if not self._pdf_path or self._total_pages == 0:
            return
        try:
            from PIL import ImageTk
            img = pdf_render_page(self._pdf_path, self._page_num, self._zoom)
            self._photo = ImageTk.PhotoImage(img)
            c = self._preview_canvas
            c.delete("all")
            c.configure(scrollregion=(0, 0, img.width + 40, img.height + 40))
            # Shadow
            c.create_rectangle(22, 22, img.width + 22, img.height + 22,
                                fill="#000000", outline="")
            # Page image
            c.create_image(20, 20, anchor="nw", image=self._photo)
            # Bounding boxes if result exists
            if self._result and self._bbox_var.get():
                self._draw_bboxes(img.width, img.height)
            self._page_label.configure(
                text=f"{self._page_num + 1} / {self._total_pages}"
            )
            self._zoom_label.configure(text=f"{int(self._zoom*100)}%")
        except ImportError:
            self._preview_canvas.delete("all")
            self._preview_canvas.create_text(
                400, 200, text="Pillow not installed.\nRun: pip install Pillow",
                font=FONT_UI, fill=T["red"]
            )
        except Exception as e:
            self._set_status(f"Preview error: {e}")

    def _draw_bboxes(self, img_w, img_h):
        """Draw bounding boxes on the preview for text blocks."""
        if not self._pdf_path:
            return
        try:
            blocks = pdf_get_text_blocks(self._pdf_path, self._page_num)
            import fitz
            doc = fitz.open(self._pdf_path)
            page = doc[self._page_num]
            pw, ph = page.rect.width, page.rect.height
            doc.close()
            if pw == 0 or ph == 0:
                return
            sx = (img_w / pw)
            sy = (img_h / ph)
            c = self._preview_canvas
            for bx0, by0, bx1, by1, _ in blocks[:40]:
                x0 = bx0 * sx + 20
                y0 = by0 * sy + 20
                x1 = bx1 * sx + 20
                y1 = by1 * sy + 20
                c.create_rectangle(x0, y0, x1, y1,
                                   outline=T["green"], width=1)
        except Exception:
            pass

    def _prev_page(self):
        if self._page_num > 0:
            self._page_num -= 1
            self._render_preview()

    def _next_page(self):
        if self._page_num < self._total_pages - 1:
            self._page_num += 1
            self._render_preview()

    def _zoom_in(self):
        if self._zoom < 3.0:
            self._zoom = round(self._zoom + 0.1, 1)
            self._render_preview()

    def _zoom_out(self):
        if self._zoom > 0.4:
            self._zoom = round(self._zoom - 0.1, 1)
            self._render_preview()

    def _scroll_preview(self, event):
        self._preview_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _ctrl_scroll(self, event):
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    # ── Extraction ────────────────────────────────────────────

    def _run_extraction(self):
        if not self._pdf_path:
            messagebox.showwarning("No File", "Please open a PDF file first.")
            return

        mode = self._mode_var.get()
        custom = self._custom_text.get("1.0", "end").strip()
        use_ocr = self._ocr_var.get()

        # UI: extracting state
        self._extract_btn.configure(text="  Extracting...", state="disabled",
                                     bg=T["accent_dk"])
        self._progress.pack(fill="x")
        self._progress.start(12)
        self._extract_status.configure(text="Running extraction...", fg=T["text3"])
        self._set_status("Extracting...")

        def worker():
            result = run_extraction(
                path=self._pdf_path,
                mode=mode,
                custom_patterns=custom,
                use_ocr=use_ocr,
                ocr_lang=self._settings.get("ocr_lang", "eng"),
                tess_cmd=self._settings.get("tesseract_cmd", ""),
            )
            self.after(0, self._on_done, result)

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, result):
        """Called on main thread when extraction completes."""
        # Reset UI
        self._progress.stop()
        self._progress.pack_forget()
        self._extract_btn.configure(text="  Extract Data  (F5)",
                                     state="normal", bg=T["accent"])

        if result.get("error"):
            msg = result["error"]
            self._extract_status.configure(text=f"Error: {msg[:80]}", fg=T["red"])
            self._set_status(f"Error: {msg[:60]}")
            messagebox.showerror("Extraction Error", msg)
            return

        self._result = result
        data = result.get("data", {})
        conf = data.get("_confidence", 0)
        dtype = data.get("_type", "Unknown")
        detected = result.get("detected", "")

        status_text = f"✓  {dtype}"
        if detected:
            status_text = f"✓  Auto-detected: {detected.title()}"
        status_text += f"  —  {int(conf*100)}% confidence"

        self._extract_status.configure(text=status_text, fg=T["green"])
        self._set_status(f"Extraction complete  |  {status_text}")

        # Update stats
        n_fields = len(data.get("_fields", {}))
        n_items  = len(data.get("_line_items", []))
        n_tables = len(data.get("_tables", []))
        n_pages  = result.get("pages", 0)

        self._stat_vars["fields"].set(str(n_fields))
        self._stat_vars["items"].set(str(n_items))
        self._stat_vars["tables"].set(str(n_tables))
        self._stat_vars["confidence"].set(f"{int(conf*100)}%")
        self._stat_vars["pages"].set(str(n_pages))

        # Populate all tabs
        self._populate_fields(result)
        self._populate_items(result)
        self._populate_tables(result)
        self._populate_json(result)
        self._populate_raw(result)

        # Refresh preview with bboxes
        self._render_preview()

        # Switch to Fields tab
        self._results_nb.select(0)

    # ── Populate Tabs ─────────────────────────────────────────

    def _populate_fields(self, result):
        tree = self._fields_tree
        tree.delete(*tree.get_children())
        data = result.get("data", {})

        # Metadata section
        meta = [
            ("Document Type",  data.get("_type", "Unknown")),
            ("Confidence",     f"{int(data.get('_confidence', 0)*100)}%"),
            ("Source File",    result.get("filename", "")),
            ("Pages",          str(result.get("pages", ""))),
            ("Mode",           result.get("mode", "")),
            ("Extracted At",   result.get("timestamp", "")),
        ]
        if result.get("detected"):
            meta.append(("Auto-detected Type", result["detected"].title()))

        for i, (k, v) in enumerate(meta):
            tag = ("alt", "meta") if i % 2 == 0 else ("meta",)
            tree.insert("", "end", values=(k, v), tags=tag)

        # Separator
        tree.insert("", "end", values=("", ""), tags=("alt",))

        # Extracted fields
        fields = data.get("_fields", {})
        if fields:
            for i, (k, v) in enumerate(fields.items()):
                tag = ("alt", "val") if i % 2 == 0 else ("val",)
                tree.insert("", "end", values=(k, str(v)), tags=tag)
        else:
            tree.insert("", "end", values=("No fields extracted",
                        "Try a different mode or enable OCR for scanned PDFs"))

    def _populate_items(self, result):
        tree = self._items_tree
        items = result.get("data", {}).get("_line_items", [])

        tree.delete(*tree.get_children())

        if not items:
            self._items_placeholder.place(relx=0.5, rely=0.5, anchor="center")
            tree["columns"] = ()
            return

        self._items_placeholder.place_forget()
        cols = list(items[0].keys())
        tree["columns"] = cols
        tree["show"] = "headings"
        for col in cols:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, width=160, anchor="w")

        for i, item in enumerate(items):
            tag = ("alt",) if i % 2 == 0 else ()
            tree.insert("", "end",
                        values=[str(item.get(c, "")) for c in cols],
                        tags=tag)

    def _populate_tables(self, result):
        # Clear inner frame
        for w in self._tables_inner.winfo_children():
            w.destroy()

        tables = result.get("data", {}).get("_tables", [])
        if not tables:
            tk.Label(self._tables_inner,
                     text="No tables found.\nRun Table or Auto extraction mode.",
                     font=FONT_UI, fg=T["text3"], bg=T["bg0"],
                     justify="center", pady=40).pack()
            return

        for tbl in tables:
            # Table header card
            hdr = tk.Frame(self._tables_inner, bg=T["bg2"],
                           highlightthickness=1, highlightbackground=T["border"])
            hdr.pack(fill="x", padx=16, pady=(12, 0))
            tk.Label(hdr,
                     text=f"  Table {tbl['index']}  —  Page {tbl['page']}  |  "
                          f"{tbl['rows']} rows × {tbl['cols']} cols",
                     font=FONT_UI_S, fg=T["accent"], bg=T["bg2"],
                     pady=6).pack(side="left")

            # Table content (mini treeview)
            tframe = tk.Frame(self._tables_inner, bg=T["bg0"])
            tframe.pack(fill="x", padx=16, pady=(0, 4))

            data = tbl["data"]
            if not data:
                continue
            ncols = max(len(r) for r in data)
            col_ids = [f"c{i}" for i in range(ncols)]

            hsb = ttk.Scrollbar(tframe, orient="horizontal",
                                 style="Thin.Horizontal.TScrollbar")
            hsb.pack(side="bottom", fill="x")

            tv = ttk.Treeview(tframe, columns=col_ids, show="headings",
                               style="App.Treeview", height=min(len(data), 8),
                               xscrollcommand=hsb.set)
            tv.pack(fill="x")
            hsb.config(command=tv.xview)
            tv.tag_configure("alt", background=T["bg2"])

            # Use first row as header if it looks like one
            start = 0
            headers = data[0] if data else []
            for ci, cid in enumerate(col_ids):
                h = headers[ci] if ci < len(headers) else f"Col {ci+1}"
                tv.heading(cid, text=h or f"Col {ci+1}", anchor="w")
                tv.column(cid, width=120, anchor="w", minwidth=60)
            start = 1

            for ri, row in enumerate(data[start:], 1):
                vals = [row[ci] if ci < len(row) else "" for ci in range(ncols)]
                tag = ("alt",) if ri % 2 == 0 else ()
                tv.insert("", "end", values=vals, tags=tag)

    def _populate_json(self, result):
        # Build clean output dict
        data = result.get("data", {})
        out = {
            "meta": {
                "filename":   result.get("filename"),
                "pages":      result.get("pages"),
                "mode":       result.get("mode"),
                "detected":   result.get("detected", result.get("mode")),
                "timestamp":  result.get("timestamp"),
                "confidence": data.get("_confidence", 0),
            },
            "document_type": data.get("_type", "unknown"),
            "fields":      data.get("_fields", {}),
            "line_items":  data.get("_line_items", []),
            "tables":      [
                {"page": t["page"], "rows": t["rows"],
                 "cols": t["cols"], "data": t["data"]}
                for t in data.get("_tables", [])
            ],
        }
        text = json.dumps(out, indent=2, ensure_ascii=False, default=str)

        t = self._json_text
        t.configure(state="normal")
        t.delete("1.0", "end")
        self._insert_json(t, text)
        t.configure(state="disabled")

    def _insert_json(self, widget, text):
        """Insert JSON text with syntax highlighting."""
        lines = text.split("\n")
        for line in lines:
            # Key: "key":
            km = re.match(r'^(\s*)("(?:[^"\\]|\\.)*")(\s*:\s*)(.*)', line)
            if km:
                widget.insert("end", km.group(1))
                widget.insert("end", km.group(2), "key")
                widget.insert("end", km.group(3), "punct")
                self._insert_json_value(widget, km.group(4))
            else:
                stripped = line.strip()
                self._insert_json_value(widget, line)
            widget.insert("end", "\n")

    def _insert_json_value(self, widget, val):
        stripped = val.strip().rstrip(",")
        if stripped.startswith('"'):
            widget.insert("end", val, "string")
        elif re.match(r'^-?\d[\d.]*$', stripped):
            widget.insert("end", val, "number")
        elif stripped in ("true", "false"):
            widget.insert("end", val, "bool")
        elif stripped == "null":
            widget.insert("end", val, "null")
        else:
            widget.insert("end", val, "punct")

    def _populate_raw(self, result):
        raw = result.get("raw_text", "")
        t = self._raw_text
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.insert("1.0", raw)
        t.configure(state="disabled")
        words = len(raw.split())
        chars = len(raw)
        lines = raw.count("\n") + 1
        self._raw_stats.configure(
            text=f"{lines} lines  ·  {words} words  ·  {chars} chars"
        )

    # ── Copy / Clipboard ──────────────────────────────────────

    def _copy_field_value(self, event):
        """Copy a field value to clipboard on double-click."""
        tree = self._fields_tree
        sel = tree.selection()
        if sel:
            val = tree.item(sel[0], "values")
            if val and len(val) > 1:
                self.clipboard_clear()
                self.clipboard_append(val[1])
                self._set_status(f"Copied: {val[1][:60]}")

    def _copy_json(self):
        if not self._result:
            return
        data = self._result.get("data", {})
        out = {
            "fields":     data.get("_fields", {}),
            "line_items": data.get("_line_items", []),
            "tables":     [{"page": t["page"], "data": t["data"]}
                           for t in data.get("_tables", [])],
        }
        self.clipboard_clear()
        self.clipboard_append(json.dumps(out, indent=2, default=str))
        self._set_status("JSON copied to clipboard")

    def _copy_raw(self):
        if not self._result:
            return
        self.clipboard_clear()
        self.clipboard_append(self._result.get("raw_text", ""))
        self._set_status("Raw text copied to clipboard")

    # ── Export ────────────────────────────────────────────────

    def _check_result(self):
        if not self._result:
            messagebox.showwarning("No Data", "Please run extraction first.")
            return False
        return True

    def _get_save_path(self, ext, desc):
        stem = os.path.splitext(self._result.get("filename", "output"))[0]
        return filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=f"{stem}_extracted{ext}",
            filetypes=[(desc, f"*{ext}"), ("All Files", "*.*")]
        )

    def _log_export(self, fmt, path):
        entry = f"{datetime.now().strftime('%H:%M:%S')}  [{fmt}]  {os.path.basename(path)}\n"
        self._export_log.configure(state="normal")
        self._export_log.insert("1.0", entry)
        self._export_log.configure(state="disabled")

    def _export_json(self):
        if not self._check_result(): return
        path = self._get_save_path(".json", "JSON File")
        if not path: return
        try:
            do_export_json(self._result, path)
            self._log_export("JSON", path)
            self._set_status(f"Exported JSON → {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_csv(self):
        if not self._check_result(): return
        path = self._get_save_path(".csv", "CSV File")
        if not path: return
        try:
            do_export_csv(self._result, path)
            self._log_export("CSV", path)
            self._set_status(f"Exported CSV → {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_excel(self):
        if not self._check_result(): return
        path = self._get_save_path(".xlsx", "Excel File")
        if not path: return
        try:
            do_export_excel(self._result, path)
            self._log_export("XLSX", path)
            self._set_status(f"Exported Excel → {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_xml(self):
        if not self._check_result(): return
        path = self._get_save_path(".xml", "XML File")
        if not path: return
        try:
            do_export_xml(self._result, path)
            self._log_export("XML", path)
            self._set_status(f"Exported XML → {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Settings ──────────────────────────────────────────────

    def _open_settings(self):
        win = tk.Toplevel(self)
        win.title("Settings")
        win.configure(bg=T["bg1"])
        win.geometry("480x380")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        # Center
        self.update_idletasks()
        x = self.winfo_x() + self.winfo_width()//2 - 240
        y = self.winfo_y() + self.winfo_height()//2 - 190
        win.geometry(f"+{x}+{y}")

        tk.Frame(win, bg=T["border"], height=1).pack(fill="x")
        header = tk.Frame(win, bg=T["bg2"])
        header.pack(fill="x")
        tk.Label(header, text="Settings", font=FONT_UI_L, fg=T["text1"],
                 bg=T["bg2"], pady=12, padx=16).pack(side="left")
        tk.Frame(win, bg=T["border"], height=1).pack(fill="x")

        body = tk.Frame(win, bg=T["bg1"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        def row(label_text, widget_factory):
            r = tk.Frame(body, bg=T["bg1"])
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label_text, font=FONT_UI_S, fg=T["text2"],
                     bg=T["bg1"], width=20, anchor="w").pack(side="left")
            w = widget_factory(r)
            w.pack(side="left", fill="x", expand=True)
            return w

        # OCR language
        lang_var = tk.StringVar(value=self._settings.get("ocr_lang", "eng"))
        lang_combo = row("OCR Language", lambda p: ttk.Combobox(
            p, textvariable=lang_var,
            values=["eng", "fra", "deu", "spa", "hin", "por", "ita", "zho"],
            style="App.TCombobox", state="readonly", width=12
        ))

        # Tesseract path
        tess_var = tk.StringVar(value=self._settings.get("tesseract_cmd", ""))
        tess_entry = row("Tesseract Path", lambda p: tk.Entry(
            p, textvariable=tess_var, font=FONT_UI_S,
            bg=T["bg3"], fg=T["text1"], insertbackground=T["accent"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=T["border"]
        ))

        def browse_tess():
            path = filedialog.askopenfilename(filetypes=[("Exe", "*.exe"), ("All", "*.*")])
            if path:
                tess_var.set(path)
        styled_btn(body, "Browse for tesseract.exe", browse_tess,
                   style="ghost", pady=4).pack(anchor="w", pady=(0, 12))

        tk.Frame(body, bg=T["border"], height=1).pack(fill="x", pady=8)

        def save_settings():
            self._settings["ocr_lang"] = lang_var.get()
            self._settings["tesseract_cmd"] = tess_var.get()
            win.destroy()
            self._set_status("Settings saved")

        btn_row = tk.Frame(body, bg=T["bg1"])
        btn_row.pack(anchor="e", pady=8)
        styled_btn(btn_row, "Cancel", win.destroy, style="ghost",
                   pady=6).pack(side="left", padx=4)
        styled_btn(btn_row, "Save Settings", save_settings, style="primary",
                   pady=6).pack(side="left")

    # ── Help ──────────────────────────────────────────────────

    def _show_help(self):
        win = tk.Toplevel(self)
        win.title("Help")
        win.configure(bg=T["bg1"])
        win.geometry("520x480")
        win.transient(self)

        header = tk.Frame(win, bg=T["bg2"])
        header.pack(fill="x")
        tk.Label(header, text="PDF Extraction Suite — Help",
                 font=FONT_UI_L, fg=T["text1"], bg=T["bg2"],
                 pady=12, padx=16).pack(side="left")
        tk.Frame(win, bg=T["border"], height=1).pack(fill="x")

        txt = scrolledtext.ScrolledText(
            win, bg=T["bg0"], fg=T["text2"], font=FONT_UI,
            relief="flat", bd=0, padx=16, pady=12, wrap="word"
        )
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", """QUICK START
─────────────────────────────────────────
1.  Open a PDF using File → Open or drag-drop.
2.  Select an Extraction Mode from the right panel.
3.  Click Extract Data or press F5.
4.  View results in the Fields / Tables / JSON tabs.
5.  Use the ✦ Gemini AI tab to analyse with Google AI.
6.  Export using the Export tab.

EXTRACTION MODES
─────────────────────────────────────────
Auto Detect       Analyses document keywords to pick the best mode.
Invoice/Receipt   Extracts vendors, dates, totals, line items, tax.
Form Fields       Finds label:value pairs (forms, applications).
Tables Only       Uses pdfplumber to extract structured tables.
Custom Patterns   You define field names + regex patterns.

✦ GEMINI AI  (Google AI Studio — free)
─────────────────────────────────────────
1. Get a free API key at https://aistudio.google.com
2. Enter the key in the Gemini AI tab.
3. Choose a model (gemini-2.0-flash is fastest & free).
4. Select a task: Arrange, Summarise, Tables, Invoice, Q&A, or Custom.
5. Choose PDF source: send PDF directly or use extracted text.
6. Click Run Gemini AI.

Free models available:
  gemini-2.0-flash        Fast, multimodal, latest
  gemini-2.0-flash-lite   Ultra-fast, low cost
  gemini-1.5-flash        Reliable multimodal
  gemini-1.5-flash-8b     Lightweight version
  gemini-1.5-pro          Most capable (slower)

CUSTOM PATTERNS FORMAT
─────────────────────────────────────────
One pattern per line:  FieldName: regex_pattern
Use a capture group () to extract a specific part.

Examples:
  Invoice No: INV-([\\d]+)
  Email: ([\\w.+%-]+@[\\w.-]+\\.[a-z]{2,})
  Total: \\$([\\d,]+\\.?\\d{0,2})

KEYBOARD SHORTCUTS
─────────────────────────────────────────
  Ctrl+O   Open PDF file
  F5       Run extraction
  Ctrl+S   Quick save as JSON

OCR (SCANNED PDFs)
─────────────────────────────────────────
Enable the OCR checkbox for scanned documents.
Requires Tesseract installed on your system.
Set the path in Settings if auto-detection fails.
  Windows: C:\\Program Files\\Tesseract-OCR\\tesseract.exe
  Linux/Mac: usually /usr/bin/tesseract

REQUIREMENTS
─────────────────────────────────────────
  pip install PyMuPDF pdfplumber Pillow openpyxl pytesseract
  (No extra package needed for Gemini — uses built-in urllib)
""")
        txt.configure(state="disabled")


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

def check_deps():
    missing = []
    for mod, pkg in [("fitz","PyMuPDF"), ("pdfplumber","pdfplumber"),
                     ("PIL","Pillow"), ("openpyxl","openpyxl")]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    return missing


if __name__ == "__main__":
    missing = check_deps()
    if missing:
        root = tk.Tk()
        root.withdraw()
        msg = ("Missing dependencies:\n\n" +
               "\n".join(f"  • {m}" for m in missing) +
               "\n\nRun:\n  pip install " + " ".join(missing))
        messagebox.showerror("Missing Packages", msg)
        root.destroy()
    else:
        app = PDFExtractorApp()
        app.mainloop()
