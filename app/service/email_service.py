from fastapi_mail import FastMail, MessageSchema, MessageType
from app.mail import conf

fastmail = FastMail(conf)

async def send_password_reset_email(email: str, token: str):
    # This URL points to your Frontend (React/Angular/Next.js)
    reset_url = f"https://your-frontend.com{token}"
    
    html = f"""
    <html>
        <body>
            <h1>Reset Your Password</h1>
            <p>We received a request to reset your password. Click the link below to proceed:</p>
            <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Reset Password
            </a>
            <p>If you didn't request this, you can safely ignore this email.</p>
            <p>This link will expire in 15 minutes.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fastmail.send_message(message)