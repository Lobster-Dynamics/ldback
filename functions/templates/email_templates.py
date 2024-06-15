SHARE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document/Directory Shared</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            width: 90%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #AC73D9;
            color: white;
            padding: 10px;
            text-align: center;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        .content {{
            padding: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }}
        .button {{
            background-color: #AC73D9;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: #8a5cb6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{subject}</h2>
        </div>
        <div class="content">
            <p>Hola {recipient_name},</p>
            <p>{sharer_name} te ha compartido un {shared_item_type}.</p>
            <a href="{link}" class="button">Ver {shared_item_type}</a>
            <p>Gracias,</p>
            <p>Tu equipo de FridaRPE</p>
        </div>
        <div class="footer">
            <p>Este es un mensaje automatizado, por favor no responda.</p>
        </div>
    </div>
</body>
</html>
"""
