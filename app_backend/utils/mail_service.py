from flask_mail import Message
from utils.extensions import mail

def enviar_mail_bienvenida(destinatario, nombre, contrasenia):
    try:
        msg = Message(
            subject="Registro exitoso",
            recipients=[destinatario]
        )

        msg.body = f"""
Hola {nombre},

Se le ha registrado correctamente en el Campus FIUBA de Introducción al Desarrollo de Software.

Ya puedes iniciar sesión utilizando tu correo electrónico y la contraseña: {contrasenia}

Saludos.
"""

        mail.send(msg)
        return True

    except Exception as e:
        print(f"Error enviando mail: {e}")
        return False