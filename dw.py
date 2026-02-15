def sync_timp_dw(cur_dw):

    cur_dw.execute("""
        DECLARE
            v_min DATE;
            v_max DATE;
        BEGIN
            SELECT MIN(data_facturare),
                   MAX(data_facturare)
            INTO v_min, v_max
            FROM ADMIN_APLICATIE.factura;

            generare_timp_upsert(v_min, v_max);
        END;
    """)
def sync_client_dw(cur_dw):

    cur_dw.execute("""
    MERGE INTO client d
    USING (
        SELECT
            id_client,
            nume || ' ' || prenume nume_client,
            nr_lucrari_anterioare
        FROM ADMIN_APLICATIE.client
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

    cur_dw.execute("""
    DELETE FROM client d
    WHERE NOT EXISTS (
        SELECT 1
        FROM ADMIN_APLICATIE.client s
        WHERE s.id_client = d.id_client
    )
    """)
def sync_locatie_dw(cur_dw):

    cur_dw.execute("""
    MERGE INTO locatie d
    USING (
        SELECT id_locatie, judet, localitate
        FROM ADMIN_APLICATIE.locatie
    ) s
    ON (d.id_locatie = s.id_locatie)

    WHEN MATCHED THEN UPDATE SET
        d.judet = s.judet,
        d.localitate = s.localitate

    WHEN NOT MATCHED THEN INSERT (
        id_locatie,
        judet,
        localitate
    )
    VALUES (
        s.id_locatie,
        s.judet,
        s.localitate
    )
    """)

    cur_dw.execute("""
    DELETE FROM locatie d
    WHERE NOT EXISTS (
        SELECT 1
        FROM ADMIN_APLICATIE.locatie s
        WHERE s.id_locatie = d.id_locatie
    )
    """)
def sync_lucrare_dw(cur_dw):

    cur_dw.execute("""
    MERGE INTO lucrare d
    USING (
        SELECT id_lucrare, nume nume_lucrare
        FROM ADMIN_APLICATIE.lucrare
    ) s
    ON (d.id_lucrare = s.id_lucrare)

    WHEN MATCHED THEN UPDATE SET
        d.nume_lucrare = s.nume_lucrare

    WHEN NOT MATCHED THEN INSERT (
        id_lucrare,
        nume_lucrare
    )
    VALUES (
        s.id_lucrare,
        s.nume_lucrare
    )
    """)

    cur_dw.execute("""
    DELETE FROM lucrare d
    WHERE NOT EXISTS (
        SELECT 1
        FROM ADMIN_APLICATIE.lucrare s
        WHERE s.id_lucrare = d.id_lucrare
    )
    """)
def sync_echipa_dw(cur_dw):

    cur_dw.execute("""
    MERGE INTO echipa d
    USING (
        SELECT
            e.id_echipa,
            s.nume || ' ' || s.prenume nume_sef,
            COUNT(a.id_angajat) nr_angajati
        FROM ADMIN_APLICATIE.echipa e
        JOIN ADMIN_APLICATIE.sef s ON s.id_sef = e.cod_sef
        LEFT JOIN ADMIN_APLICATIE.angajat a ON a.cod_echipa = e.id_echipa
        GROUP BY e.id_echipa, s.nume, s.prenume
    ) s
    ON (d.id_echipa = s.id_echipa)

    WHEN MATCHED THEN UPDATE SET
        d.nume_sef = s.nume_sef,
        d.nr_angajati = s.nr_angajati

    WHEN NOT MATCHED THEN INSERT (
        id_echipa,
        nume_sef,
        nr_angajati
    )
    VALUES (
        s.id_echipa,
        s.nume_sef,
        s.nr_angajati
    )
    """)

    cur_dw.execute("""
    DELETE FROM echipa d
    WHERE NOT EXISTS (
        SELECT 1
        FROM ADMIN_APLICATIE.echipa s
        WHERE s.id_echipa = d.id_echipa
    )
    """)
def sync_vanzari_dw(cur_dw):

    cur_dw.execute("""
    MERGE INTO vanzari d
    USING (
        SELECT
            f.id_factura,
            f.data_facturare,
            f.cod_client,
            f.cod_lucrare,
            l.cod_locatie,
            e.id_echipa,
            o.pret
        FROM ADMIN_APLICATIE.factura f
        JOIN ADMIN_APLICATIE.lucrare l
            ON f.cod_lucrare = l.id_lucrare
        JOIN ADMIN_APLICATIE.echipa e
            ON l.cod_sef = e.cod_sef
        JOIN ADMIN_APLICATIE.oferta o
            ON f.cod_oferta_acceptata = o.id_oferta
    ) s
    ON (d.id_factura = s.id_factura)

    WHEN MATCHED THEN UPDATE SET
        d.id_timp = s.data_facturare,
        d.id_client = s.cod_client,
        d.id_lucrare = s.cod_lucrare,
        d.id_locatie = s.cod_locatie,
        d.id_echipa = s.id_echipa,
        d.valoare_vanzare = s.pret

    WHEN NOT MATCHED THEN INSERT (
        id_factura,
        id_timp,
        id_client,
        id_lucrare,
        id_locatie,
        id_echipa,
        valoare_vanzare
    )
    VALUES (
        s.id_factura,
        s.data_facturare,
        s.cod_client,
        s.cod_lucrare,
        s.cod_locatie,
        s.id_echipa,
        s.pret
    )
    """)

    cur_dw.execute("""
    DELETE FROM vanzari d
    WHERE NOT EXISTS (
        SELECT 1
        FROM ADMIN_APLICATIE.factura s
        WHERE s.id_factura = d.id_factura
    )
    """)
def sync_all_dw(conn_dw):

    cur_dw = conn_dw.cursor()

    try:
        sync_timp_dw(cur_dw)
        sync_client_dw(cur_dw)
        sync_locatie_dw(cur_dw)
        sync_lucrare_dw(cur_dw)
        sync_echipa_dw(cur_dw)
        sync_vanzari_dw(cur_dw)

        conn_dw.commit()

    except Exception as e:
        conn_dw.rollback()
        raise e

    finally:
        cur_dw.close()
