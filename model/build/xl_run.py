# SPDX-License-Identifier: Apache-2.0
"""Save a workbook, recalculate it with Excel, and reload with cached values."""
import subprocess, os
import openpyxl


def recalc(path):
    ps = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recalc_excel.ps1")
    out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps, path],
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0 or "recalculated" not in out.stdout:
        raise RuntimeError(out.stdout + out.stderr)


def save_and_recalc(wb, path):
    wb.save(path)
    recalc(path)
    return openpyxl.load_workbook(path, data_only=True)


def cell(addr):
    return addr.split("!")[1].replace("$", "")


ERR_CODES = ("#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!", "#SPILL!", "#CALC!")


def errors(wbv):
    return [(ws.title, c.coordinate, c.value) for ws in wbv for row in ws.iter_rows() for c in row
            if isinstance(c.value, str) and c.value in ERR_CODES]


def scrub_metadata(path, creator="AI unit economics planning tool (fictional worked example)"):
    """Remove personal and local information that Excel writes on save: last-modified-by and the stored local file path."""
    import re, shutil, zipfile
    tmp = path + ".scrub"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                t = data.decode("utf-8")
                t = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", "<cp:lastModifiedBy></cp:lastModifiedBy>", t)
                t = re.sub(r"<dc:creator>.*?</dc:creator>", f"<dc:creator>{creator}</dc:creator>", t)
                data = t.encode("utf-8")
            elif item.filename == "xl/workbook.xml":
                t = data.decode("utf-8")
                t = re.sub(r"<mc:AlternateContent[^>]*>(?:(?!</mc:AlternateContent>).)*?absPath(?:(?!</mc:AlternateContent>).)*?</mc:AlternateContent>", "", t, flags=re.S)
                data = t.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
