# TelegramManager
Telegram Group Manager helper

- Primero debes registrarte en my.telegram.org y obtener una API ID y API Hash. 
- Luego crea un entorno Python y agrega la biblioteca de funciones de Telegram: "pip install telethon"
- Crea un archivo de texto api_secrets.json con los siguientes contenidos

```
{
    "api_id": "123456",
    "api_hash": "abc123def456gh789ijklmnop",
    "phone": "+1234567890"
}
```

- Ejecuta "python t_connector.py" y anota los Group IDs de los grupos de origen y destino
- Ajusta los grupos source y target en "t_addusers.py"
- Ejecuta "python t_addusers.py"
