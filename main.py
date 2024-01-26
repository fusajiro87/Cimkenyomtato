import tkinter
import pyodbc
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
from datetime import date
from zebrafy import ZebrafyImage
import os
import socket
import qrcode
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter import ttk
import ping


window = tkinter.Tk()
window.title("Címke nyomtatás")
window.geometry('+50+50')
frame = tkinter.Frame(window)
frame.pack()

font = ("Arial", 10)

# Főablak
cimkenyomtato_frame = tkinter.LabelFrame(frame)
cimkenyomtato_frame.grid(row=0, column=0, padx=20, pady= 10)
cimkenyomtato_label = tkinter.Label(cimkenyomtato_frame, text="Címkenyomtató", font=("Arial", 20))
cimkenyomtato_label.grid(row=0, column=0, padx=20, pady= 10)

#Adatok frame
adatok_frame = tkinter.LabelFrame(frame)
adatok_frame.grid(row=1, column=0)

# Munkaszám
munkaszam_label = tkinter.Label(adatok_frame, text="Munkaszám", font=font)
munkaszam_label.grid(row=0, column=0, padx=20, pady=10)
munkaszam_entry = tkinter.Entry(adatok_frame, font=font, width=50)
munkaszam_entry.grid(row=0, column=1, padx=20, pady=10)

# Vevő
vevo_label = tkinter.Label(adatok_frame, text="Vevő", font=font)
vevo_label.grid(row=1, column=0, padx=20, pady=10)
vevo_entry = tkinter.Entry(adatok_frame, font=font, width=50)
vevo_entry.grid(row=1, column=1, padx=20, pady=10)

# Rajzszám
rajzszam_label = tkinter.Label(adatok_frame, text="Rajzszám", font=font)
rajzszam_label.grid(row=2, column=0, padx=20, pady=10)
rajzszam_entry = tkinter.Entry(adatok_frame, font=font, width=50)
rajzszam_entry.grid(row=2, column=1, padx=20, pady=10)

# Megnevezés
megnevezes_label = tkinter.Label(adatok_frame, text="Megnevezés", font=font)
megnevezes_label.grid(row=3, column=0, padx=20, pady=10)
megnevezes_entry = tkinter.Entry(adatok_frame, font=font, width=50)
megnevezes_entry.grid(row=3, column=1, padx=20, pady=10)

# Nyelv
nyelv_select = tkinter.StringVar()
nyelv_label = tkinter.Label(adatok_frame, text="Nyelv", font=font)
nyelv_label.grid(row=4, column=0, padx=20)
nyelv_entry = ttk.Radiobutton(adatok_frame, text="angol", variable=nyelv_select, value="angol")
nyelv_entry_2 = ttk.Radiobutton(adatok_frame, text="magyar", variable=nyelv_select, value="magyar")
nyelv_entry.grid(row=4, column=1, sticky = "W", padx=20)
nyelv_entry_2.grid(row=4, column=1, sticky = "", padx=20)

# Mennyiség
mennyiseg_label = tkinter.Label(adatok_frame, text="Mennyiség", font=font)
mennyiseg_label.grid(row=5, column=0, padx=20, pady=10)
mennyiseg_entry = tkinter.Entry(adatok_frame, font=font, width=50)
mennyiseg_entry.grid(row=5, column=1, padx=20, pady=10)

# Ellenőrizte
inspectors = ["Hetényi", "István", "Lázi", "László", "Papucsek", "Álmos", "Major", "Gábor", "Gondos", "István"]
ellenorizte_entry_values = [inspectors[0] + " " + inspectors[1],
                            inspectors[2] + " " + inspectors[3],
                            inspectors[4] + " " + inspectors[5],
                            inspectors[6] + " " + inspectors[7],
                            inspectors[8] + " " + inspectors[9]]
