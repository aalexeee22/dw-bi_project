from flask import Flask, render_template, request, redirect
import oracledb
import os
from dotenv import load_dotenv
from dw import sync_all_dw
app = Flask(__name__)
load_dotenv()
# conectare ORACLE
def get_connection(DB_USER, DB_PASSWORD, DB_DSN):
    return oracledb.connect(
        user=os.getenv(DB_USER),
        password=os.getenv(DB_PASSWORD),
        dsn=os.getenv(DB_DSN)
    )
conn = get_connection("DB_USER","DB_PASSWORD","DB_DSN")
conn_dw   = get_connection("DB_USER_DW","DB_PASSWORD_DW","DB_DSN")
# HOME
@app.route("/")
def index():
    return render_template(
        "index.html",
        tabel_curent=""
    )

# CLIENTI
@app.route("/clienti")
def clienti():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id_client,
        nume,
        prenume,
        ADMIN_APLICATIE.dec_tel(numar_telefon),
        nr_lucrari_anterioare
    FROM CLIENT
    ORDER BY id_client
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "clienti.html",
        clienti=data,
        tabel_curent="clienti"
    )

@app.route("/clienti/add", methods=["POST"])
def add_client():
    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        prenume = request.form["prenume"]
        telefon = request.form["telefon"]
        nr = int(request.form["nr"])

        if not telefon.isdigit():
            return "Telefon invalid"

        if nr < 0:
            return "Nr lucrari trebuie sa fie >= 0"

        cur.execute("SELECT NVL(MAX(id_client),0)+1 FROM CLIENT")
        new_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO CLIENT(
            id_client,
            nume,
            prenume,
            numar_telefon,
            nr_lucrari_anterioare
        )
        VALUES (
            :1,
            :2,
            :3,
            DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:4),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            :5
        )
        """, (
            new_id,
            nume,
            prenume,
            telefon,
            nr
        ))

        conn.commit()
        return redirect("/clienti")

    except:
        return "Date invalide"

    finally:
        cur.close()


@app.route("/clienti/update/<int:id>", methods=["POST"])
def update_client(id):
    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        prenume = request.form["prenume"]
        telefon = request.form["telefon"]
        nr = int(request.form["nr"])

        if not telefon.isdigit():
            return "Telefon invalid"

        if nr < 0:
            return "Nr lucrari trebuie sa fie >= 0"

        cur.execute("""
        UPDATE CLIENT
        SET
            nume = :1,
            prenume = :2,
            numar_telefon = DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:3),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            nr_lucrari_anterioare = :4
        WHERE id_client = :5
        """, (
            nume,
            prenume,
            telefon,
            nr,
            id
        ))

        conn.commit()
        return redirect("/clienti")

    except:
        return "Date invalide"

    finally:
        cur.close()



@app.route("/clienti/delete/<id>", methods=["POST"])
def delete_client(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM CLIENT WHERE id_client=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/clienti")

# LOCATIE
@app.route("/locatie")
def locatie():
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM LOCATIE
        ORDER BY id_locatie
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "locatie.html",
        locatii=data,
        tabel_curent="locatie"
    )

@app.route("/locatie/add", methods=["POST"])
def add_locatie():
    cur = conn.cursor()
    cur.execute("SELECT NVL(MAX(id_locatie),0)+1 FROM LOCATIE")
    new_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO LOCATIE
        VALUES (:1,:2,:3,:4,:5)
    """, (
        new_id,
        request.form["judet"],
        request.form["localitate"],
        request.form["strada"],
        request.form["detalii"]
    ))

    conn.commit()
    cur.close()

    return redirect("/locatie")

