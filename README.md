# TelegramManager
Telegram Group Manager helper

Primero debes registrarte en my.telegram.org y obtener una API ID y API Hash
crea un entorno python y agrega la biblioteca de funciones de Telegram: "pip install telethon"

Crea un archivo de texto api_secrets.json con los siguientes contenidos

```
{
    "api_id": "123456",
    "api_hash": "abc123def456gh789ijklmnop",
    "phone": "+1234567890"
}
```

Ajusta los grupos source y target en "t_addusers.py"

ejecuta "python t_addusers.py"
