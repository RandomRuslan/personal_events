import logging
import smtplib
from typing import List, NoReturn


from constants import MAIL_USER, MAIL_PWD
from pe_utils import convert_ts_to_date, Repeater


class Mailer:

    def __init__(self, db_conn):
        self.db_conn = db_conn
        Repeater(60, self.check_notification_need).start()

    def check_notification_need(self) -> NoReturn:
        if not all([MAIL_USER, MAIL_PWD]):
            logging.info('You need to define MAIL_USER and MAIL_PWD for mailing')
            return

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        try:
            smtp.login(MAIL_USER, MAIL_PWD)
        except smtplib.SMTPAuthenticationError as e:
            logging.error(e)
            smtp.quit()
            return

        events = self.db_conn.load_events_for_mailing()
        if events:
            self.send_mails(smtp, events)

        smtp.quit()
            
    def send_mails(self, smtp: smtplib.SMTP, events: List) -> NoReturn:
        for event in events:
            if self.send_mail(smtp, event):
                event['notified'] = True

        for event in events:
            if event.get('notified'):
                try:
                    self.db_conn.edit_event(event['cardId'], {'notified': True})
                except Exception as e:
                    logging.exception(e)

    @staticmethod
    def send_mail(smtp: smtplib.SMTP, event: dict) -> bool:
        ts = int(event['ts'])
        tz = int(event['tz'])
        date = ' '.join(convert_ts_to_date(ts, tz))
        date += f' (GMT {"+" if tz > 0 else ""}{tz}:00)'

        text = f'Hello!\n'
        text += f'Event: "{event["title"]}"\n'
        text += f'Time: {date}\n\n'
        text += event['note']

        try:
            smtp.sendmail(MAIL_USER, event['email'], text.encode('utf-8'))
        except Exception as e:
            logging.exception(e)
            return False

        logging.info(f'Message {event["title"]} is sent to {event["email"]}. Card id: {event["cardId"]}')
        return True
