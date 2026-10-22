import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
import os, sys, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

APP_TITLE = "Affidavit Maker"
class App:
    def __init__(self, root):
        self.root=root
        root.title(APP_TITLE)
        root.geometry("900x780")
        root.minsize(760,650)
        self.kind=tk.StringVar(value="name")
        self.fields={}
        self.files={}
        top=ttk.Frame(root,padding=14); top.pack(fill="x")
        ttk.Label(top,text="AFFIDAVIT MAKER",font=("Arial",18,"bold")).pack(anchor="w")
        ttk.Label(top,text="Two separate formats based on your uploaded samples • PDF output • Local/offline use").pack(anchor="w",pady=(4,0))
        choose=ttk.LabelFrame(root,text="Select affidavit format",padding=10); choose.pack(fill="x",padx=14,pady=6)
        ttk.Radiobutton(choose,text="1. Name Change Affidavit",variable=self.kind,value="name",command=self.render_fields).pack(side="left",padx=8)
        ttk.Radiobutton(choose,text="2. After Marriage Affidavit (Husband + Wife)",variable=self.kind,value="marriage",command=self.render_fields).pack(side="left",padx=8)
        self.body=ttk.Frame(root,padding=(14,4)); self.body.pack(fill="both",expand=True)
        self.render_fields()
        bottom=ttk.Frame(root,padding=14); bottom.pack(fill="x")
        ttk.Button(bottom,text="Generate Affidavit PDF",command=self.generate).pack(side="left")
        ttk.Button(bottom,text="Clear Form",command=self.clear).pack(side="left",padx=8)
        ttk.Label(bottom,text="Review the generated draft before signing/notarizing.",foreground="#8d1027").pack(side="right")

    def render_fields(self):
        for w in self.body.winfo_children(): w.destroy()
        self.fields={}; self.files={}
        canvas=tk.Canvas(self.body,highlightthickness=0)
        scroll=ttk.Scrollbar(self.body,orient="vertical",command=canvas.yview)
        inner=ttk.Frame(canvas)
        inner.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0),window=inner,anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand=True); scroll.pack(side="right",fill="y")
        if self.kind.get()=="name":
            specs=[
                ("old_name","Old Name / Surname *"),("new_name","Correct / New Name *"),("address","Full Address *"),
                ("place","Place","Ahmedabad"),("date","Date",date.today().strftime("%d/%m/%Y")),
                ("declaration","Optional reason / extra declaration","")
            ]
            for s in specs: self.add_entry(inner,*s)
            self.add_file(inner,"photo","Applicant Photo")
            self.add_file(inner,"sign","Applicant Signature")
            ttk.Label(inner,text="Name-change wording follows the uploaded sample structure. Confirm names against source documents.",wraplength=760).pack(anchor="w",pady=10)
        else:
            specs=[
                ("husband_name","Husband full name *"),("wife_old","Wife old / pre-marriage name *"),("wife_new","Wife new / post-marriage name *"),
                ("address","Joint residential address *"),("religion","Religion",""),("marriage_date","Marriage date (DD/MM/YYYY) *",""),
                ("marriage_place","Place of marriage *","Ahmedabad"),("place","Affidavit place","Ahmedabad"),
                ("date","Affidavit date",date.today().strftime("%d/%m/%Y")),("extra","Optional additional declaration","")
            ]
            for s in specs: self.add_entry(inner,*s)
            self.add_file(inner,"joint_photo","Joint Husband-Wife Photo")
            self.add_file(inner,"husband_sign","Husband Signature")
            self.add_file(inner,"wife_sign","Wife Signature")
            ttk.Label(inner,text="After-marriage wording follows the uploaded sample structure. Add only accurate details; do not use this format if the facts differ.",wraplength=760).pack(anchor="w",pady=10)

    def add_entry(self,parent,key,label,default=""):
        row=ttk.Frame(parent); row.pack(fill="x",pady=4)
        ttk.Label(row,text=label,width=29).pack(side="left",anchor="nw")
        if key in ("address","declaration","extra"):
            widget=tk.Text(row,height=3 if key=="address" else 2,width=70,wrap="word")
            widget.pack(side="left",fill="x",expand=True)
            if default: widget.insert("1.0",default)
        else:
            widget=ttk.Entry(row,width=75)
            widget.pack(side="left",fill="x",expand=True)
            if default: widget.insert(0,default)
        self.fields[key]=widget

    def add_file(self,parent,key,label):
        row=ttk.Frame(parent); row.pack(fill="x",pady=4)
        ttk.Label(row,text=label,width=29).pack(side="left")
        v=tk.StringVar(value="No file selected")
        self.files[key]=v
        ttk.Label(row,textvariable=v,width=52).pack(side="left",fill="x",expand=True)
        ttk.Button(row,text="Browse…",command=lambda k=key,vv=v:self.pick_file(k,vv)).pack(side="left")

    def pick_file(self,key,var):
        p=filedialog.askopenfilename(title="Select image",filetypes=[("Image files","*.png *.jpg *.jpeg *.bmp"),("All files","*.*")])
        if p: self.files[key]=p; var.set(os.path.basename(p))

    def get(self,key):
        w=self.fields.get(key)
        if not w:return ""
        return w.get("1.0","end").strip() if isinstance(w,tk.Text) else w.get().strip()

    def clear(self):
        if messagebox.askyesno("Clear","Clear all fields and selected images?"):
            self.render_fields()

    def generate(self):
        kind=self.kind.get()
        required = ["old_name","new_name","address"] if kind=="name" else ["husband_name","wife_old","wife_new","address","marriage_date"]
        missing=[k for k in required if not self.get(k)]
        if missing:
            messagebox.showerror("Missing information","Please fill all required fields marked with *.")
            return
        target=filedialog.asksaveasfilename(title="Save affidavit PDF",defaultextension=".pdf",filetypes=[("PDF file","*.pdf")],initialfile=("Name_Change_Affidavit.pdf" if kind=="name" else "After_Marriage_Affidavit.pdf"))
        if not target:return
        try:
            if kind=="name": self.make_name_pdf(target)
            else: self.make_marriage_pdf(target)
            messagebox.showinfo("Success","Affidavit PDF created:\n"+target+"\n\nPlease review all text and image placement before use.")
        except Exception as e:
            messagebox.showerror("Could not create PDF",str(e))

    def styles(self):
        ss=getSampleStyleSheet()
        return (
            ParagraphStyle("AffTitle",parent=ss["Title"],fontName="Times-Bold",fontSize=15,leading=18,alignment=TA_CENTER,spaceAfter=18,textColor=colors.black),
            ParagraphStyle("AffBody",parent=ss["BodyText"],fontName="Times-Roman",fontSize=11.2,leading=16,alignment=TA_LEFT,spaceAfter=10),
            ParagraphStyle("Small",parent=ss["BodyText"],fontName="Times-Roman",fontSize=10,leading=13,alignment=TA_LEFT,spaceAfter=4)
        )
    def safe(self,s):
        from xml.sax.saxutils import escape
        return escape(s or "").replace("\n","<br/>")
    def add_img(self,path,w,h):
        if path and os.path.isfile(path):
            im=RLImage(path,width=w,height=h)
            im.hAlign="CENTER"
            return im
        return Paragraph(" ",self.styles()[2])

    def make_name_pdf(self,path):
        title,body,small=self.styles()
        d=SimpleDocTemplate(path,pagesize=A4,rightMargin=25*mm,leftMargin=25*mm,topMargin=22*mm,bottomMargin=22*mm)
        old,new,addr=self.get("old_name"),self.get("new_name"),self.get("address")
        place=self.get("place") or "Ahmedabad"; dt=self.get("date") or date.today().strftime("%d/%m/%Y")
        reason=self.get("declaration") or "No additional declaration."
        story=[Paragraph("AFFIDAVIT",title)]
        photo=self.files.get("photo","")
        if photo and os.path.isfile(photo):
            story.append(self.add_img(photo,25*mm,30*mm)); story.append(Spacer(1,5*mm))
        story.append(Paragraph(f"I, the undersigned <b>{self.safe(old)}</b>, aged adult, residing at <b>{self.safe(addr)}</b>, do hereby state on oath as under:",body))
        story.append(Paragraph(f"1. That my correct full name is <b>{self.safe(new)}</b>, which is mentioned in my Aadhaar Card, Election Card, etc., but in some of my documents my name is mentioned as <b>{self.safe(old)}</b>, and hence I want to change/correct my name in Government Gazette.",body))
        story.append(Paragraph("2. That I have made this affidavit to produce before the Govt. Printing &amp; Stationery, Rajkot for change of my name as under:",body))
        story.append(Spacer(1,4*mm))
        story.append(Paragraph(f"<b>Old Name:</b> {self.safe(old)}",body))
        story.append(Paragraph(f"<b>New Name:</b> {self.safe(new)}",body))
        story.append(Paragraph(f"3. That what is stated above is true and correct to the best of my knowledge and belief. {self.safe(reason)}",body))
        story.append(Spacer(1,8*mm))
        story.append(Paragraph(f"Place: {self.safe(place)}",body)); story.append(Paragraph(f"Date: {self.safe(dt)}",body))
        sign=self.files.get("sign","")
        if sign and os.path.isfile(sign): story.append(self.add_img(sign,38*mm,15*mm))
        story.append(Spacer(1,8*mm)); story.append(Paragraph("(Signature of Deponent)",ParagraphStyle("right",parent=small,alignment=TA_RIGHT)))
        d.build(story)

    def make_marriage_pdf(self,path):
        title,body,small=self.styles()
        d=SimpleDocTemplate(path,pagesize=A4,rightMargin=22*mm,leftMargin=22*mm,topMargin=18*mm,bottomMargin=18*mm)
        husband,wold,wnew,addr=self.get("husband_name"),self.get("wife_old"),self.get("wife_new"),self.get("address")
        rel=self.get("religion") or "________"; md=self.get("marriage_date"); mp=self.get("marriage_place") or "Ahmedabad"
        place=self.get("place") or "Ahmedabad"; dt=self.get("date") or date.today().strftime("%d/%m/%Y"); extra=self.get("extra") or ""
        story=[Paragraph("AFFIDAVIT",title)]
        jp=self.files.get("joint_photo","")
        if jp and os.path.isfile(jp): story.append(self.add_img(jp,42*mm,30*mm)); story.append(Spacer(1,4*mm))
        story.append(Paragraph(f"We, the undersigned, Deponent No. 1, <b>{self.safe(husband)}</b>, and Deponent No. 2, <b>{self.safe(wold)}</b>, both major/adults, both {self.safe(rel)} by religion, presently residing at <b>{self.safe(addr)}</b>,",body))
        story.append(Paragraph("We, the deponents, do hereby take oath according to our religion and solemnly affirm and declare through this Affidavit that:",body))
        story.append(Paragraph(f"1. We, the deponents, are presently residing with our family at the above-mentioned address.",body))
        story.append(Paragraph(f"2. We, the deponents, state that our marriage was solemnized on <b>{self.safe(md)}</b> at <b>{self.safe(mp)}</b> according to our religion, in the presence of our parents, family members, elders, guests and witnesses. Since then, we have become the legally wedded husband and wife of each other. We hereby declare the same through this Affidavit.",body))
        story.append(Paragraph("3. We state that our marriage was solemnized in a simple manner. If applicable, we did not print or issue a wedding invitation card and have not obtained a Marriage Certificate. Please edit this clause if it does not accurately describe your circumstances.",body))
        story.append(Paragraph(f"4. The pre-marriage/old name of Deponent No. 2, <b>{self.safe(wold)}</b>, is required to be published in the Gujarat Government Gazette as the post-marriage/new name, <b>{self.safe(wnew)}</b>. Therefore, this Affidavit is being submitted as proof of the husband-wife relationship before the office of the Manager, Government Printing and Stationery, Rajkot.",body))
        story.append(Paragraph(f"<b>Old Name:</b> {self.safe(wold)}",body)); story.append(Paragraph(f"<b>New Name:</b> {self.safe(wnew)}",body))
        story.append(Paragraph(f"5. We hereby declare that all facts stated above are true and correct to the best of our knowledge and belief. {self.safe(extra)}",body))
        story.append(Spacer(1,5*mm)); story.append(Paragraph(f"Place: {self.safe(place)}",body)); story.append(Paragraph(f"Date: {self.safe(dt)}",body))
        hsign=self.files.get("husband_sign",""); wsign=self.files.get("wife_sign","")
        cells=[]
        for label,p in [("Signature of Deponent No. 1 (Husband)",hsign),("Signature of Deponent No. 2 (Wife)",wsign)]:
            cell=[]
            if p and os.path.isfile(p): cell.append(RLImage(p,width=38*mm,height=15*mm))
            else: cell.append(Spacer(1,15*mm))
            cell.append(Paragraph(label,small)); cells.append(cell)
        table=Table([[cells[0],cells[1]]],colWidths=[78*mm,78*mm])
        table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM"),("ALIGN",(0,0),(-1,-1),"LEFT"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),8*mm),("TOPPADDING",(0,0),(-1,-1),10*mm)]))
        story.append(table)
        d.build(story)

if __name__=="__main__":
    root=tk.Tk()
    try: ttk.Style().theme_use("vista")
    except: pass
    App(root)
    root.mainloop()