@app.route("/locatie/update/<int:id>", methods=["POST"])
def update_locatie(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE LOCATIE
    SET
        judet = :1,
        localitate = :2,
        strada = :3,
        detalii = :4
    WHERE id_locatie = :5
    """, (
        request.form["judet"],
        request.form["localitate"],
        request.form["strada"],
        request.form["detalii"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/locatie")

@app.route("/locatie/delete/<id>",methods=["POST"])
def delete_locatie(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM LOCATIE WHERE id_locatie=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/locatie")

# ANGAJAT
@app.route("/angajat")
def angajat():

    cur = conn.cursor()

    # angajati
    cur.execute("""
    SELECT
        id_angajat,
        nume,
        prenume,
        ADMIN_APLICATIE.dec_tel(numar_telefon),
        varsta,
        specializare,
        experienta,
        ADMIN_APLICATIE.dec_salariu(salariu),
        cod_echipa
    FROM ANGAJAT
    ORDER BY id_angajat
    """)
    angajati = cur.fetchall()

    # ⭐ ECHIPE (asta lipsește)
    cur.execute("""
    SELECT id_echipa
    FROM ECHIPA
    ORDER BY id_echipa
    """)
    echipe = cur.fetchall()

    cur.close()

    return render_template(
        "angajat.html",
        angajati=angajati,
        echipe=echipe,
        tabel_curent="angajat"
    )

@app.route("/angajat/add", methods=["POST"])
def add_angajat():

    cur = conn.cursor()

    try:
        varsta = int(request.form["varsta"])
        experienta = int(request.form["experienta"])
        telefon = request.form["telefon"]
        salariu = int(request.form["salariu"])

        if varsta < 18:
            return "Varsta trebuie sa fie minim 18"



        if salariu <= 0:
            return "Salariul trebuie sa fie mai mare decat 0"

        if experienta < 0:
            return "Experienta nu poate fi negativa"

        if not telefon.isdigit():
            return "Telefon trebuie sa contina doar cifre"

        echipa = request.form["echipa"]

        if echipa:
            cur.execute("""
                SELECT COUNT(*)
                FROM ECHIPA
                WHERE id_echipa=:1
            """, [int(echipa)])

            if cur.fetchone()[0] == 0:
                return "Echipa nu exista"

        cur.execute("SELECT NVL(MAX(id_angajat),0)+1 FROM ANGAJAT")
        new_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO ANGAJAT(
            id_angajat,
            nume,
            prenume,
            numar_telefon,
            varsta,
            specializare,
            experienta,
            salariu,
            cod_echipa
        )
        VALUES(
            :1,
            :2,
            :3,
            DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:4),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            :5,
            :6,
            :7,
            DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:8),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            :9
        )
        """, (
            new_id,
            request.form["nume"],
            request.form["prenume"],
            telefon,
            varsta,
            request.form["specializare"],
            experienta,
            request.form["salariu"],
            int(echipa) if echipa else None
        ))

        conn.commit()
        return redirect("/angajat")

    except Exception as e:
        return f"Eroare: {str(e)}"

    finally:
        cur.close()

@app.route("/angajat/update/<int:id>", methods=["POST"])
def update_angajat(id):

    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        prenume = request.form["prenume"]
        telefon = request.form["telefon"]

        varsta = int(request.form["varsta"])
        experienta = int(request.form["experienta"])
        salariu = int(request.form["salariu"])

        echipa = request.form["echipa"]

        if not telefon.isdigit():
            return "Telefon trebuie sa contina doar cifre"

        if varsta < 18:
            return "Varsta trebuie sa fie minim 18"

        if experienta < 0:
            return "Experienta nu poate fi negativa"

        if salariu <= 0:
            return "Salariul trebuie sa fie mai mare decat 0"

        # ⭐ VALIDARE FK ECHIPA
        if echipa:
            cur.execute("""
                SELECT COUNT(*)
                FROM ECHIPA
                WHERE id_echipa=:1
            """, [int(echipa)])

            if cur.fetchone()[0] == 0:
                return "Echipa nu exista"

        # ⭐ UPDATE REAL
        cur.execute("""
        UPDATE ANGAJAT
        SET
            nume=:1,
            prenume=:2,
            numar_telefon=DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:3),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            varsta=:4,
            specializare=:5,
            experienta=:6,
            salariu=DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:7),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            cod_echipa=:8
        WHERE id_angajat=:9
        """, (
            nume,
            prenume,
            telefon,
            varsta,
            request.form["specializare"],
            experienta,
            salariu,
            int(echipa) if echipa else None,
            id
        ))

        conn.commit()
        return redirect("/angajat")

    except Exception as e:
        return f"Eroare update angajat: {str(e)}"

    finally:
        cur.close()

