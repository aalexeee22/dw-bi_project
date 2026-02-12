from flask import Flask, render_template, request, redirect
import oracledb

app = Flask(__name__)

# conectare ORACLE
conn = oracledb.connect(
    user="ADMIN_APLICATIE",
    password="1234",
    dsn="localhost:1521/XEPDB1"
)

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
        int(request.form["id"]),
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["nr"])
    ))

    conn.commit()
    cur.close()

    return redirect("/clienti")

@app.route("/clienti/update/<int:id>", methods=["POST"])
def update_client(id):
    cur = conn.cursor()

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
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["nr"]),
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/clienti")


@app.route("/clienti/delete/<id>")
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

    cur.execute("""
        INSERT INTO LOCATIE
        VALUES (:1,:2,:3,:4,:5)
    """, (
        request.form["id"],
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

@app.route("/locatie/delete/<id>")
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

    data = cur.fetchall()
    cur.close()

    return render_template(
        "angajat.html",
        angajati=data,
        tabel_curent="angajat"
    )
@app.route("/angajat/add", methods=["POST"])
def add_angajat():
    cur = conn.cursor()

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
        int(request.form["id"]),
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["varsta"]),
        request.form["specializare"],
        int(request.form["experienta"]),
        request.form["salariu"],
        request.form["echipa"] if request.form["echipa"] else None
    ))

    conn.commit()
    cur.close()

    return redirect("/angajat")
@app.route("/angajat/update/<int:id>", methods=["POST"])
def update_angajat(id):
    cur = conn.cursor()

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
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["varsta"]),
        request.form["specializare"],
        int(request.form["experienta"]),
        request.form["salariu"],
        request.form["echipa"] if request.form["echipa"] else None,
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/angajat")
@app.route("/angajat/delete/<int:id>")
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
        int(request.form["id"]),
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["varsta"]),
        int(request.form["experienta"]),
        request.form["salariu"]
    ))

    conn.commit()
    cur.close()

    return redirect("/sef")
@app.route("/sef/update/<int:id>", methods=["POST"])
def update_sef(id):
    cur = conn.cursor()

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
        request.form["nume"],
        request.form["prenume"],
        request.form["telefon"],
        int(request.form["varsta"]),
        int(request.form["experienta"]),
        request.form["salariu"],
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/sef")
@app.route("/sef/delete/<int:id>")
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

    cur.execute("""
        INSERT INTO COLABORATORI(
            id_colaborator,
            nume,
            numar_telefon
        )
        VALUES(:1,:2,:3)
    """, (
        int(request.form["id"]),
        request.form["nume"],
        request.form["telefon"]
    ))

    conn.commit()
    cur.close()

    return redirect("/colaboratori")
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

@app.route("/colaboratori/delete/<int:id>")
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

    cur.execute("""
    INSERT INTO SELECTIE_COLABORATORI(
        id_selectie,
        cod_colaborator,
        cod_oferta,
        procent_colaborator
    )
    VALUES(:1,:2,:3,:4)
    """, (
        int(request.form["id"]),
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
@app.route("/selectie_colaboratori/delete/<int:id>")
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

    cur.execute("""
    INSERT INTO ECHIPA(
        id_echipa,
        cod_sef
    )
    VALUES(:1,:2)
    """, (
        int(request.form["id"]),
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
@app.route("/echipa/delete/<int:id>")
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
        int(request.form["id"]),
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
@app.route("/factura/delete/<int:id>")
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

    cur.execute("""
    INSERT INTO LUCRARE(
        id_lucrare,
        nume,
        cod_locatie,
        cod_sef
    )
    VALUES(:1,:2,:3,:4)
    """, (
        int(request.form["id"]),
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
@app.route("/lucrare/delete/<int:id>")
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

    cur.execute("""
        INSERT INTO OFERTA(
            id_oferta,
            pret
        )
        VALUES(:1,:2)
    """, (
        int(request.form["id"]),
        int(request.form["pret"])
    ))

    conn.commit()
    cur.close()

    return redirect("/oferta")
@app.route("/oferta/update/<int:id>", methods=["POST"])
def update_oferta(id):
    cur = conn.cursor()

    cur.execute("""
        UPDATE OFERTA
        SET pret=:1
        WHERE id_oferta=:2
    """, (
        int(request.form["pret"]),
        id
    ))

    conn.commit()
    cur.close()

    return redirect("/oferta")
@app.route("/oferta/delete/<int:id>")
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
@app.route("/programare_utilaje/delete/<int:utilaj>/<int:locatie>")
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

    cur.execute("""
    INSERT INTO RECENZIE(
        id_recenzie,
        cod_client,
        cod_lucrare,
        parere
    )
    VALUES(:1,:2,:3,:4)
    """, (
        int(request.form["id"]),
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
@app.route("/recenzie/delete/<int:id>")
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
@app.route("/utilaj/delete/<int:id>")
def delete_utilaj(id):
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM UTILAJ WHERE id_utilaj=:1",
        [id]
    )

    conn.commit()
    cur.close()

    return redirect("/utilaj")

# RUN
if __name__ == "__main__":
    app.run(debug=True)
