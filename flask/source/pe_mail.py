import logging
import smtplib


from constants import MAIL_USER, MAIL_PWD
from pe_utils import convert_ts_to_date, Repeater


class Mailer:

    def __init__(self, db_conn):
        self.db_conn = db_conn
        Repeater(60, self.check_notification_need).start()

    def check_notification_need(self):
        events = self.db_conn.load_events_for_mailing()
        if events:
            self.send_mails(events)
            
    def send_mails(self, events):
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(MAIL_USER, MAIL_PWD)
        for event in events:
            if self.send_mail(smtp, event):
                event['notified'] = True

        for event in events:
            if event.get('notified'):
                try:
                    self.db_conn.edit_event(event['cardId'], {'notified': True})
                except Exception as e:
                    logging.exception(e)

        smtp.quit()

    @staticmethod
    def send_mail(smtp, event):
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

        logging.warning(f'Message {event["title"]} is sent to {event["email"]}. Card id: {event["cardId"]}')
        return True