ellenorizte_label = tkinter.Label(adatok_frame, text="Ellenőrizte", font=font)
ellenorizte_label.grid(row=6, column=0, padx=20, pady=10)
ellenorizte_entry = AutocompleteCombobox(adatok_frame, font=font, width=48, completevalues=ellenorizte_entry_values)
ellenorizte_entry.grid(row=6, column=1, padx=20, pady=10)
ellenorizte_entry['values'] = ellenorizte_entry_values

# Nyomtatási mennyiség
peldanyszam_label = tkinter.Label(adatok_frame, text="Példányszám", font=font)
peldanyszam_label.grid(row=7, column=0, padx=20, pady=10)
peldanyszam_entry = tkinter.Entry(adatok_frame, font=font, width=50)
peldanyszam_entry.grid(row=7, column=1, padx=20, pady=10)
peldanyszam_entry.insert(0, "1")

def adatok_betoltese(*args):

    answer = ping.zebra_ping()
    if answer == "Request":
        tkinter.messagebox.showwarning(title="Nyomtató", message=("Kapcsolati hiba! Lehetséges okok:\n"
                                                                  " - A nyomtató nem üzemel megfelelően.\n"
                                                                  " - A számítógép nem csatlakozik a hálózatra.\n"
                                                                  " - A helyi hálózaton váratlan probléma lépett fel.\n"
                                                                  "\n"
                                                                  "Lehetséges megoldások:\n"
                                                                  " - Címkenyomtató program újraindítása.\n"
                                                                  " - Nyomtató újraindítása.\n"
                                                                  " - Számítógép újraindítása.\n"))
        exit()

    global cimke
    filtered_rows = []
    row = ""
    vevo_entry.delete(0, 'end')
    rajzszam_entry.delete(0, 'end')
    megnevezes_entry.delete(0, 'end')
    mennyiseg_entry.delete(0, 'end')

    try:
        cnxn = pyodbc.connect('DSN=szerver')
        cursor = cnxn.cursor()
        cursor.execute('''
        select vevo.nev,
        torzs.rajzszam,
        kereskedelem02_munkaszam.munkaszam,
        termeles_program.zaras_datum,
        raktar_pozicio_katalogus01.megnevezes as raktar_pozicio_megnevezes,
        kereskedelem02.torzsszam,
        torzs.megnevezes 
        from holes_aw_kereskedelem.kereskedelem02_munkaszam 
        left join holes_aw_kereskedelem.kereskedelem02 on kereskedelem02.azonosito=kereskedelem02_munkaszam.azonosito_kereskedelem02
        left join holes_aw_kereskedelem.kereskedelem01 on kereskedelem01.azonosito=kereskedelem02.azonosito_kereskedelem01
        left join holes_aw.vevo on vevo.kod=kereskedelem01.vevo
        left join holes_aw.torzs on torzs.torzsszam=kereskedelem02.torzsszam
        left join holes_aw_termeles_t.termeles_program on termeles_program.munkaszam=kereskedelem02_munkaszam.munkaszam
        left join (select torzsszam, raktar_pozicio from holes_aw_keszlet.raktarkeszlet_fifo where raktar_pozicio is not null group by torzsszam) as raktarkeszlet_fifo on raktarkeszlet_fifo.torzsszam=kereskedelem02.torzsszam
        left join holes_aw.raktar_pozicio_katalogus01 on raktar_pozicio_katalogus01.kod=raktarkeszlet_fifo.raktar_pozicio
        where year(kereskedelem01.datum)>1999
        ''')
    except:
        messagebox.showerror("Hiba!", "A Benefit adatbázisa nem elérhető jelenleg, feltehetőleg hálózati probléma miatt!")


    azonosito = munkaszam_entry.get()
    azonosito = azonosito.upper()
    for row in cursor:
        if row.munkaszam == azonosito:
            filtered_rows.append(list(row))
    if len(filtered_rows) == 0:
        messagebox.showerror("Hiba!", "Ez a munkaszám nem létezik!")
    cimke = filtered_rows[0]
    vevo_entry.insert(0, cimke[0])
    rajzszam_entry.insert(0, cimke[1])
    megnevezes_entry.insert(0, cimke[6])


