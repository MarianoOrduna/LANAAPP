import smtplib
from email.message import EmailMessage

CORREO_EMISOR = "gabriel.mzn.r.xx66@gmail.com"
CONTRASENA_CORREO = "bhrq dzlm hzuk rcpn"

async def enviar_correo(asunto: str, mensaje: str, destinatario: str):
    correo = EmailMessage()
    correo["From"] = CORREO_EMISOR
    correo["To"] = destinatario
    correo["Subject"] = asunto
    correo.set_content(mensaje)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(CORREO_EMISOR, CONTRASENA_CORREO)
            servidor.send_message(correo)
    except Exception as error:
        print("Error al enviar correo:", error)