@app.route("/angajat/delete/<int:id>",methods=["POST"])
def delete_angajat(id):
    cur = conn.cursor()

    cur.execute("DELETE FROM ANGAJAT WHERE id_angajat=:1", [id])

    conn.commit()
    cur.close()

    return redirect("/angajat")
# SEF
@app.route("/sef")
def sef():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id_sef,
        nume,
        prenume,
        ADMIN_APLICATIE.dec_tel(numar_telefon),
        varsta,
        experienta,
        ADMIN_APLICATIE.dec_salariu(salariu)
    FROM SEF
    ORDER BY id_sef
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "sef.html",
        sefi=data,
        tabel_curent="sef"
    )
@app.route("/sef/add", methods=["POST"])
def add_sef():

    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        prenume = request.form["prenume"]
        telefon = request.form["telefon"]

        varsta = int(request.form["varsta"])
        experienta = int(request.form["experienta"])
        salariu = int(request.form["salariu"])

        if not telefon.isdigit():
            return "Telefon invalid"

        if varsta < 18:
            return "Varsta trebuie sa fie minim 18"

        if experienta < 0:
            return "Experienta nu poate fi negativa"

        if salariu <= 0:
            return "Salariul trebuie sa fie mai mare decat 0"

        cur.execute("SELECT NVL(MAX(id_sef),0)+1 FROM SEF")
        new_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO SEF(
            id_sef,
            nume,
            prenume,
            numar_telefon,
            varsta,
            experienta,
            salariu
        )
        VALUES(
            :1,
            :2,
            :3,
            DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:4),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            :5,
            :6,
            DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:7),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            )
        )
        """, (
            new_id,
            nume,
            prenume,
            telefon,
            varsta,
            experienta,
            salariu
        ))

        conn.commit()
        return redirect("/sef")

    except:
        return "Date invalide"

    finally:
        cur.close()

@app.route("/sef/update/<int:id>", methods=["POST"])
def update_sef(id):

    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        prenume = request.form["prenume"]
        telefon = request.form["telefon"]

        varsta = int(request.form["varsta"])
        experienta = int(request.form["experienta"])
        salariu = int(request.form["salariu"])

        if not telefon.isdigit():
            return "Telefon invalid"

        if varsta < 18:
            return "Varsta trebuie sa fie minim 18"

        if experienta < 0:
            return "Experienta nu poate fi negativa"

        if salariu <= 0:
            return "Salariul trebuie sa fie mai mare decat 0"

        cur.execute("""
        UPDATE SEF
        SET
            nume=:1,
            prenume=:2,
            numar_telefon=DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:3),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            ),
            varsta=:4,
            experienta=:5,
            salariu=DBMS_CRYPTO.ENCRYPT(
                UTL_RAW.CAST_TO_RAW(:6),
                4353,
                UTL_RAW.CAST_TO_RAW('cheie_secreta_1234')
            )
        WHERE id_sef=:7
        """, (
            nume,
            prenume,
            telefon,
            varsta,
            experienta,
            salariu,
            id
        ))

        conn.commit()
        return redirect("/sef")

    except:
        return "Date invalide"

    finally:
        cur.close()

@app.route("/sef/delete/<int:id>", methods=["POST"])
def delete_sef(id):
    cur = conn.cursor()

    cur.execute("DELETE FROM SEF WHERE id_sef=:1", [id])

    conn.commit()
    cur.close()

    return redirect("/sef")
# COLABORATORI
@app.route("/colaboratori")
def colaboratori():
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id_colaborator,
            nume,
            numar_telefon
        FROM COLABORATORI
        ORDER BY id_colaborator
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "colaboratori.html",
        colaboratori=data,
        tabel_curent="colaboratori"
    )
@app.route("/colaboratori/add", methods=["POST"])
def add_colaborator():
    cur = conn.cursor()

    try:
        nume = request.form["nume"]
        telefon = request.form["telefon"]

        if not telefon.isdigit():
            return "Telefon invalid"

        cur.execute("SELECT NVL(MAX(id_colaborator),0)+1 FROM COLABORATORI")
        new_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO COLABORATORI(
            id_colaborator,
            nume,
            numar_telefon
        )
        VALUES(:1,:2,:3)
        """, (
            new_id,
            nume,
            telefon
        ))

        conn.commit()
        return redirect("/colaboratori")

    except:
        return "Date invalide"

    finally:
        cur.close()