def nyomtatas():


    nyelv = nyelv_select.get()
    img = Image.new(mode="RGB", size=(700, 500), color='white')
    font = ImageFont.truetype('C:\\Windows\\Fonts\\Calibrib.ttf', 28)
    font2 = ImageFont.truetype('C:\\Windows\\Fonts\\Calibri.ttf', 28)
    font3 = ImageFont.truetype('C:\\Windows\\Fonts\\Calibrib.ttf', 40)
    draw = ImageDraw.Draw(img)

    if nyelv == "magyar":
        draw.text((235, 50), "KISÉRŐ JEGY", fill='black', font=font3)
        draw.text((30, 120), "CÉG:", fill='black', font=font)
        draw.text((30, 170), "MUNKASZÁM:", fill='black', font=font)
        draw.text((30, 220), "RAJZSZÁM:", fill='black', font=font)
        draw.text((30, 270), "MEGNEVEZÉS:", fill='black', font=font)
        draw.text((30, 320), "MENNYISÉG:", fill='black', font=font)
        draw.text((30, 370), "ELLENŐRIZTE:", fill='black', font=font)
        draw.text((30, 420), "DÁTUM:", fill='black', font=font)

    else:
        draw.text((235, 50), "QUALITY CERTIFICATE", fill='black', font=font3)
        draw.text((30, 120), "COMPANY:", fill='black', font=font)
        draw.text((30, 170), "PRODUCTION:", fill='black', font=font)
        draw.text((30, 220), "DRAWING NO.:", fill='black', font=font)
        draw.text((30, 270), "NAME:", fill='black', font=font)
        draw.text((30, 320), "QUANTITY:", fill='black', font=font)
        draw.text((30, 370), "INSPECTOR:", fill='black', font=font)
        draw.text((30, 420), "DATE:", fill='black', font=font)

    font4 = font2
    text_ceg = vevo_entry.get()
    text_munkaszam = munkaszam_entry.get()
    text_rajzszam = rajzszam_entry.get()
    cegnev_hossz = draw.textlength(text_ceg, font=font4)
    font_size = 28
    while cegnev_hossz > 450:
        font_size = font_size - 1
        font4 = ImageFont.truetype('C:\\Windows\\Fonts\\Calibri.ttf', font_size)
        cegnev_hossz = draw.textlength(text_ceg, font=font4)

    draw.text((235, 120), text_ceg, fill='black', font=font4)
    draw.text((235, 170), text_munkaszam, fill='black', font=font2)
    draw.text((235, 220), text_rajzszam, fill='black', font=font)

    text_megnevezes = megnevezes_entry.get()

    font4 = font2
    megnevezes_hossz = draw.textlength(text_megnevezes, font=font4)
    while megnevezes_hossz > 450:
        font_size = font_size - 1
        font4 = ImageFont.truetype('C:\\Windows\\Fonts\\Calibri.ttf', font_size)
        megnevezes_hossz = draw.textlength(text_megnevezes, font=font4)

    text_mennyiseg = mennyiseg_entry.get()

    draw.text((235, 270), text_megnevezes, fill='black', font=font4)
    draw.text((235, 320), text_mennyiseg, fill='black', font=font2)
    if nyelv == "angol":
        convert_name = ellenorizte_entry.get().split()
        text_ellenorizte = convert_name[1] + " " + convert_name[0]
    else:
        text_ellenorizte = ellenorizte_entry.get()
    draw.text((235, 370), text_ellenorizte, fill='black', font=font2)

    if cimke[3] == None:
        if nyelv == "angol":
            text_datum = date.today().strftime('%d.%m.%Y')
        else:
            date.today().strftime('%Y.%m.%d')
    else:
        if nyelv == "angol":
            text_datum = date.today().strftime('%d.%m.%Y')
        else:
            date_object = cimke[3]
            if nyelv == "angol":
                text_datum = date_object.strftime('%d.%m.%Y')
            else:
                text_datum = date_object.strftime('%Y.%m.%d')

    draw.text((235, 420), text_datum, fill='black', font=font2)

    qr = qrcode.QRCode(box_size=7, border=2)
    qr2 = qrcode.QRCode(box_size=3, border=2)
    qr.add_data(cimke[5])
    qr2.add_data(text_mennyiseg)
    qr.make()
    qr2.make()
    qr_img = qr.make_image()
    qr2_img = qr2.make_image()
    qr_img.save('qr.png')
    qr2_img.save("qr2.png")
    qrimage = Image.open('qr.png')
    qrimage2 = Image.open("qr2.png")
    img_copy = img.copy()
    img_copy.paste(qrimage, (500, 320))
    img_copy.paste(qrimage2, (30, 20))
    zpl_string = ZebrafyImage(img_copy, invert=True, width=600, height=430).to_zpl()

    TCP_IP = '192.168.99.190'
    TCP_PORT = 9100
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    if int(peldanyszam_entry.get()) > 1:
        for i in range(int(peldanyszam_entry.get())):
            s.send(bytes(zpl_string, "utf-8"))
    else:
        s.send(bytes(zpl_string, "utf-8"))

    s.close()

    os.remove("qr.png")
    os.remove("qr2.png")

