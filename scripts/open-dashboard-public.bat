@echo off
chcp 65001 >nul
echo Проверь: МТ5 должен быть открыт и залогинен.
echo.
echo Запускаю дашборд...
start "Дашборд Yasno.trade (не закрывать)" cmd /k "cd /d C:\Users\mpush\Desktop\yasno-trade\scripts && python serve_dash.py"

timeout /t 3 /nobreak >nul

echo Открываю публичную ссылку...
start "Публичная ссылка (не закрывать)" cmd /k "ssh -R 80:localhost:8765 localhost.run"

echo.
echo Готово. Ссылка появится в новом окне "Публичная ссылка" через несколько секунд
echo - ищи строку вида https://xxxxx.lhr.life
echo.
echo Чтобы выключить публичный доступ - просто закрой оба новых окна.
pause