@app.route("/colaboratori/update/<int:id>", methods=["POST"])
def update_colaborator(id):
    cur = conn.cursor()

    cur.execute("""
        UPDATE COLABORATORI
        SET
            nume=:1,
            numar_telefon=:2
        WHERE id_colaborator=:3
    """, (
        request.form["nume"],
        request.form["telefon"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/colaboratori")

@app.route("/colaboratori/delete/<int:id>",methods=["POST"])
def delete_colaborator(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM COLABORATORI WHERE id_colaborator=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/colaboratori")

# SELECTIE_COLABORATORI
@app.route("/selectie_colaboratori")
def selectie_colaboratori():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        sc.id_selectie,
        sc.cod_colaborator,
        c.nume,
        sc.cod_oferta,
        o.pret,
        sc.procent_colaborator
    FROM SELECTIE_COLABORATORI sc
    JOIN COLABORATORI c ON sc.cod_colaborator = c.id_colaborator
    JOIN OFERTA o ON sc.cod_oferta = o.id_oferta
    ORDER BY sc.id_selectie
    """)

    data = cur.fetchall()

    cur.execute("SELECT id_colaborator, nume FROM COLABORATORI")
    colaboratori = cur.fetchall()

    cur.execute("SELECT id_oferta, pret FROM OFERTA")
    oferte = cur.fetchall()

    cur.close()

    return render_template(
        "selectie_colaboratori.html",
        selectii=data,
        colaboratori=colaboratori,
        oferte=oferte,
        tabel_curent="selectie_colaboratori"
    )
@app.route("/selectie_colaboratori/add", methods=["POST"])
def add_selectie():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_selectie),0)+1 FROM SELECTIE_COLABORATORI")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO SELECTIE_COLABORATORI(
        id_selectie,
        cod_colaborator,
        cod_oferta,
        procent_colaborator
    )
    VALUES(:1,:2,:3,:4)
    """, (
        new_id,
        int(request.form["colaborator"]),
        int(request.form["oferta"]),
        int(request.form["procent"])
    ))

    conn.commit()
    cur.close()

    return redirect("/selectie_colaboratori")
@app.route("/selectie_colaboratori/update/<int:id>", methods=["POST"])
def update_selectie(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE SELECTIE_COLABORATORI
    SET
        cod_colaborator=:1,
        cod_oferta=:2,
        procent_colaborator=:3
    WHERE id_selectie=:4
    """, (
        int(request.form["colaborator"]),
        int(request.form["oferta"]),
        int(request.form["procent"]),
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/selectie_colaboratori")
@app.route("/selectie_colaboratori/delete/<int:id>",methods=["POST"])
def delete_selectie(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM SELECTIE_COLABORATORI WHERE id_selectie=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/selectie_colaboratori")

# ECHIPA
@app.route("/echipa")
def echipa():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        e.id_echipa,
        e.cod_sef,
        s.nume,
        s.prenume
    FROM ECHIPA e
    JOIN SEF s ON e.cod_sef = s.id_sef
    ORDER BY e.id_echipa
    """)

    data = cur.fetchall()

    cur.execute("SELECT id_sef, nume, prenume FROM SEF")
    sefi = cur.fetchall()

    cur.close()

    return render_template(
        "echipa.html",
        echipe=data,
        sefi=sefi,
        tabel_curent="echipa"
    )
@app.route("/echipa/add", methods=["POST"])
def add_echipa():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_echipa),0)+1 FROM ECHIPA")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO ECHIPA(
        id_echipa,
        cod_sef
    )
    VALUES(:1,:2)
    """, (
        new_id,
        int(request.form["sef"])
    ))

    conn.commit()
    cur.close()

    return redirect("/echipa")
@app.route("/echipa/update/<int:id>", methods=["POST"])
def update_echipa(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE ECHIPA
    SET cod_sef=:1
    WHERE id_echipa=:2
    """, (
        int(request.form["sef"]),
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/echipa")
@app.route("/echipa/delete/<int:id>",methods=["POST"])
def delete_echipa(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM ECHIPA WHERE id_echipa=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/echipa")

# FACTURA
@app.route("/factura")
def factura():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        f.id_factura,
        f.cod_oferta_acceptata,
        o.pret,
        f.cod_client,
        c.nume,
        c.prenume,
        f.cod_lucrare,
        l.nume,
        f.data_facturare
    FROM FACTURA f
    LEFT JOIN OFERTA o ON f.cod_oferta_acceptata = o.id_oferta
    LEFT JOIN CLIENT c ON f.cod_client = c.id_client
    JOIN LUCRARE l ON f.cod_lucrare = l.id_lucrare
    ORDER BY f.id_factura
    """)

    facturi = cur.fetchall()

    cur.execute("SELECT id_oferta, pret FROM OFERTA")
    oferte = cur.fetchall()

    cur.execute("SELECT id_client, nume, prenume FROM CLIENT")
    clienti = cur.fetchall()

    cur.execute("SELECT id_lucrare, nume FROM LUCRARE")
    lucrari = cur.fetchall()

    cur.close()

    return render_template(
        "factura.html",
        facturi=facturi,
        oferte=oferte,
        clienti=clienti,
        lucrari=lucrari,
        tabel_curent="factura"
    )
@app.route("/factura/add", methods=["POST"])
def add_factura():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_factura),0)+1 FROM FACTURA")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO FACTURA(
        id_factura,
        cod_oferta_acceptata,
        cod_client,
        cod_lucrare,
        data_facturare
    )
    VALUES(:1,:2,:3,:4,TO_DATE(:5,'YYYY-MM-DD'))
    """, (
        new_id,
        request.form["oferta"] if request.form["oferta"] else None,
        request.form["client"] if request.form["client"] else None,
        int(request.form["lucrare"]),
        request.form["data"]
    ))

    conn.commit()
    cur.close()

    return redirect("/factura")
@app.route("/factura/update/<int:id>", methods=["POST"])
def update_factura(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE FACTURA
    SET
        cod_oferta_acceptata=:1,
        cod_client=:2,
        cod_lucrare=:3,
        data_facturare=TO_DATE(:4,'YYYY-MM-DD')
    WHERE id_factura=:5
    """, (
        request.form["oferta"] if request.form["oferta"] else None,
        request.form["client"] if request.form["client"] else None,
        int(request.form["lucrare"]),
        request.form["data"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/factura")
@app.route("/factura/delete/<int:id>",methods=["POST"])
def delete_factura(id):
    cur = conn.cursor()

    cur.execute("DELETE FROM FACTURA WHERE id_factura=:1", [id])

    conn.commit()
    cur.close()

    return redirect("/factura")

# LUCRARE
@app.route("/lucrare")
def lucrare():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        l.id_lucrare,
        l.nume,
        l.cod_locatie,
        loc.judet,
        loc.localitate,
        l.cod_sef,
        s.nume,
        s.prenume
    FROM LUCRARE l
    JOIN LOCATIE loc ON l.cod_locatie = loc.id_locatie
    JOIN SEF s ON l.cod_sef = s.id_sef
    ORDER BY l.id_lucrare
    """)

    lucrari = cur.fetchall()

    cur.execute("""
    SELECT id_locatie, judet, localitate
    FROM LOCATIE
    """)
    locatii = cur.fetchall()

    cur.execute("""
    SELECT id_sef, nume, prenume
    FROM SEF
    """)
    sefi = cur.fetchall()

    cur.close()

    return render_template(
        "lucrare.html",
        lucrari=lucrari,
        locatii=locatii,
        sefi=sefi,
        tabel_curent="lucrare"
    )
@app.route("/lucrare/add", methods=["POST"])
def add_lucrare():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_lucrare),0)+1 FROM LUCRARE")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO LUCRARE(
        id_lucrare,
        nume,
        cod_locatie,
        cod_sef
    )
    VALUES(:1,:2,:3,:4)
    """, (
        new_id,
        request.form["nume"],
        int(request.form["locatie"]),
        int(request.form["sef"])
    ))

    conn.commit()
    cur.close()

    return redirect("/lucrare")
@app.route("/lucrare/update/<int:id>", methods=["POST"])
def update_lucrare(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE LUCRARE
    SET
        nume=:1,
        cod_locatie=:2,
        cod_sef=:3
    WHERE id_lucrare=:4
    """, (
        request.form["nume"],
        int(request.form["locatie"]),
        int(request.form["sef"]),
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/lucrare")
@app.route("/lucrare/delete/<int:id>",methods=["POST"])
def delete_lucrare(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM LUCRARE WHERE id_lucrare=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/lucrare")

# OFERTA
@app.route("/oferta")
def oferta():
    cur = conn.cursor()

    cur.execute("""
        SELECT id_oferta, pret
        FROM OFERTA
        ORDER BY id_oferta
    """)

    oferte = cur.fetchall()
    cur.close()

    return render_template(
        "oferta.html",
        oferte=oferte,
        tabel_curent="oferta"
    )
@app.route("/oferta/add", methods=["POST"])
def add_oferta():
    cur = conn.cursor()

    try:
        pret = int(request.form["pret"])

        if pret <= 0:
            return "Pretul trebuie sa fie mai mare decat 0"

        cur.execute("SELECT NVL(MAX(id_oferta),0)+1 FROM OFERTA")
        new_id = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO OFERTA(
            id_oferta,
            pret
        )
        VALUES(:1,:2)
        """, (
            new_id,
            pret
        ))

        conn.commit()
        return redirect("/oferta")

    except:
        return "Date invalide"

    finally:
        cur.close()

@app.route("/oferta/update/<int:id>", methods=["POST"])
def update_oferta(id):
    cur = conn.cursor()

    try:
        pret = int(request.form["pret"])

        if pret <= 0:
            return "Pretul trebuie sa fie mai mare decat 0"

        cur.execute("""
        UPDATE OFERTA
        SET pret=:1
        WHERE id_oferta=:2
        """, (
            pret,
            id
        ))

        conn.commit()
        return redirect("/oferta")

    except:
        return "Date invalide"

    finally:
        cur.close()

@app.route("/oferta/delete/<int:id>",methods=["POST"])
def delete_oferta(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM OFERTA WHERE id_oferta=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/oferta")

# PROGRAMARE_UTILAJE
@app.route("/programare_utilaje")
def programare_utilaje():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        p.cod_utilaj,
        u.nume,
        p.cod_locatie,
        l.judet,
        l.localitate,
        p.data_inceput,
        p.data_terminare
    FROM PROGRAMARE_UTILAJE p
    JOIN UTILAJ u ON p.cod_utilaj = u.id_utilaj
    JOIN LOCATIE l ON p.cod_locatie = l.id_locatie
    ORDER BY p.cod_utilaj, p.cod_locatie
    """)

    programari = cur.fetchall()

    cur.execute("SELECT id_utilaj, nume FROM UTILAJ")
    utilaje = cur.fetchall()

    cur.execute("SELECT id_locatie, judet, localitate FROM LOCATIE")
    locatii = cur.fetchall()

    cur.close()

    return render_template(
        "programare_utilaje.html",
        programari=programari,
        utilaje=utilaje,
        locatii=locatii,
        tabel_curent="programare_utilaje"
    )
@app.route("/programare_utilaje/add", methods=["POST"])
def add_programare():
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO PROGRAMARE_UTILAJE(
        cod_utilaj,
        cod_locatie,
        data_inceput,
        data_terminare
    )
    VALUES(:1,:2,TO_DATE(:3,'YYYY-MM-DD'),TO_DATE(:4,'YYYY-MM-DD'))
    """, (
        int(request.form["utilaj"]),
        int(request.form["locatie"]),
        request.form["data_start"],
        request.form["data_end"]
    ))

    conn.commit()
    cur.close()

    return redirect("/programare_utilaje")
@app.route("/programare_utilaje/update/<int:utilaj>/<int:locatie>", methods=["POST"])
def update_programare(utilaj, locatie):
    cur = conn.cursor()

    cur.execute("""
    UPDATE PROGRAMARE_UTILAJE
    SET
        data_inceput = TO_DATE(:1,'YYYY-MM-DD'),
        data_terminare = TO_DATE(:2,'YYYY-MM-DD')
    WHERE cod_utilaj = :3
    AND cod_locatie = :4
    """, (
        request.form["data_start"],
        request.form["data_end"],
        utilaj,
        locatie
    ))

    conn.commit()
    cur.close()

    return redirect("/programare_utilaje")
@app.route("/programare_utilaje/delete/<int:utilaj>/<int:locatie>", methods=["POST"])
def delete_programare(utilaj, locatie):
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM PROGRAMARE_UTILAJE
    WHERE cod_utilaj=:1 AND cod_locatie=:2
    """, (utilaj, locatie))

    conn.commit()
    cur.close()

    return redirect("/programare_utilaje")

