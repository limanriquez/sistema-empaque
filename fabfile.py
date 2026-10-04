from fabric import Connection


# ============================================================
# CONFIGURACIÓN
# ============================================================

HOST = "3.20.106.73"
USER = "ubuntu"

# Llave AWS ubicada junto a este fabfile.py
KEY_FILE = "llaveAwsAuditoria.pem"

# Proyecto Django en AWS
REMOTE = "/var/www/auditoria/src"

# Python del entorno virtual de producción
VENV_PYTHON = "/var/www/auditoria/entornoVirtual/bin/python"


# ============================================================
# CONEXIÓN
# ============================================================

def connection():
    return Connection(
        host=HOST,
        user=USER,
        connect_kwargs={
            "key_filename": KEY_FILE,
        },
    )


# ============================================================
# DEPLOY
# ============================================================

def deploy():
    c = connection()

    try:

        print("\n")
        print("========================================")
        print("          DEPLOY AUDITORIA")
        print("========================================")
        print(f"Servidor : {HOST}")
        print(f"Proyecto : {REMOTE}")
        print("========================================\n")

        # ----------------------------------------------------
        # 1. ACTUALIZAR CÓDIGO
        # ----------------------------------------------------

        print("1. Actualizando código desde Git...")

        c.run(
            f"cd {REMOTE} && "
            f"git pull --ff-only origin main"
        )

        # ----------------------------------------------------
        # 2. ACTUALIZAR DEPENDENCIAS
        # ----------------------------------------------------

        print("\n2. Actualizando dependencias Python...")

        c.run(
            f"cd {REMOTE} && "
            f"{VENV_PYTHON} -m pip install -r requirements.txt"
        )

        # ----------------------------------------------------
        # 3. VALIDAR DJANGO
        # ----------------------------------------------------

        print("\n3. Validando Django...")

        c.run(
            f"cd {REMOTE} && "
            f"{VENV_PYTHON} manage.py check"
        )

        # ----------------------------------------------------
        # 4. MIGRACIONES
        # ----------------------------------------------------

        print("\n4. Aplicando migraciones...")

        c.run(
            f"cd {REMOTE} && "
            f"{VENV_PYTHON} manage.py migrate --noinput"
        )

        # ----------------------------------------------------
        # 5. ARCHIVOS ESTÁTICOS
        # ----------------------------------------------------

        print("\n5. Actualizando archivos estáticos...")

        c.run(
            f"cd {REMOTE} && "
            f"{VENV_PYTHON} manage.py collectstatic --noinput"
        )

        # ----------------------------------------------------
        # 6. VALIDAR NGINX
        # ----------------------------------------------------

        print("\n6. Validando configuración de Nginx...")

        c.run("sudo nginx -t")

        # ----------------------------------------------------
        # 7. REINICIAR GUNICORN
        # ----------------------------------------------------

        print("\n7. Reiniciando Gunicorn...")

        c.run(
            "sudo systemctl restart gunicorn.service"
        )

        # ----------------------------------------------------
        # 8. RECARGAR NGINX
        # ----------------------------------------------------

        print("\n8. Recargando Nginx...")

        c.run(
            "sudo systemctl reload nginx"
        )

        # ----------------------------------------------------
        # 9. VERIFICAR GUNICORN
        # ----------------------------------------------------

        print("\n9. Verificando Gunicorn...")

        c.run(
            "sudo systemctl is-active gunicorn.service"
        )

        # ----------------------------------------------------
        # 10. MOSTRAR COMMIT DESPLEGADO
        # ----------------------------------------------------

        print("\n10. Commit desplegado:")

        c.run(
            f"cd {REMOTE} && "
            f"git log -1 --oneline"
        )

        # ----------------------------------------------------
        # FIN
        # ----------------------------------------------------

        print("\n")
        print("========================================")
        print("     DEPLOY TERMINADO CORRECTAMENTE")
        print("========================================")
        print("\n")

    except Exception:

        print("\n")
        print("========================================")
        print("          ERROR EN EL DEPLOY")
        print("========================================")
        print("El proceso se detuvo.")
        print("========================================")
        print("\n")

        raise

    finally:
        c.close()
