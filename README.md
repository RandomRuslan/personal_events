# Personal events
Сервис для создания списка событий с почтовыми напоминаниями  

## Установка
1. Скачайте репозиторий

2. В файле `flask/source/constants.py` заполните данные электронной почты, с которой будут отправляться напоминания. Примечание: поддерживается только gmail:
    ```
    MAIL_USER - адрес 
    MAIL_PWD - пароль
    ```
  
3. Настройте указанную google-почту: разрешите небезопасным приложениям доступ к аккаунту 😏: https://myaccount.google.com/lesssecureapps?pli=1

4. В директории с файлом `docker-compose.yml` запустите команду:
    ```
    $ [sudo] docker-compose up --build
    ```
5. Откройте в браузере `http://127.0.0.1:5000/`