# RECENZIE
@app.route("/recenzie")
def recenzie():
    cur = conn.cursor()

    cur.execute("""
    SELECT
        r.id_recenzie,
        r.cod_client,
        c.nume,
        c.prenume,
        r.cod_lucrare,
        l.nume,
        r.parere
    FROM RECENZIE r
    JOIN CLIENT c ON r.cod_client = c.id_client
    JOIN LUCRARE l ON r.cod_lucrare = l.id_lucrare
    ORDER BY r.id_recenzie
    """)

    recenzii = cur.fetchall()

    cur.execute("SELECT id_client, nume, prenume FROM CLIENT")
    clienti = cur.fetchall()

    cur.execute("SELECT id_lucrare, nume FROM LUCRARE")
    lucrari = cur.fetchall()

    cur.close()

    return render_template(
        "recenzie.html",
        recenzii=recenzii,
        clienti=clienti,
        lucrari=lucrari,
        tabel_curent="recenzie"
    )
@app.route("/recenzie/add", methods=["POST"])
def add_recenzie():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_recenzie),0)+1 FROM RECENZIE")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO RECENZIE(
        id_recenzie,
        cod_client,
        cod_lucrare,
        parere
    )
    VALUES(:1,:2,:3,:4)
    """, (
        new_id,
        int(request.form["client"]),
        int(request.form["lucrare"]),
        request.form["parere"]
    ))

    conn.commit()
    cur.close()

    return redirect("/recenzie")
@app.route("/recenzie/update/<int:id>", methods=["POST"])
def update_recenzie(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE RECENZIE
    SET
        cod_client=:1,
        cod_lucrare=:2,
        parere=:3
    WHERE id_recenzie=:4
    """, (
        int(request.form["client"]),
        int(request.form["lucrare"]),
        request.form["parere"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/recenzie")
@app.route("/recenzie/delete/<int:id>",methods=["POST"])
def delete_recenzie(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM RECENZIE WHERE id_recenzie=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/recenzie")

# UTILAJ
@app.route("/utilaj")
def utilaj():
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id_utilaj,
            nume,
            an_fabricatie
        FROM UTILAJ
        ORDER BY id_utilaj
    """)

    utilaje = cur.fetchall()
    cur.close()

    return render_template(
        "utilaj.html",
        utilaje=utilaje,
        tabel_curent="utilaj"
    )
@app.route("/utilaj/add", methods=["POST"])
def add_utilaj():
    cur = conn.cursor()

    cur.execute("SELECT NVL(MAX(id_utilaj),0)+1 FROM UTILAJ")
    new_id = cur.fetchone()[0]

    cur.execute("""
    INSERT INTO UTILAJ(
        id_utilaj,
        nume,
        an_fabricatie
    )
    VALUES(:1,:2,TO_DATE(:3,'YYYY-MM-DD'))
    """, (
        int(request.form["id"]),
        request.form["nume"],
        request.form["an"]
    ))

    conn.commit()
    cur.close()

    return redirect("/utilaj")
@app.route("/utilaj/update/<int:id>", methods=["POST"])
def update_utilaj(id):
    cur = conn.cursor()

    cur.execute("""
    UPDATE UTILAJ
    SET
        nume=:1,
        an_fabricatie=TO_DATE(:2,'YYYY-MM-DD')
    WHERE id_utilaj=:3
    """, (
        request.form["nume"],
        request.form["an"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/utilaj")
@app.route("/utilaj/delete/<int:id>",methods=["POST"])
def delete_utilaj(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM UTILAJ WHERE id_utilaj=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/utilaj")

@app.route("/dw/load/client", methods=["POST"])
def dw_load_client():

    cur = conn_dw.cursor()

    cur.execute("""
    MERGE INTO client d
    USING (
        SELECT
            id_client,
            nume || ' ' || prenume nume_client,
            nr_lucrari_anterioare
        FROM admin_aplicatie.client
    ) s
    ON (d.id_client = s.id_client)

    WHEN MATCHED THEN UPDATE SET
        d.nume_client = s.nume_client,
        d.nr_lucrari_anterioare = s.nr_lucrari_anterioare

    WHEN NOT MATCHED THEN INSERT (
        id_client,
        nume_client,
        nr_lucrari_anterioare
    )
    VALUES (
        s.id_client,
        s.nume_client,
        s.nr_lucrari_anterioare
    )
    """)

    conn_dw.commit()
    cur.close()

    return "DW CLIENT SYNC OK"

from flask import jsonify
# sincronizare DW
@app.route("/dw/sync_all", methods=["POST"])
def sync_dw():
    try:
        sync_all_dw(conn_dw)
        return jsonify({"status": "ok", "message": "Sincronizare DW realizata"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# CLIENT DW
@app.route("/dw/client")
def dw_client():

    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM client
        ORDER BY id_client
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "client_dw.html",
        data=data
    )
# VANZARI DW
@app.route("/dw/vanzari")
def dw_vanzari():

    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM vanzari
        ORDER BY id_factura
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "vanzari_dw.html",
        data=data
    )
# TIMP DW
@app.route("/dw/timp")
def dw_timp():
    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM timp
        ORDER BY id_timp
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "timp_dw.html",
        timp=data,
        tabel_curent="dw_timp"
    )
# LUCRARE DW
@app.route("/dw/lucrare")
def dw_lucrare():
    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM lucrare
        ORDER BY id_lucrare
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "lucrare_dw.html",
        lucrari=data,
        tabel_curent="dw_lucrare"
    )
# LOCATIE DW
@app.route("/dw/locatie")
def dw_locatie():
    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM locatie
        ORDER BY id_locatie
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "locatie_dw.html",
        locatii=data,
        tabel_curent="dw_locatie"
    )
# ECHIPA DW
@app.route("/dw/echipa")
def dw_echipa():
    cur = conn_dw.cursor()

    cur.execute("""
        SELECT *
        FROM echipa
        ORDER BY id_echipa
    """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        "echipa_dw.html",
        echipe=data,
        tabel_curent="dw_echipa"
    )

# RUN
if __name__ == "__main__":
    app.run(debug=True)