def vizsgalat():

    answer = ping.zebra_ping()
    if answer == "Request":
        tkinter.messagebox.showwarning(title="Nyomtató", message=("Kapcsolati hiba! Lehetséges okok:\n "
                                                                 " - A nyomtató nem üzemel megfelelően.\n"
                                                                 " - A számítógép nem csatlakozik a hálózatra.\n"
                                                                 " - A helyi hálózaton váratlan probléma lépett fel.\n"
                                                                  "\n"
                                                                  "Lehetséges megoldások:\n"
                                                                  " - Címkenyomtató program újraindítása.\n"
                                                                  " - Nyomtató újraindítása.\n"
                                                                  " - Számítógép újraindítása.\n"))
        return

    if nyelv_select.get() == "":
        tkinter.messagebox.showwarning(title="Nyelv", message="A címke nyelve nem lett kiválasztva!")
        return
    if mennyiseg_entry.get() == "":
        tkinter.messagebox.showwarning(title="Mennyiség", message="Mennyiség nem lett megadva!")
        return
    try:
        type(int(mennyiseg_entry.get()))
    except:
        tkinter.messagebox.showwarning(title="Mennyiség", message="Mennyiség nem megfelelő!")
        return
    if ellenorizte_entry.get() == "":
        tkinter.messagebox.showwarning(title="Ellenőrizte", message="Ellenőrizte mező nics kitöltve!")
        return
    if munkaszam_entry.get() == "":
        tkinter.messagebox.showwarning(title="Munkaszám", message="Munkaszám mező nics kitöltve!")
        return
    if vevo_entry.get() == "":
        tkinter.messagebox.showwarning(title="Vevő", message="Vevő mező nics kitöltve!")
        return

    if rajzszam_entry.get() == "":
        answer = tkinter.messagebox.askokcancel(title="Rajzszám", message="Rajzszám mező nics kitöltve! Folytatja?")
        if answer == False:
            return

    nyomtatas()


def kilepes():
    window.quit()
    window.destroy()



# Gombok frame
gombok_frame = tkinter.LabelFrame(frame)
gombok_frame.grid(row=2, column=0)

# Gombok
adat_betoltes_gomb = tkinter.Button(frame, text="Adat betöltése", font=font, command=adatok_betoltese)
adat_betoltes_gomb.grid(row=2, column=0, sticky="news", padx=5, pady=5)
nyomtatas_gomb = tkinter.Button(frame, text="Nyomtatás", font=font, command=vizsgalat)
nyomtatas_gomb.grid(row=3, column=0, sticky="news", padx=5, pady=5)
kilepes_gomb = tkinter.Button(frame, text="Kilépés", font=font, command=kilepes)
kilepes_gomb.grid(row=4, column=0, sticky="news", padx=5, pady=5)
munkaszam_entry.bind('<Return>', adatok_betoltese)



window.mainloop()

